import sys
from src.config import ErroConfiguracao, carregar_configuracao
from src.llm_client import ErroComunicacaoLLM, chamar_modelo
from src.prompt_builder import preparar_solicitacao, validar_entrada
from src.response_parser import ErroRespostaLLM, tratar_resposta


def capturar_entrada() -> str:
    print("=== Triagem Preliminar de Ocorrências Socioambientais ===")
    return input("Descreva o relato da ocorrência: ")


def apresentar_resultado(ficha: str) -> None:
    print("\n" + ficha + "\n")


def executar() -> int:
    try:
        config = carregar_configuracao()
        entrada_bruta = capturar_entrada()
        relato_valido = validar_entrada(entrada_bruta)
        payload = preparar_solicitacao(relato_valido)
        resposta_bruta = chamar_modelo(config, payload)
        ficha_formatada = tratar_resposta(resposta_bruta)
        apresentar_resultado(ficha_formatada)
        return 0
    except (ValueError, ErroConfiguracao, ErroComunicacaoLLM, ErroRespostaLLM) as erro:
        print(f"\n[Aviso] {erro}\n", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n[Aviso] Execução interrompida pelo usuário.\n", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(executar())