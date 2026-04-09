"""Suite de testes para o Analisador Léxico Minerês.

Testa todos os componentes:
- Código válido
- Números em 6 formatos
- Strings e caracteres
- Operadores e comparadores
- Palavras-chave
- Tratamento de erros
- Análise de arquivos
- Comentários
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from AnaliseLexica.analisador_lexico import AnalisadorLexico
from AnaliseLexica.mineires_token import Token
from AnaliseLexica.tokenType import TokenType

def exibir_tokens(tokens: list, titulo: str = "") -> None:
    """Exibe tokens em formato tabular."""
    if titulo:
        print(f"\n{'='*70}")
        print(f"  {titulo}")
        print(f"{'='*70}\n")

    print(f"{'Linha':<6} {'Col':<5} {'Lexema':<20} {'Tipo de Token':<25}")
    print("-" * 70)

    for token in tokens:
        if token.token == TokenType.EOF:
            continue

        lexema_display = (
            repr(token.lexema) if token.token.name.startswith("LITERAL") else token.lexema
        )
        tipo_display = f"{token.token.value} {token.token.name}"
        print(
            f"{token.linha:<6} {token.coluna:<5} {lexema_display:<20} {tipo_display:<25}"
        )

    print()

def teste_codigo_valido() -> None:
    analisador = AnalisadorLexico()

    codigo_simples = """bora_cumpade main()
simbora
    trem_di_numeru i fica_assim_entao 0 uai
    trem_cum_virgula x fica_assim_entao 3.14 uai
    oia_proce_ve "Hello Minerês!" uai
cabo"""

    tokens, erros = analisador.analisar_codigo(codigo_simples)

    exibir_tokens(tokens, "TESTE 1: Código Válido Simples")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Nenhum erro encontrado!")

def teste_numeros() -> None:
    analisador = AnalisadorLexico()

    codigo_numeros = """trem_di_numeru dec fica_assim_entao 42 uai
trem_di_numeru hex fica_assim_entao 0xFF uai
trem_di_numeru oct1 fica_assim_entao 07 uai
trem_di_numeru oct2 fica_assim_entao 017 uai
trem_cum_virgula float1 fica_assim_entao 3.14 uai
trem_cum_virgula float2 fica_assim_entao .92 uai
trem_cum_virgula float3 fica_assim_entao 0.33 uai"""

    tokens, erros = analisador.analisar_codigo(codigo_numeros)

    exibir_tokens(tokens, "TESTE 2: Diferentes Tipos de Números")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Todos os números foram reconhecidos corretamente!")

def teste_strings_e_chars() -> None:
    analisador = AnalisadorLexico()

    codigo_strings = """trem_discrita msg1 fica_assim_entao "Ola Minerês!" uai
trem_discrita msg2 fica_assim_entao "String com escapes: \\n \\t \\\\ \\"aspas\\"" uai
trem_discrita msg3 fica_assim_entao "" uai
trosso letra fica_assim_entao 'a' uai
trosso quebra fica_assim_entao '\\n' uai
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

    codigo_ops = """x fica_assim_entao a + b uai
y fica_assim_entao c - d uai
resto fica_assim_entao valor % 2 uai

uai_se (x <= 10 tamem y >= 5) simbora
    z fica_assim_entao a neh_nada b quarque_um c mema_coisa d uai
cabo"""

    tokens, erros = analisador.analisar_codigo(codigo_ops)

    exibir_tokens(tokens, "TESTE 4: Operadores e Símbolos")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Operadores reconhecidos corretamente!")

def teste_palavras_chave() -> None:
    analisador = AnalisadorLexico()

    codigo_palavras = """bora_cumpade main()
simbora
    trem_di_numeru x fica_assim_entao 0 uai
    uai_se (x > 0) simbora
        ta_bao x uai
    cabo
    enquanto_tiver_trem (eh) simbora
        toca_o_trem uai
    cabo
cabo"""

    tokens, erros = analisador.analisar_codigo(codigo_palavras)

    exibir_tokens(tokens, "TESTE 5: Palavras-Chave Minerês")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Todas as palavras-chave foram reconhecidas!")

def teste_erros() -> None:
    """Testa detecção de erros."""
    analisador = AnalisadorLexico()

    codigo_com_erros = """trem_di_numeru num1 fica_assim_entao 0xGG uai
trem_discrita str fica_assim_entao "String aberta
trem_di_numeru num2 fica_assim_entao 09 uai
trem_di_numeru @ fica_assim_entao 5 uai"""

    tokens, erros = analisador.analisar_codigo(codigo_com_erros)

    exibir_tokens(tokens, "TESTE 6: Detecção de Erros")

    print(erros.gerar_relatorio())

def teste_arquivo() -> None:
    analisador = AnalisadorLexico()

    arquivo = (
        Path(__file__).parent.parent.parent / "Mineirês" / "exemplo1.uai"
    )

    if arquivo.exists():
        print(f"\n{'='*70}")
        print(f"  TESTE 7: Análise de Arquivo ({arquivo.name})")
        print(f"{'='*70}\n")

        print(f"Conteúdo do arquivo:\n{'-'*70}")
        with open(arquivo, encoding="utf-8") as f:
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

    codigo = """bora_cumpade main()
simbora
    // Este é um comentário de uma linha
    trem_di_numeru x fica_assim_entao 10 uai  // Comentário inline
    
    // Outro comentário
    // E mais outro
    oia_proce_ve "olá" uai
    
cabo
"""

    tokens, erros = analisador.analisar_codigo(codigo)

    exibir_tokens(tokens, "TESTE 8: Comentários de Uma Linha (//)")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Nenhum erro encontrado!")

def teste_comentario_bloco() -> None:
    analisador = AnalisadorLexico()

    codigo = """bora_cumpade main()
simbora
    causo
        Este é um comentário
        que ocupa múltiplas linhas
        e deve ser ignorado completamente
    fim_do_causo
    
    trem_di_numeru y fica_assim_entao 42 uai
    
    causo
        Outro comentário de bloco
        com várias linhas
    fim_do_causo
    
    oia_proce_ve "programa continua" uai
    
cabo
"""

    tokens, erros = analisador.analisar_codigo(codigo)

    exibir_tokens(tokens, "TESTE 9: Comentários Multilinha (causo ... fim_do_causo)")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Nenhum erro encontrado!")

def teste_comentarios_aninhados() -> None:
    analisador = AnalisadorLexico()

    codigo = """bora_cumpade main()
simbora
    // Comentário de linha
    
    causo
        Comentário de bloco
        // Comentário de linha dentro do bloco (ainda comentário)
        mais conteúdo
    fim_do_causo
    
    // Mais um comentário de linha
    trem_di_numeru z fica_assim_entao 0xFF uai
    
cabo
"""

    tokens, erros = analisador.analisar_codigo(codigo)

    exibir_tokens(tokens, "TESTE 10: Combinação de Comentários")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Nenhum erro encontrado!")

def teste_comentario_nao_fechado() -> None:
    analisador = AnalisadorLexico()

    codigo = """bora_cumpade main()
simbora
    trem_di_numeru x fica_assim_entao 10 uai
    
    causo
        Comentário sem ser fechado
        vai até aqui
cabo
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

bora_cumpade main()
simbora
    // Inicializar contador
    trem_di_numeru contador fica_assim_entao 0 uai
    
    causo
        Loop para imprimir números
        de 0 até 10
    fim_do_causo
    
    enquanto_tiver_trem (contador <= 10) simbora
        oia_proce_ve contador uai  // Exibir valor
        contador fica_assim_entao contador + 1 uai  // Incrementar
    cabo
    
    // Fim do programa
    ta_bao 0 uai
cabo
"""

    tokens, erros = analisador.analisar_codigo(codigo)

    exibir_tokens(tokens, "TESTE 12: Código Realista com Comentários")

    print(f"Total de tokens gerados: {len([t for t in tokens if t.token != TokenType.EOF])}\n")

    if erros.tem_erros():
        print(erros.gerar_relatorio())
    else:
        print("✓ Nenhum erro encontrado!")

def main() -> None:
    """Executa a suite de testes."""
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