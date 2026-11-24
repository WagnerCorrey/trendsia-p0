from unittest.mock import MagicMock, patch
import pytest  # type: ignore[import-not-found]
import requests  # type: ignore[import-not-found]

from src.config import ConfiguracaoApp, ErroConfiguracao, carregar_configuracao
from src.llm_client import ErroComunicacaoLLM, chamar_modelo
from src.prompt_builder import preparar_solicitacao, validar_entrada
from src.response_parser import ErroRespostaLLM, tratar_resposta


def test_entrada_vazia_deve_ser_impedida():
    with pytest.raises(ValueError, match="Entrada vazia"):
        validar_entrada("   \n\t  ")


def test_credencial_ausente(monkeypatch):
    monkeypatch.setattr("src.config.load_dotenv", lambda: None)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ErroConfiguracao, match="Credencial ausente"):
        carregar_configuracao()


def test_credencial_invalida_http_401():
    config = ConfiguracaoApp(api_key="chave_falsa_teste", modelo="gemini-4-hydrogen", timeout=10)
    payload = preparar_solicitacao("Descarte irregular de entulho na margem do rio.")

    resposta_mock = MagicMock()
    resposta_mock.status_code = 401
    resposta_mock.ok = False

    with patch("src.llm_client.requests.post", return_value=resposta_mock):
        with pytest.raises(ErroComunicacaoLLM, match="Credencial inválida"):
            chamar_modelo(config, payload)


def test_timeout_na_chamada():
    config = ConfiguracaoApp(api_key="chave_teste", modelo="gemini-4-hydrogen", timeout=5)
    payload = preparar_solicitacao("Queimada próxima à área de preservação.")

    with patch("src.llm_client.requests.post", side_effect=requests.exceptions.Timeout):
        with pytest.raises(ErroComunicacaoLLM, match="Tempo limite esgotado"):
            chamar_modelo(config, payload)


def test_falha_de_comunicacao():
    config = ConfiguracaoApp(api_key="chave_teste", modelo="gemini-4-hydrogen", timeout=5)
    payload = preparar_solicitacao("Vazamento de óleo em córrego urbano.")

    with patch("src.llm_client.requests.post", side_effect=requests.exceptions.ConnectionError):
        with pytest.raises(ErroComunicacaoLLM, match="Falha de comunicação"):
            chamar_modelo(config, payload)


def test_indisponibilidade_servidor_503():
    config = ConfiguracaoApp(api_key="chave_teste", modelo="gemini-4-hydrogen" \
    "", timeout=5)
    payload = preparar_solicitacao("Desmatamento recente próximo à estrada vicinal.")

    resposta_mock = MagicMock()
    resposta_mock.status_code = 503
    resposta_mock.ok = False

    with patch("src.llm_client.requests.post", return_value=resposta_mock):
        with pytest.raises(ErroComunicacaoLLM, match="Serviço indisponível"):
            chamar_modelo(config, payload)


def test_resposta_vazia_ou_inesperada():
    with pytest.raises(ErroRespostaLLM, match="Resposta vazia"):
        tratar_resposta({"candidates": []})

    with pytest.raises(ErroRespostaLLM, match="Formato inesperado"):
        tratar_resposta({"candidates": [{"content": {}}]})


def test_fluxo_sucesso_simulado():
    config = ConfiguracaoApp(api_key="chave_teste", modelo="gemini-4-hydrogen", timeout=10)
    relato = validar_entrada("Acúmulo de lixo bloqueando bueiro na Rua das Flores.")
    payload = preparar_solicitacao(relato)

    resposta_mock = MagicMock()
    resposta_mock.status_code = 200
    resposta_mock.ok = True
    resposta_mock.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": (
                                "--- Ficha Preliminar (sujeita à revisão humana) ---\n"
                                "Tema: Obstrução de drenagem por resíduos sólidos\n"
                                "Local/Referência: Rua das Flores\n"
                                "Urgência: Média"
                            )
                        }
                    ]
                }
            }
        ]
    }

    with patch("src.llm_client.requests.post", return_value=resposta_mock):
        dados = chamar_modelo(config, payload)
        resultado = tratar_resposta(dados)

    assert "Tema: Obstrução de drenagem" in resultado
    assert "Urgência: Média" in resultado