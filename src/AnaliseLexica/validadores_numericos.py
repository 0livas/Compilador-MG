import re
from enum import Enum
from tokenType import TokenType

class TipoNumero(Enum):
    """Tipos de números suportados pela linguagem Minerês."""
    INTEIRO_DECIMAL = 1
    INTEIRO_HEXADECIMAL = 2
    INTEIRO_OCTAL = 3
    INTEIRO_BINARIO = 4
    PONTO_FLUTUANTE = 5
    NOTACAO_CIENTIFICA = 6

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
            TipoNumero.INTEIRO_OCTAL: re.compile(r"^0[oO][0-7]+$"),
            TipoNumero.INTEIRO_BINARIO: re.compile(r"^0[bB][01]+$"),
            TipoNumero.NOTACAO_CIENTIFICA: re.compile(r"^\d+(\.\d+)?[eE][+-]?\d+$"),
            TipoNumero.PONTO_FLUTUANTE: re.compile(r"^\d+\.\d+$"),
            TipoNumero.INTEIRO_DECIMAL: re.compile(r"^\d+$"),
        }

    def validar_numero(self, lexema: str) -> tuple[bool, TipoNumero | None]:
        """Valida e classifica um número. Testa padrões em ordem específica."""
        if not lexema:
            return False, None

        ordem_validacao = [
            TipoNumero.INTEIRO_HEXADECIMAL,
            TipoNumero.INTEIRO_OCTAL,
            TipoNumero.INTEIRO_BINARIO,
            TipoNumero.NOTACAO_CIENTIFICA,
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
            TipoNumero.INTEIRO_BINARIO,
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
            TipoNumero.INTEIRO_BINARIO: "inteiro binário",
            TipoNumero.PONTO_FLUTUANTE: "ponto flutuante",
            TipoNumero.NOTACAO_CIENTIFICA: "notação científica",
        }
        return descricoes.get(tipo_numero, "número desconhecido")

    def eh_inicio_numero(self, char: str) -> bool:
        """Verifica se caractere pode iniciar um número."""
        return char.isdigit()

    def validar_sequencia_numerica(self, lexema: str) -> bool:
        """Valida se sequência de caracteres forma um número."""
        if not lexema:
            return False

        if lexema.startswith(("0x", "0X", "0o", "0O", "0b", "0B")):
            return len(lexema) > 2

        return all(c.isdigit() or c in ".eE+-" for c in lexema)
