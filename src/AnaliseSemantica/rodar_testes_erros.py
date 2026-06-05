import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from AnaliseLexica.analisador_lexico import AnalisadorLexico
from AnaliseSintatica.analisador_sintatico import AnalisadorSintatico, ExcecaoSintatica
from AnaliseSintatica.gerador_quadruplas import GeradorQuadruplas
from AnaliseSemantica.analisador_semantico import SemanticError, AnalisadorSemantico

def main():
    arquivo_teste = Path(__file__).resolve().parent / "testes_erros_semanticos.uai"
    
    with open(arquivo_teste, "r", encoding="utf-8") as f:
        codigo = f.read()

    lexico = AnalisadorLexico()
    tokens, erros_lexicos = lexico.analisar_codigo(codigo)
    
    if erros_lexicos.tem_erros():
        print("Erros léxicos encontrados (Inesperado)!")
        print(erros_lexicos.gerar_relatorio())
        return

    sintatico = AnalisadorSintatico(tokens)
    try:
        programa = sintatico.analisar()
    except ExcecaoSintatica as e:
        print(f"Erro sintático (Inesperado): {e}")
        return

    print(f"Arquivo lido com sucesso. Iniciando verificação de {len(programa.functions)} funções de teste de erro semântico...\n")

    todos_sucesso = True

    for funcao in programa.functions:
        print(f"--- Testando função: {funcao.name} ---")
        gerador = GeradorQuadruplas()
        gerador.semantico = AnalisadorSemantico()
        try:
            gerador._gerar_funcao(funcao)
            print("❌ FALHA: A função não estourou nenhum erro semântico!")
            todos_sucesso = False
        except SemanticError as e:
            print(f"✅ SUCESSO: Erro semântico corretamente identificado e localizado:")
            print(f"   -> {e}")
            if "linha 0" in str(e) or "coluna 0" in str(e):
                 print("   ⚠️ AVISO: A linha ou coluna reportada está como 0, verifique o tracking no parser!")
                 todos_sucesso = False
        except Exception as e:
            print(f"❌ ERRO INESPERADO: Ocorreu uma exceção que não é um erro semântico: {e}")
            todos_sucesso = False
        print()

    if todos_sucesso:
        print("TODOS OS TESTES DE ERRO SEMÂNTICO PASSARAM CORRETAMENTE.")
    else:
        print("ALGUNS TESTES FALHARAM OU NÃO REPORTARAM A LINHA CORRETA.")

if __name__ == "__main__":
    main()
