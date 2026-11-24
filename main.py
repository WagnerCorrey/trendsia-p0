import os
import requests
from dotenv import load_dotenv

load_dotenv()


def analisar_ocorrencia(relato: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    modelo = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

    if not api_key:
        raise ValueError(
            "Credencial GEMINI_API_KEY não encontrada. Configure a variável de ambiente antes de executar."
        )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    prompt = (
        "Você apoia a triagem preliminar e supervisionada de relatos socioambientais. "
        "Analise o relato informal a seguir e responda APENAS nestas três linhas, "
        "sem inventar informações ausentes:\n"
        "Tema: <tema ambiental ou socioambiental identificado>\n"
        "Local/Referência: <local ou referência citada no texto ou 'Não informado'>\n"
        "Urgência: <Baixa | Média | Alta | Não evidente>\n\n"
        f"Relato: {relato}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 800},
    }

    resposta = requests.post(url, headers=headers, json=payload, timeout=15)
    resposta.raise_for_status()

    dados = resposta.json()
    candidatos = dados.get("candidates", [])
    if not candidatos:
        return "Não foi possível obter uma resposta textual do modelo."

    partes = candidatos[0].get("content", {}).get("parts", [])
    texto = "".join(parte.get("text", "") for parte in partes).strip()
    return texto if texto else "A resposta retornou vazia."


def main() -> None:
    print("=== Triagem Preliminar de Ocorrências Socioambientais (Nível Básico) ===")
    relato = input("Digite um relato curto e fictício de ocorrência: ").strip()

    if not relato:
        print("Nenhuma entrada informada. Digite um relato textual para continuar.")
        return

    try:
        ficha = analisar_ocorrencia(relato)
        print("\n--- Ficha Preliminar (sujeita à revisão humana) ---")
        print(ficha)
    except ValueError as erro:
        print(f"Erro de configuração: {erro}")
    except requests.RequestException as erro:
        print(f"Falha na comunicação com o serviço de LLM: {erro}")


if __name__ == "__main__":
    main()