"""Módulo de Análise Léxica - Compilador Minerês.

Fornece tokenização de código Minerês com identificação de:
- Palavras-chave da linguagem
- Números em múltiplas bases
- Strings e caracteres
- Operadores e símbolos
- Comentários
- Erros léxicos
"""

from .analisador_lexico import AnalisadorLexico
from .mineires_token import Token
from .tokenType import TokenType

__all__ = ["AnalisadorLexico", "Token", "TokenType"]
