import re
from enum import Enum
from tokenType import TokenType

class TipoNumero(Enum):
    """Tipos de números suportados pela linguagem Minerês."""
    INTEIRO_DECIMAL = 1
    INTEIRO_HEXADECIMAL = 2
    INTEIRO_OCTAL = 3
    PONTO_FLUTUANTE = 4

class ValidadorNumerico:
    """Valida e classifica números usando regex.
    
    Suporta 4 bases/formatos:
    - Decimal/Real: 42, 0, 30, .33 ...
    - Hexadecimal: 0xFF
    - Octal: 01, 07, 017
    """

    def __init__(self):
        self.padroes = {
            TipoNumero.INTEIRO_HEXADECIMAL: re.compile(r"^0[xX][0-9A-Fa-f]+$"),
            TipoNumero.INTEIRO_OCTAL: re.compile(r"^0[0-7]+$"),
            TipoNumero.PONTO_FLUTUANTE: re.compile(r"^(\d+\.\d+|\.\d+)$"),
            TipoNumero.INTEIRO_DECIMAL: re.compile(r"^(0|[1-9]\d*)$"),
        }

    def validar_numero(self, lexema: str) -> tuple[bool, TipoNumero | None]:
        """Valida e classifica um número. Testa padrões em ordem específica."""
        if not lexema:
            return False, None

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