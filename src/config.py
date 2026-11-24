import os
from dataclasses import dataclass


def load_dotenv() -> None:
    """Carrega pares CHAVE=VALOR simples do arquivo .env sem depender de pacotes externos."""
    caminho = os.path.join(os.getcwd(), ".env")
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if not linha or linha.startswith("#") or "=" not in linha:
                    continue

                chave, valor = linha.split("=", 1)
                chave = chave.strip()
                valor = valor.strip()
                if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in ('"', "'"):
                    valor = valor[1:-1]

                if chave and chave not in os.environ:
                    os.environ[chave] = valor
    except FileNotFoundError:
        pass


class ErroConfiguracao(Exception):
    """Erro amigável para problemas de configuração ou credenciais."""


@dataclass(frozen=True)
class ConfiguracaoApp:
    api_key: str
    modelo: str
    timeout: int


def carregar_configuracao() -> ConfiguracaoApp:
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "cole_sua_chave_do_google_ai_studio_aqui":
        raise ErroConfiguracao(
            "Credencial ausente: configure a variável GEMINI_API_KEY no arquivo .env antes de executar."
        )

    modelo = os.getenv("GEMINI_MODEL", "gemini-4-hydrogen").strip()
    if not modelo:
        raise ErroConfiguracao(
            "Configuração inválida: a variável GEMINI_MODEL não pode estar vazia."
        )

    timeout_str = os.getenv("LLM_TIMEOUT", "15").strip()
    try:
        timeout = int(timeout_str)
        if timeout <= 0:
            raise ValueError
    except ValueError:
        raise ErroConfiguracao(
            "Configuração inválida: LLM_TIMEOUT deve ser um número inteiro positivo."
        )

    return ConfiguracaoApp(api_key=api_key, modelo=modelo, timeout=timeout)