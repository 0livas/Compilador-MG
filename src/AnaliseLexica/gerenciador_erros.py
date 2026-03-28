from dataclasses import dataclass
from typing import Optional

@dataclass
class ErroLexico:
    """Representa um erro encontrado durante análise léxica.
    
    Atributos:
        tipo: Classificação do erro
        mensagem: Descrição do erro
        linha: Número da linha (1-indexed)
        coluna: Número da coluna (0-indexed)
        lexema: Trecho problemático
        sugestao: Dica para correção
    """

    tipo: str
    mensagem: str
    linha: int
    coluna: int
    lexema: Optional[str] = None
    sugestao: Optional[str] = None

    def __str__(self) -> str:
        """Formata o erro para exibição."""
        resultado = f"Erro Léxico [{self.tipo}] na linha {self.linha}, coluna {self.coluna}:"
        resultado += f"\n  {self.mensagem}"

        if self.lexema:
            resultado += f"\n  Lexema: '{self.lexema}'"

        if self.sugestao:
            resultado += f"\n  Sugestão: {self.sugestao}"

        return resultado

    def para_dict(self) -> dict:
        """Converte o erro para dicionário."""
        return {
            "tipo": self.tipo,
            "mensagem": self.mensagem,
            "linha": self.linha,
            "coluna": self.coluna,
            "lexema": self.lexema,
            "sugestao": self.sugestao,
        }

class GerenciadorErros:
    """Gerencia e acumula erros léxicos durante análise.
    
    Registra erros com contexto completo para relatórios detalhados.
    """

    def __init__(self):
        self.erros: list[ErroLexico] = []

    def registrar_numero_invalido(
        self,
        lexema: str,
        linha: int,
        coluna: int,
        motivo: str = "",
    ) -> None:
        """Registra erro de número inválido."""
        msg = f"Número inválido: '{lexema}'"
        if motivo:
            msg += f" ({motivo})"

        erro = ErroLexico(
            tipo="número inválido",
            mensagem=msg,
            linha=linha,
            coluna=coluna,
            lexema=lexema,
            sugestao="Verifique a sintaxe numérica (bases: decimal, 0x-hex, 0o-octal, 0b-binário)",
        )
        self.erros.append(erro)

    def registrar_string_nao_fechada(
        self, linha_inicio: int, coluna_inicio: int, linha_fim: int
    ) -> None:
        """Registra erro de string não fechada."""
        erro = ErroLexico(
            tipo="string não fechada",
            mensagem=f"String iniciado em linha {linha_inicio}, coluna {coluna_inicio} "
            f"não foi fechado",
            linha=linha_fim,
            coluna=0,
            sugestao='Use aspas duplas (") para fechar a string',
        )
        self.erros.append(erro)

    def registrar_char_nao_fechado(
        self, linha: int, coluna: int, char_lido: str = ""
    ) -> None:
        """Registra erro de caractere literal não fechado."""
        erro = ErroLexico(
            tipo="caractere literal não fechado",
            mensagem="Caractere literal não foi fechado com apóstrofo",
            linha=linha,
            coluna=coluna,
            lexema=f"'{char_lido}",
            sugestao="Use apóstrofos (') para delimitar caracteres: 'a'",
        )
        self.erros.append(erro)

    def registrar_caractere_invalido(
        self, caractere: str, linha: int, coluna: int
    ) -> None:
        erro = ErroLexico(
            tipo="caractere inválido",
            mensagem=f"Caractere não reconhecido: '{caractere}' (ASCII {ord(caractere)})",
            linha=linha,
            coluna=coluna,
            lexema=caractere,
        )
        self.erros.append(erro)

    def registrar_erro_customizado(
        self,
        tipo: str,
        mensagem: str,
        linha: int,
        coluna: int,
        lexema: str = "",
        sugestao: str = "",
    ) -> None:
        erro = ErroLexico(
            tipo=tipo,
            mensagem=mensagem,
            linha=linha,
            coluna=coluna,
            lexema=lexema if lexema else None,
            sugestao=sugestao if sugestao else None,
        )
        self.erros.append(erro)

    def tem_erros(self) -> bool:
        return len(self.erros) > 0

    def quantidade_erros(self) -> int:
        return len(self.erros)

    def obter_erros(self) -> list[ErroLexico]:
        return self.erros.copy()

    def obter_ultimo_erro(self) -> Optional[ErroLexico]:
        return self.erros[-1] if self.erros else None

    def limpar(self) -> None:
        self.erros.clear()

    def gerar_relatorio(self) -> str:
        if not self.tem_erros():
            return "✓ Nenhum erro encontrado"

        relatorio = f"❌ Total de {self.quantidade_erros()} erro(s) encontrado(s):\n\n"
        for i, erro in enumerate(self.erros, 1):
            relatorio += f"{i}. {erro}\n"

        return relatorio

    def filtrar_por_tipo(self, tipo: str) -> list[ErroLexico]:
        return [e for e in self.erros if e.tipo == tipo]

    def filtrar_por_linha(self, linha: int) -> list[ErroLexico]:
        return [e for e in self.erros if e.linha == linha]
