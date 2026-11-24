class ErroRespostaLLM(Exception):
    """Erro amigável quando a resposta do modelo vem vazia ou malformada."""


def tratar_resposta(dados_resposta: dict) -> str:
    try:
        candidatos = dados_resposta.get("candidates", [])
        if not candidatos:
            raise ErroRespostaLLM(
                "Resposta vazia: o modelo não retornou nenhuma ficha para o relato enviado."
            )

        partes = candidatos[0].get("content", {}).get("parts", [])
        if not partes or "text" not in partes[0]:
            raise ErroRespostaLLM(
                "Formato inesperado: a resposta do modelo não contém o texto esperado."
            )

        texto_final = partes[0]["text"].strip()
        if not texto_final:
            raise ErroRespostaLLM(
                "Resposta vazia: o texto gerado pelo modelo veio em branco."
            )

        return texto_final
    except (AttributeError, IndexError, TypeError):
        raise ErroRespostaLLM(
            "Formato inesperado: não foi possível interpretar a estrutura retornada pelo modelo."
        )