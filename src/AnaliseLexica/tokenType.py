from enum import Enum, auto

class TokenType(Enum):
    # Main
    MAIN = auto()

    # Condicionais
    IF = auto()
    ELSE = auto()

    # Switch e Case
    SWITCH = auto()
    CASE = auto()

    # Loops
    FOR = auto()
    WHILE = auto()

    # Fluxo/Funções
    RETURN = auto()
    BREAK = auto()
    CONTINUE = auto()

    # Variáveis
    TYPE_INT = auto()
    TYPE_FLOAT = auto()
    TYPE_STRING = auto()
    TYPE_CHAR = auto()

    TYPE_BOOLEAN = auto()
    TRUE = auto()
    FALSE = auto()

    # Inicio / Fim de Bloco de Código
    BEGIN_BLOCK = auto()
    END_BLOCK = auto()

    # Delimitadores
    SEMICOLON = auto()
    COMMA = auto()
    QUOTE = auto()
    SINGLE_QUOTE = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()

    # Operadores Relacionais
    LESS = auto()
    GREATER = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    ASSIGN = auto()
    NOT_EQUAL = auto()
    EQUAL = auto()

    # Operadores Logicos
    OR = auto()
    NOT = auto()
    AND = auto()
    XOR = auto()

    # Operadores Aritméticos
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MOD = auto()
    WHOLE_DIVISION = auto()

    #Entrada e Saída
    INPUT = auto()
    OUTPUT = auto()

    # Bases Numéricas
    LITERAL_INT = auto()
    LITERAL_FLOAT = auto()
    LITERAL_STRING = auto()
    LITERAL_CHAR = auto()

    # Identificador
    IDENTIFIER = auto()

    # Fim do Código
    EOF = auto()

    PALAVRAS_CHAVE = {
        #Fluxo e Funções
        "bora_cumpade" : TokenType.MAIN,
        "ta_bao" : TokenType.RETURN,
        "para_o_trem" : TokenType.BREAK,
        "toca_o_trem" : TokenType.CONTINUE,

        #Estruturas de Controle
        "uai_se" : TokenType.IF,
        "uai_senao" : TokenType.ELSE,
        "enquanto_tiver_trem" : TokenType.WHILE,
        "dependenu" : TokenType.SWITCH,
        "du_casu" : TokenType.CASE,
         
        #Variáveis de Dados
        "trem_di_numeru" : TokenType.TYPE_INT,
        "Trem_cum_virgula" : TokenType.TYPE_CHAR,
        "trem_discrita": TokenType.TYPE_STRING,
        "trem_discolhe" : TokenType.TYPE_BOOLEAN,
        "eh" : TokenType.TRUE,
        "num_eh" : TokenType.FALSE,
        "char" : TokenType.TYPE_CHAR,

        #Escopo e Sintaxe
        "simbora" : TokenType. 
    }