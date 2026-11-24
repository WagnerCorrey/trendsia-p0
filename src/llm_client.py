import requests
from src.config import ConfiguracaoApp


class ErroComunicacaoLLM(Exception):
    """Erro amigável para falhas de rede, autenticação ou indisponibilidade da API."""


def chamar_modelo(config: ConfiguracaoApp, payload: dict) -> dict:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.modelo}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": config.api_key,
    }

    try:
        resposta = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=config.timeout,
        )
    except requests.exceptions.Timeout:
        raise ErroComunicacaoLLM(
            f"Tempo limite esgotado ({config.timeout}s): o serviço do Gemini demorou a responder. Tente novamente."
        )
    except requests.exceptions.ConnectionError:
        raise ErroComunicacaoLLM(
            "Falha de comunicação: não foi possível conectar à API do Gemini. Verifique sua conexão com a internet."
        )
    except requests.exceptions.RequestException:
        raise ErroComunicacaoLLM(
            "Erro inesperado na requisição ao serviço de linguagem. Verifique sua rede e tente novamente."
        )

    if resposta.status_code in (400, 401, 403):
        raise ErroComunicacaoLLM(
            "Credencial inválida ou sem permissão: verifique se sua GEMINI_API_KEY no arquivo .env está correta e ativa."
        )
    if resposta.status_code == 429:
        raise ErroComunicacaoLLM(
            "Limite de requisições atingido: aguarde alguns instantes antes de enviar uma nova solicitação."
        )
    if resposta.status_code >= 500:
        raise ErroComunicacaoLLM(
            f"Serviço indisponível no momento (erro {resposta.status_code}). Tente novamente mais tarde."
        )
    if not resposta.ok:
        raise ErroComunicacaoLLM(
            f"Falha ao processar a solicitação junto ao provedor (status HTTP {resposta.status_code})."
        )

    try:
        return resposta.json()
    except ValueError:
        raise ErroComunicacaoLLM(
            "Resposta inválida: o servidor retornou um conteúdo que não está no formato JSON esperado."
        )