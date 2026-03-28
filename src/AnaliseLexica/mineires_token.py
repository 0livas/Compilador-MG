from dataclasses import dataclass

@dataclass
class Token:
    lexema: str = ""
    token: int = 0
    linha: int = 0
    coluna: int = 0