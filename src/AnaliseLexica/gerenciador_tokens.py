from tokenType import TokenType, PALAVRAS_CHAVE

class GerenciadorTokens:

    def __init__(self):
        self.palavras_chave = PALAVRAS_CHAVE.copy()
        self.simbolos_simples = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.MULTIPLY,
            "/": TokenType.DIVIDE,
            "%": TokenType.MOD,
            ";": TokenType.SEMICOLON,
            ",": TokenType.COMMA,
            "(": TokenType.LEFT_PAREN,
            ")": TokenType.RIGHT_PAREN,
            "{": TokenType.BEGIN_BLOCK,
            "}": TokenType.END_BLOCK,
            '"': TokenType.QUOTE,
            "'": TokenType.SINGLE_QUOTE,
            "=": TokenType.ASSIGN,
            "!": TokenType.NOT,
            "&": TokenType.AND,
            "|": TokenType.OR,
            "^": TokenType.XOR,
            "<": TokenType.LESS,
            ">": TokenType.GREATER,
        }
        self.simbolos_compostos = {
            "==": TokenType.EQUAL,
            "!=": TokenType.NOT_EQUAL,
            "<=": TokenType.LESS_EQUAL,
            ">=": TokenType.GREATER_EQUAL,
            "&&": TokenType.AND,
            "||": TokenType.OR,
            "//": TokenType.WHOLE_DIVISION,
        }

    def buscar_palavra_chave(self, lexema: str) -> TokenType | None:
        lexema_lower = lexema.lower()
        return self.palavras_chave.get(lexema_lower)

    def buscar_simbolo_composto(self, simbolo: str) -> TokenType | None:
        return self.simbolos_compostos.get(simbolo)

    def buscar_simbolo_simples(self, simbolo: str) -> TokenType | None:
        return self.simbolos_simples.get(simbolo)

    def eh_parte_de_numero(self, char: str) -> bool:
        return char.isdigit() or char in "xXoObB._eE+-"

    def eh_parte_de_identificador(self, char: str) -> bool:
        return char.isalnum() or char == "_"

    def eh_espaco_em_branco(self, char: str) -> bool:
        return char in " \t\r"

    def eh_delimitador(self, char: str) -> bool:
        return char in self.simbolos_simples or char in "(){}[];,.\"\'"

    def get_tamanho_palavras_chave(self) -> int:
        return len(self.palavras_chave)

    def listar_palavras_chave(self) -> dict:
        return dict(self.palavras_chave)
