from dataclasses import dataclass


@dataclass
class Token:
    """Representa um token extraído durante a análise léxica.
    
    Atributos:
        lexema: O texto original do token no código-fonte
        token: Tipo do token (TokenType)
        linha: Número da linha onde o token foi encontrado (1-indexed)
        coluna: Número da coluna onde o token foi encontrado (0-indexed)
    """
    lexema: str = ""
    token: int = 0
    linha: int = 0
    coluna: int = 0