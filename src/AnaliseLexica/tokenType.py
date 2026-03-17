from enum import Enum, auto

class TokenType(Enum):
    # Main
    MAIN = auto()

    # Condicionais
    IF = auto()
    ELSE = auto()
    ELIF = auto()

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

    BOOLEAN = auto()
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
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()

    # Operadores Relacionais
    LESS = auto()
    GREATER = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    ASSIGN = auto()
    DIFFERENT = auto()
    DOUBLE_EQUAL = auto()

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
    CIN = auto()
    COUT = auto()

    # Texto e Documentação
    COMMENT_INLINE = auto()
    COMMENT_BEGIN = auto()
    COMMENT_END = auto()

    # Bases Numéricas
    LITERAL_INT = auto()
    LITERAL_FLOAT = auto()
    LITERAL_STRING = auto()
    LITERAL_CHAR = auto()

    # Identificador
    IDENTIFIER = auto()

    # Fim do Código
    EOF = auto()