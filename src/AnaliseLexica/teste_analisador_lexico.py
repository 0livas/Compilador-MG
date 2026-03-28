import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from analisador_lexico import AnalisadorLexico
from mineires_token import Token

def exibir_tokens(tokens: list, titulo: str = "") -> None:
    if titulo:
        print(f"\n{'='*70}")
        print(f"  {titulo}")
        print(f"{'='*70}\n")

    print(f"{'Linha':<6} {'Col':<5} {'Lexema':<20} {'Tipo de Token':<25}")
    print("-" * 70)

    for token in tokens:
        if token.token.name == "EOF":
            continue

        lexema_display = (
            repr(token.lexema) if token.token.name.startswith("LITERAL") else token.lexema
        )
        print(
            f"{token.linha:<6} {token.coluna:<5} {lexema_display:<20} {token.token.name:<25}"
        )

    print()

def teste_codigo_valido() -> None:
    analisador = AnalisadorLexico()

    codigo_simples = """bora_cumpade
simbora
    trem_di_numeru i = 0;
    trem_cum_virgula x = 3.14;
    talavez "Hello Minerês!";
cabou"""

    tokens, erros = analisador.analisar_codigo(codigo_simples)

    exibir_tokens(tokens, "TESTE 1: Código Válido Simples")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Nenhum erro encontrado!")

def teste_numeros() -> None:
    analisador = AnalisadorLexico()

    codigo_numeros = """trem_di_numeru dec = 42;
trem_di_numeru hex = 0xFF;
trem_di_numeru oct = 0o77;
trem_di_numeru bin = 0b1010;
trem_cum_virgula float1 = 3.14;
trem_cum_virgula float2 = 1.5e-3;
trem_cum_virgula float3 = 2.0E+10;"""

    tokens, erros = analisador.analisar_codigo(codigo_numeros)

    exibir_tokens(tokens, "TESTE 2: Diferentes Tipos de Números")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Todos os números foram reconhecidos corretamente!")

def teste_strings_e_chars() -> None:
    analisador = AnalisadorLexico()

    codigo_strings = """trem_discrita msg1 = "Ola Minerês!";
trem_discrita msg2 = "String com escapes: \\n \\t \\\\ \\"aspas\\"";
trem_discrita msg3 = "";
"""

    tokens, erros = analisador.analisar_codigo(codigo_strings)

    exibir_tokens(tokens, "TESTE 3: Strings e Caracteres")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Strings processadas corretamente!")

def teste_operadores() -> None:
    """Testa operadores e símbolos."""
    analisador = AnalisadorLexico()

    codigo_ops = """a = b + c;
d = e - f * g / h;
uai_se (x <= 10 && y >= 5) simbora
    z = a != b || c == d;
cabou
resultado = a % 2;
divisao_inteira = 10 // 3;"""

    tokens, erros = analisador.analisar_codigo(codigo_ops)

    exibir_tokens(tokens, "TESTE 4: Operadores e Símbolos")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Operadores reconhecidos corretamente!")

def teste_palavras_chave() -> None:
    analisador = AnalisadorLexico()

    codigo_palavras = """bora_cumpade
simbora
    trem_di_numeru x = 0;
    uai_se (x > 0) simbora
        ta_bao x;
    cabou
    enquanto_tiver_trem (eh) simbora
        toca_o_trem;
    cabou
cabou"""

    tokens, erros = analisador.analisar_codigo(codigo_palavras)

    exibir_tokens(tokens, "TESTE 5: Palavras-Chave Minerês")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Todas as palavras-chave foram reconhecidas!")

def teste_erros() -> None:
    """Testa detecção de erros."""
    analisador = AnalisadorLexico()

    codigo_com_erros = """trem_di_numeru num1 = 0xGG;
trem_discrita str = "String aberta
trem_di_numeru num2 = 0o99;
trem_di_numeru @ = 5;"""

    tokens, erros = analisador.analisar_codigo(codigo_com_erros)

    exibir_tokens(tokens, "TESTE 6: Detecção de Erros")

    print(erros.gerar_relatorio())

def teste_arquivo() -> None:
    analisador = AnalisadorLexico()

    arquivo = (
        Path(__file__).parent.parent.parent / "Mineirês" / "exemplo1.mng"
    )

    if arquivo.exists():
        print(f"\n{'='*70}")
        print(f"  TESTE 7: Análise de Arquivo ({arquivo.name})")
        print(f"{'='*70}\n")

        print(f"Conteúdo do arquivo:\n{'-'*70}")
        with open(arquivo) as f:
            print(f.read())
        print(f"{'-'*70}\n")

        tokens, erros = analisador.analisar_arquivo(str(arquivo))

        exibir_tokens(tokens, "Tokens Gerados")

        if erros.tem_erros():
            print(erros.gerar_relatorio())
        else:
            print("✓ Arquivo analisado com sucesso!")

    else:
        print(f"\n⚠️ Arquivo {arquivo} não encontrado")

def teste_comentario_linha() -> None:
    analisador = AnalisadorLexico()

    codigo = """bora_cumpade
simbora
    // Este é um comentário de uma linha
    trem_di_numeru x = 10;  // Comentário inline
    
    // Outro comentário
    // E mais outro
    talavez "olá";
    
cabou
"""

    tokens, erros = analisador.analisar_codigo(codigo)

    exibir_tokens(tokens, "TESTE 8: Comentários de Uma Linha (//)")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Nenhum erro encontrado!")

def teste_comentario_bloco() -> None:
    analisador = AnalisadorLexico()

    codigo = """bora_cumpade
simbora
    causo
        Este é um comentário
        que ocupa múltiplas linhas
        e deve ser ignorado completamente
    fim_do_causo
    
    trem_di_numeru y = 42;
    
    causo
        Outro comentário de bloco
        com várias linhas
    fim_do_causo
    
    talavez "programa continua";
    
cabou
"""

    tokens, erros = analisador.analisar_codigo(codigo)

    exibir_tokens(tokens, "TESTE 9: Comentários Multilinha (causo ... fim_do_causo)")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Nenhum erro encontrado!")

def teste_comentarios_aninhados() -> None:
    analisador = AnalisadorLexico()

    codigo = """bora_cumpade
simbora
    // Comentário de linha
    
    causo
        Comentário de bloco
        // Comentário de linha dentro do bloco (ainda comentário)
        mais conteúdo
    fim_do_causo
    
    // Mais um comentário de linha
    trem_di_numeru z = 0xFF;
    
cabou
"""

    tokens, erros = analisador.analisar_codigo(codigo)

    exibir_tokens(tokens, "TESTE 10: Combinação de Comentários")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Nenhum erro encontrado!")

def teste_comentario_nao_fechado() -> None:
    analisador = AnalisadorLexico()

    codigo = """bora_cumpade
simbora
    trem_di_numeru x = 10;
    
    causo
        Comentário sem ser fechado
        vai até aqui
cabou
"""

    tokens, erros = analisador.analisar_codigo(codigo)

    exibir_tokens(tokens, "TESTE 11: Erro - Comentário Multilinha Não Fechado")

    if erros.tem_erros():
        print("❌ Erros Encontrados:")
        print(erros.gerar_relatorio())
    else:
        print("⚠️ Nenhum erro registrado (esperava erro)")

def teste_codigo_real_com_comentarios() -> None:
    analisador = AnalisadorLexico()

    codigo = """causo
    Programa: Contador de 0 até 10
    Autor: João Paulo
    Data: 2026-03-27
fim_do_causo

bora_cumpade
simbora
    // Inicializar contador
    trem_di_numeru contador = 0;
    
    causo
        Loop para imprimir números
        de 0 até 10
    fim_do_causo
    
    enquanto_tiver_trem (contador <= 10) simbora
        talavez contador;  // Exibir valor
        contador = contador + 1;  // Incrementar
    cabou
    
    // Fim do programa
    ta_bao 0;
cabou
"""

    tokens, erros = analisador.analisar_codigo(codigo)

    exibir_tokens(tokens, "TESTE 12: Código Realista com Comentários")

    print(f"Total de tokens gerados: {len([t for t in tokens if t.token.name != 'EOF'])}\n")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Nenhum erro encontrado!")

def main() -> None:
    """Executa todos os testes."""
    print("\n" + "="*70)
    print("TESTES DO ANALISADOR LÉXICO - LINGUAGEM MINERÊS")
    print("="*70)

    try:
        teste_codigo_valido()
        teste_numeros()
        teste_strings_e_chars()
        teste_operadores()
        teste_palavras_chave()
        teste_erros()
        teste_arquivo()
        teste_comentario_linha()
        teste_comentario_bloco()
        teste_comentarios_aninhados()
        teste_comentario_nao_fechado()
        teste_codigo_real_com_comentarios()

        print("\n" + "="*70)
        print("✓ TODOS OS TESTES COMPLETADOS")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ ERRO DURANTE TESTES: {e}")
        import traceback

        traceback.print_exc()

if __name__ == "__main__":
    main()
