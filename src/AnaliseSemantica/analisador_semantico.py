from __future__ import annotations
from typing import Optional, Dict, Tuple
from AnaliseSintatica.nos_ast import Literal

class SemanticError(Exception):
    def __init__(self, message: str, linha: int = 0, coluna: int = 0):
        self.message = message
        self.linha = linha
        self.coluna = coluna
        super().__init__(self.message)

    def __str__(self):
        if self.linha > 0 and self.coluna > 0:
            return f"Erro Semântico na linha {self.linha}, coluna {self.coluna}: {self.message}"
        return f"Erro Semântico: {self.message}"

class SymbolTable:
    def __init__(self, parent: Optional[SymbolTable] = None):
        self.symbols: Dict[str, str] = {}
        self.parent = parent

    def define(self, name: str, type_: str) -> bool:
        if name in self.symbols:
            return False
        self.symbols[name] = type_
        return True

    def lookup(self, name: str) -> Optional[str]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

class AnalisadorSemantico:
    def __init__(self):
        self.tabela_simbolos = SymbolTable()
        self.MAPA_TIPOS = {
            "trem_di_numeru": "INT",
            "trem_cum_virgula": "FLOAT",
            "trem_discrita": "STRING",
            "trem_discolhe": "BOOL",
            "trosso": "CHAR"
        }

    def entrar_escopo(self):
        self.tabela_simbolos = SymbolTable(self.tabela_simbolos)

    def sair_escopo(self):
        if self.tabela_simbolos.parent:
            self.tabela_simbolos = self.tabela_simbolos.parent

    def declarar_variavel(self, nome: str, tipo_mineres: str, linha: int = 0, coluna: int = 0):
        tipo_interno = self.MAPA_TIPOS.get(tipo_mineres, tipo_mineres)
        if not self.tabela_simbolos.define(nome, tipo_interno):
            raise SemanticError(f"Redeclaração da variável '{nome}' no mesmo escopo.", linha, coluna)

    def obter_tipo_variavel(self, nome: str, linha: int = 0, coluna: int = 0) -> str:
        tipo = self.tabela_simbolos.lookup(nome)
        if tipo is None:
            raise SemanticError(f"Variável '{nome}' não foi declarada previamente.", linha, coluna)
        return tipo

    def validar_operacao_binaria(self, operador: str, tipo_esq: str, tipo_dir: str, linha: int = 0, coluna: int = 0) -> str:
        if tipo_esq != tipo_dir:
            raise SemanticError(f"Tipos incompatíveis para operação '{operador}': {tipo_esq} e {tipo_dir}", linha, coluna)
        
        if operador in ["EQUAL", "NOT_EQUAL", "LESS", "LESS_EQUAL", "GREATER", "GREATER_EQUAL"]:
            return "BOOL"
        
        if operador in ["MOD", "WHOLE_DIVISION"] and tipo_esq != "INT":
             raise SemanticError(f"Operação '{operador}' só é permitida para o tipo INT.", linha, coluna)
        
        if operador in ["AND", "OR", "XOR"] and tipo_esq != "BOOL":
             raise SemanticError(f"Operação lógica '{operador}' só é permitida para o tipo BOOL.", linha, coluna)

        return tipo_esq

    def validar_operacao_unaria(self, operador: str, tipo: str, linha: int = 0, coluna: int = 0) -> str:
        if operador == "NOT" and tipo != "BOOL":
            raise SemanticError(f"Operador 'NOT' só pode ser aplicado a BOOL.", linha, coluna)
        if operador in ["PLUS", "MINUS"] and tipo not in ["INT", "FLOAT"]:
            raise SemanticError(f"Operador '{operador}' só pode ser aplicado a tipos numéricos.", linha, coluna)
        return tipo

    def converter_e_obter_tipo_literal(self, literal: Literal) -> Tuple[str, str]:
        """Converte o valor se necessário (hexa/octal -> decimal) e retorna (valor_normalizado, tipo_interno)."""
        kind = literal.kind
        value = literal.value
        linha = getattr(literal, "linha", 0)
        coluna = getattr(literal, "coluna", 0)

        if kind == "LITERAL_INT":
            try:
                if value.lower().startswith("0x"):
                    return str(int(value, 16)), "INT"
                elif value.startswith("0") and len(value) > 1 and value[1].isdigit():
                    return str(int(value, 8)), "INT"
                return str(int(value)), "INT"
            except ValueError:
                 raise SemanticError(f"Literal inteiro inválido: {value}", linha, coluna)
        
        if kind == "LITERAL_FLOAT":
            return value, "FLOAT"
        if kind == "LITERAL_STRING":
            return value, "STRING"
        if kind == "LITERAL_CHAR":
            return value, "CHAR"
        if kind in ["TRUE", "FALSE"]:
            return value, "BOOL"
            
        return value, "UNKNOWN"
