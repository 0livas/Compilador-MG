from difflib import get_close_matches

from .tokenType import TokenType, PALAVRAS_CHAVE

class GerenciadorTokens:
    """Gerencia tabelas hash de palavras-chave e símbolos.
    
    Mantém três tabelas hash para busca O(1):
    - palavras_chave: Keywords da linguagem Minerês
    - simbolos_simples: Operadores/delimitadores de 1 caractere
    - simbolos_compostos: Operadores de 2+ caracteres
    """

    def __init__(self):
        self.palavras_chave = PALAVRAS_CHAVE.copy()
        self.simbolos_simples = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "%": TokenType.MOD,
            ",": TokenType.COMMA,
            "(": TokenType.LEFT_PAREN,
            ")": TokenType.RIGHT_PAREN,
            "{": TokenType.BEGIN_BLOCK,
            "}": TokenType.END_BLOCK,
            "<": TokenType.LESS,
            ">": TokenType.GREATER,
            ":": TokenType.COLON,
        }
        self.simbolos_compostos = {
            "<=": TokenType.LESS_EQUAL,
            ">=": TokenType.GREATER_EQUAL,
        }

    def buscar_palavra_chave(self, lexema: str) -> TokenType | None:
        """Busca palavra-chave na tabela (case-insensitive)."""
        lexema_lower = lexema.lower()
        return self.palavras_chave.get(lexema_lower)

    def sugerir_palavra_chave_proxima(self, lexema: str, cutoff: float = 0.8) -> str | None:
        """Retorna palavra-chave mais próxima para possíveis typos."""
        if not lexema:
            return None

        matches = get_close_matches(
            lexema.lower(),
            list(self.palavras_chave.keys()),
            n=1,
            cutoff=cutoff,
        )
        return matches[0] if matches else None

    def buscar_simbolo_composto(self, simbolo: str) -> TokenType | None:
        """Busca símbolo composto (==, !=, <=, >=, etc)."""
        return self.simbolos_compostos.get(simbolo)

    def buscar_simbolo_simples(self, simbolo: str) -> TokenType | None:
        """Busca símbolo simples (1 caractere)."""
        return self.simbolos_simples.get(simbolo)

    def eh_parte_de_numero(self, char: str) -> bool:
        """Verifica se caractere pode fazer parte de um número."""
        return char.isdigit() or char in "xXabcdefABCDEF."

    def eh_parte_de_identificador(self, char: str) -> bool:
        """Verifica se caractere pode fazer parte de um identificador."""
        return char.isalnum() or char == "_"

    def eh_espaco_em_branco(self, char: str) -> bool:
        """Verifica se caractere é espaço em branco."""
        return char in " \t\r"

    def eh_delimitador(self, char: str) -> bool:
        """Verifica se caractere é um delimitador/operador."""
        return char in self.simbolos_simples or char in "{}()'\":"

    def get_tamanho_palavras_chave(self) -> int:
        """Retorna quantidade de palavras-chave registradas."""
        return len(self.palavras_chave)

    def listar_palavras_chave(self) -> dict:
        """Retorna cópia da tabela de palavras-chave."""
        return dict(self.palavras_chave)