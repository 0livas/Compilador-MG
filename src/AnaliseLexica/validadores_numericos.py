import re
from enum import Enum
from .tokenType import TokenType

class TipoNumero(Enum):
    """Tipos de números suportados pela linguagem Minerês."""
    INTEIRO_DECIMAL = 1
    INTEIRO_HEXADECIMAL = 2
    INTEIRO_OCTAL = 3
    PONTO_FLUTUANTE = 4

class ValidadorNumerico:
    """Valida e classifica números usando regex.
    
    Suporta 6 bases/formatos:
    - Decimal: 42
    - Hexadecimal: 0xFF
    - Octal: 0o77
    - Binário: 0b1010
    - Ponto flutuante: 3.14
    - Notação científica: 1.5e-3
    """

    def __init__(self):
        self.padroes = {
            TipoNumero.INTEIRO_HEXADECIMAL: re.compile(r"^0[xX][0-9A-Fa-f]+$"),
            TipoNumero.INTEIRO_OCTAL: re.compile(r"^0[0-7]+$"),
            TipoNumero.PONTO_FLUTUANTE: re.compile(r"^(?:\d+\.\d*|\.\d+)$"),
            TipoNumero.INTEIRO_DECIMAL: re.compile(r"^(?:0|[1-9]\d*)$"),
        }

    def normalizar_numero(self, lexema: str) -> str:
        """Normaliza formatos numéricos aceitos pela linguagem."""
        if re.match(r"^\d+\.$", lexema):
            return lexema + "0"
        return lexema

    def validar_numero(self, lexema: str) -> tuple[bool, TipoNumero | None]:
        """Valida e classifica um número. Testa padrões em ordem específica."""
        if not lexema:
            return False, None

        lexema = self.normalizar_numero(lexema)

        ordem_validacao = [
            TipoNumero.INTEIRO_HEXADECIMAL,
            TipoNumero.INTEIRO_OCTAL,
            TipoNumero.PONTO_FLUTUANTE,
            TipoNumero.INTEIRO_DECIMAL,
        ]

        for tipo in ordem_validacao:
            if self.padroes[tipo].match(lexema):
                return True, tipo

        return False, None

    def converter_para_token_type(self, tipo_numero: TipoNumero) -> TokenType:
        """Converte TipoNumero para TokenType apropriado."""
        if tipo_numero in [
            TipoNumero.INTEIRO_DECIMAL,
            TipoNumero.INTEIRO_HEXADECIMAL,
            TipoNumero.INTEIRO_OCTAL,
        ]:
            return TokenType.LITERAL_INT
        else:
            return TokenType.LITERAL_FLOAT

    def obter_descricao_tipo(self, tipo_numero: TipoNumero) -> str:
        """Retorna descrição legível do tipo de número."""
        descricoes = {
            TipoNumero.INTEIRO_DECIMAL: "inteiro decimal",
            TipoNumero.INTEIRO_HEXADECIMAL: "inteiro hexadecimal",
            TipoNumero.INTEIRO_OCTAL: "inteiro octal",
            TipoNumero.PONTO_FLUTUANTE: "ponto flutuante",
        }
        return descricoes.get(tipo_numero, "número desconhecido")

    def eh_inicio_numero(self, char: str) -> bool:
        """Verifica se caractere pode iniciar um número."""
        return char.isdigit() or char == "."

    def validar_sequencia_numerica(self, lexema: str) -> bool:
        """Valida se sequência de caracteres forma um número."""
        if not lexema:
            return False

        return self.validar_numero(lexema)[0]