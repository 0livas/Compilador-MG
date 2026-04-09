import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from AnaliseLexica.analisador_lexico import AnalisadorLexico
from AnaliseSintatica.analisador_sintatico import AnalisadorSintatico, ExcecaoSintatica


def main(): 
    caminho = str(
        Path(__file__).resolve().parent.parent.parent / "Mineirês" / "exemplo1.uai"
    )

    lexico = AnalisadorLexico()
    tokens, erros_lexicos = lexico.analisar_arquivo(caminho)

    if erros_lexicos.tem_erros():
        print("ERROS LÉXICOS ENCONTRADOS:")
        print(erros_lexicos.gerar_relatorio())
        return

    print("ANÁLISE LÉXICA CONCLUÍDA COM SUCESSO!")
    print(f"Total de tokens gerados: {len(tokens)}")

    sintatico = AnalisadorSintatico(tokens)

    try:
        sintatico.analisar()
        print("✓ Sintaxe válida")
    except ExcecaoSintatica as e:
        print("ERRO SINTÁTICO ENCONTRADO:")
        print(e)


if __name__ == "__main__":
    main()