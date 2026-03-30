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

    #Comentários
    BEGIN_COMMENT = auto()
    END_COMMENT = auto()
    INLINE_COMMENT = auto()

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
    "roda_esse_trem" : TokenType.FOR,
    "enquanto_tiver_trem" : TokenType.WHILE,
    "dependenu" : TokenType.SWITCH,
    "du_casu" : TokenType.CASE,
         
    #Variáveis de Dados
    "trem_di_numeru" : TokenType.TYPE_INT,
    "trem_cum_virgula" : TokenType.TYPE_FLOAT,
    "trem_discrita": TokenType.TYPE_STRING,
    "trem_discolhe" : TokenType.TYPE_BOOLEAN,
    "eh" : TokenType.TRUE,
    "num_eh" : TokenType.FALSE,
    "trosso" : TokenType.TYPE_CHAR,

    #Escopo e Sintaxe
    "simbora" : TokenType.BEGIN_BLOCK,
    "cabo" : TokenType.END_BLOCK,
    "uai": TokenType.SEMICOLON,
    "," : TokenType.COMMA,

    # Operadores Relacionais
    "<" : TokenType.LESS,
    ">" : TokenType.GREATER,
    "<=" : TokenType.LESS_EQUAL,
    ">=" : TokenType.GREATER_EQUAL,
    "fica_assim_entao" : TokenType.ASSIGN,
    "neh_nada" : TokenType.NOT_EQUAL,
    "mema_coisa" : TokenType.EQUAL,

    #Operadores Lógicos
    "quarque_um" : TokenType.OR,
    "vam_marca" : TokenType.NOT,
    "tamem" : TokenType.AND,
    "um_o_oto" : TokenType.XOR,

    #Operadores Aritméticos
    "+" : TokenType.PLUS,
    "-" : TokenType.MINUS,
    "veiz" : TokenType.MULTIPLY,
    "sob" : TokenType.DIVIDE,
    "%" : TokenType.MOD,

    #Entrada e Saída
    "xove" : TokenType.INPUT,
    "oia_proce_ve" : TokenType.OUTPUT,  

    #Comentários
    "//" : TokenType.INLINE_COMMENT,
    "causo" : TokenType.BEGIN_COMMENT,
    "fim_do_causo" : TokenType.END_COMMENT,
}