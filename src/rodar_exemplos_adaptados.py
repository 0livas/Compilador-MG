import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from AnaliseLexica.analisador_lexico import AnalisadorLexico
from AnaliseSintatica.analisador_sintatico import AnalisadorSintatico, ExcecaoSintatica
from AnaliseSintatica.gerador_quadruplas import GeradorQuadruplas
from AnaliseSemantica.analisador_semantico import SemanticError

ROOT = Path(__file__).resolve().parent.parent
EXEMPLOS_DIR = ROOT / "Mineirês" / "exemplos_adaptados"

DEVEM_COMPILAR = {
    "01_teste_completo.uai",
    "02_loop_while.uai",
    "03_loop_for.uai",
    "04_switch_case.uai",
    "05_fibonacci.uai",
    "08_concatenar.uai",
    "10_xove_read.uai",
    "11_eq_str.uai",
    "12_conversao_numeral.uai",
    "17_or_op.uai",
}

DEVEM_FALHAR = {
    "06_codigo_errado.uai",
    "07_erro_atrib.uai",
    "09_invalido_char_op.uai",
    "13_dif_types.uai",
    "14_div_zero.uai",
    "15_redeclaracao.uai",
    "16_declaracao_previa.uai",
    "18_str_op_error.uai",
    "19_condicao_nao_booleana_if.uai",
    "20_caso_duplicado_switch.uai",
}


def compilar_arquivo(caminho: Path) -> tuple[bool, str]:
    lexico = AnalisadorLexico()
    tokens, erros_lexicos = lexico.analisar_arquivo(str(caminho))

    if erros_lexicos.tem_erros():
        return False, f"erro léxico: {erros_lexicos.quantidade_erros()} ocorrência(s)"

    sintatico = AnalisadorSintatico(tokens)

    try:
        programa = sintatico.analisar()
        gerador = GeradorQuadruplas()
        gerador.gerar(programa)
        return True, "compilou com sucesso"
    except ExcecaoSintatica as e:
        return False, f"erro sintático: {e}"
    except SemanticError as e:
        return False, f"erro semântico: {e}"
    except Exception as e:  # proteção para bugs do compilador
        return False, f"erro interno: {type(e).__name__}: {e}"



def esperado_para(nome: str) -> str:
    if nome in DEVEM_COMPILAR:
        return "compilar"
    if nome in DEVEM_FALHAR:
        return "falhar"
    return "desconhecido"



def rodar_suite() -> int:
    arquivos = sorted(EXEMPLOS_DIR.glob("*.uai"))

    if not arquivos:
        print("Nenhum exemplo encontrado em:")
        print(EXEMPLOS_DIR)
        return 2

    total = 0
    aprovados = 0

    print("=" * 72)
    print("SUITE DOS EXEMPLOS ADAPTADOS")
    print("=" * 72)
    print(f"Pasta: {EXEMPLOS_DIR}")
    print()

    for caminho in arquivos:
        total += 1
        nome = caminho.name
        esperado = esperado_para(nome)
        ok, detalhe = compilar_arquivo(caminho)

        if esperado == "compilar":
            passou = ok
            status = "PASSOU" if passou else "FALHOU"
            resultado = "compilou" if ok else "não compilou"
        elif esperado == "falhar":
            passou = not ok
            status = "PASSOU" if passou else "FALHOU"
            resultado = "falhou como esperado" if not ok else "compilou, mas deveria falhar"
        else:
            passou = ok
            status = "SEM EXPECTATIVA"
            resultado = detalhe

        if passou:
            aprovados += 1

        print(f"[{status}] {nome}")
        print(f"  esperado: {esperado}")
        print(f"  resultado: {resultado}")
        print(f"  detalhe: {detalhe}")
        print()

    print("-" * 72)
    print(f"Resumo: {aprovados}/{total} casos dentro do esperado")

    if aprovados == total:
        print("Suite concluída sem divergências.")
        return 0

    print("Há divergências entre o comportamento atual e o esperado.")
    return 1


if __name__ == "__main__":
    raise SystemExit(rodar_suite())
