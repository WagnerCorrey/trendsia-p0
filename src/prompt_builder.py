def validar_entrada(relato: str) -> str:
    texto_limpo = relato.strip()
    if not texto_limpo:
        raise ValueError(
            "Entrada vazia: por favor, digite o relato da ocorrência socioambiental antes de enviar."
        )
    return texto_limpo


def preparar_solicitacao(relato: str) -> dict:
    instrucao = (
        "Você é um assistente de triagem de ocorrências socioambientais. "
        "Analise o relato fornecido e responda estritamente no formato abaixo, sem texto adicional:\n"
        "--- Ficha Preliminar (sujeita à revisão humana) ---\n"
        "Tema: <categoria objetiva do problema>\n"
        "Local/Referência: <local citado ou 'Não informado'>\n"
        "Urgência: <Baixa, Média ou Alta>\n\n"
        f"Relato: {relato}"
    )
    return {
        "contents": [
            {
                "parts": [{"text": instrucao}]
            }
        ]
    }