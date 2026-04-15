from dataclasses import dataclass
from typing import Optional

from AnaliseLexica.mineires_token import Token
from AnaliseLexica.tokenType import TokenType

@dataclass
class ErroSintatico:
    mensagem: str
    linha: int
    coluna: int
    esperado: Optional[str] = None
    encontrado: Optional[str] = None

    def __str__(self) -> str:
        texto = f"Erro Sintático na linha {self.linha}, coluna {self.coluna}: {self.mensagem}"
        if self.esperado:
            texto += f"\n  Esperado: {self.esperado}"
        if self.encontrado:
            texto += f"\n  Encontrado: {self.encontrado}"
        return texto


class ExcecaoSintatica(Exception):
    def __init__(self, erro: ErroSintatico):
        self.erro = erro
        super().__init__(str(erro))


class AnalisadorSintatico:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.posicao = 0

    def analisar(self) -> bool:
        encontrou_main = False
        nomes_funcoes: set[str] = set()

        if not self.verificar(TokenType.FUNCTION):
            self.erro("Esperava declaração de função iniciando com 'bora_cumpade'")

        while self.verificar(TokenType.FUNCTION):
            nome_funcao, linha_funcao, coluna_funcao = self.function_()

            if nome_funcao in nomes_funcoes:
                raise ExcecaoSintatica(
                    ErroSintatico(
                        mensagem=f"Função '{nome_funcao}' já foi declarada",
                        linha=linha_funcao,
                        coluna=coluna_funcao,
                        encontrado=f"IDENTIFIER ('{nome_funcao}')",
                    )
                )

            nomes_funcoes.add(nome_funcao)

            if nome_funcao == "main":
                encontrou_main = True

        if not encontrou_main:
            self.erro("Esperava ao menos uma função 'main'")

        self.consumir(TokenType.EOF)
        return True

    def atual(self) -> Token:
        return self.tokens[self.posicao]

    def anterior(self) -> Token:
        return self.tokens[self.posicao - 1]

    def avancar(self) -> Token:
        if not self.esta_no_fim():
            self.posicao += 1
        return self.anterior()

    def esta_no_fim(self) -> bool:
        return self.atual().token == TokenType.EOF

    def verificar(self, token_type: TokenType) -> bool:
        if self.esta_no_fim():
            return token_type == TokenType.EOF
        return self.atual().token == token_type

    def verificar_lexema(self, lexema: str) -> bool:
        return self.atual().lexema == lexema

    def match(self, *tipos: TokenType) -> bool:
        for tipo in tipos:
            if self.verificar(tipo):
                self.avancar()
                return True
        return False

    def consumir(self, tipo: TokenType, mensagem: str = "") -> Token:
        if self.verificar(tipo):
            return self.avancar()

        token = self.atual()
        raise ExcecaoSintatica(
            ErroSintatico(
                mensagem=mensagem or f"Token inesperado",
                linha=token.linha,
                coluna=token.coluna,
                esperado=tipo.name,
                encontrado=f"{token.token.name} ('{token.lexema}')",
            )
        )

    def erro(self, mensagem: str) -> None:
        token = self.atual()
        raise ExcecaoSintatica(
            ErroSintatico(
                mensagem=mensagem,
                linha=token.linha,
                coluna=token.coluna,
                encontrado=f"{token.token.name} ('{token.lexema}')",
            )
        )

    def function_(self) -> tuple[str, int, int]:
        self.consumir(TokenType.FUNCTION, "Esperava 'bora_cumpade'")

        if self.verificar(TokenType.MAIN):
            token_nome = self.avancar()
        else:
            token_nome = self.consumir(
                TokenType.IDENTIFIER,
                "Esperava nome da função (identificador) ou 'main'",
            )

        nome_funcao = token_nome.lexema

        self.consumir(TokenType.LEFT_PAREN, f"Esperava '(' após {nome_funcao}")
        self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' após '('")
        self.bloco()
        return nome_funcao, token_nome.linha, token_nome.coluna

    def type_(self) -> None:
        if not self.match(
            TokenType.TYPE_INT,
            TokenType.TYPE_FLOAT,
            TokenType.TYPE_STRING,
            TokenType.TYPE_BOOLEAN,
            TokenType.TYPE_CHAR,
        ):
            self.erro("Esperava um tipo válido")

    def bloco(self) -> None:
        self.consumir(TokenType.BEGIN_BLOCK, "Esperava 'simbora'")
        self.stmt_list()
        self.consumir(TokenType.END_BLOCK, "Esperava 'cabo'")

    def stmt_list(self) -> None:
        while self.inicio_de_stmt():
            self.stmt()

    def inicio_de_stmt(self) -> bool:
        return self.atual().token in {
            TokenType.FOR,
            TokenType.INPUT,
            TokenType.OUTPUT,
            TokenType.WHILE,
            TokenType.IF,
            TokenType.SWITCH,
            TokenType.BEGIN_BLOCK,
            TokenType.BREAK,
            TokenType.CONTINUE,
            TokenType.RETURN,
            TokenType.SEMICOLON,
            TokenType.TYPE_INT,
            TokenType.TYPE_FLOAT,
            TokenType.TYPE_STRING,
            TokenType.TYPE_BOOLEAN,
            TokenType.TYPE_CHAR,
            TokenType.IDENTIFIER,
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.NOT,
            TokenType.LEFT_PAREN,
            TokenType.LITERAL_STRING,
            TokenType.LITERAL_INT,
            TokenType.LITERAL_FLOAT,
            TokenType.LITERAL_CHAR,
            TokenType.TRUE,
            TokenType.FALSE,
        }

    def stmt(self) -> None:
        if self.verificar(TokenType.FOR):
            self.for_stmt()
        elif self.verificar(TokenType.INPUT) or self.verificar(TokenType.OUTPUT):
            self.io_stmt()
        elif self.verificar(TokenType.WHILE):
            self.while_stmt()
        elif self.verificar(TokenType.IF):
            self.if_stmt()
        elif self.verificar(TokenType.SWITCH):
            self.case_stmt()
        elif self.verificar(TokenType.BEGIN_BLOCK):
            self.bloco()
        elif self.verificar(TokenType.BREAK):
            self.avancar()
            self.consumir(TokenType.SEMICOLON, "Esperava 'uai' após 'para_o_trem'")
        elif self.verificar(TokenType.CONTINUE):
            self.avancar()
            self.consumir(TokenType.SEMICOLON, "Esperava 'uai' após 'toca_o_trem'")
        elif self.verificar(TokenType.RETURN):
            self.avancar()
            self.expr()
            self.consumir(TokenType.SEMICOLON, "Esperava 'uai' após retorno")
        elif self.verificar(TokenType.SEMICOLON):
            self.avancar()
        elif self.verificar(TokenType.TYPE_INT,):
            self.declaration()
        elif self.verificar(TokenType.TYPE_FLOAT):
            self.declaration()
        elif self.verificar(TokenType.TYPE_STRING):
            self.declaration()
        elif self.verificar(TokenType.TYPE_BOOLEAN):
            self.declaration()
        elif self.verificar(TokenType.TYPE_CHAR):
            self.declaration()
        else:
            self.atrib()
            self.consumir(TokenType.SEMICOLON, "Esperava 'uai' após atribuição")

# descricao das instrucoes
    def for_declaration(self) -> None:
        self.type_()
        self.decl_item()
        while self.match(TokenType.COMMA):
            self.decl_item()

    def declaration(self) -> None:
        self.type_()
        self.decl_item()
        while self.match(TokenType.COMMA):
            self.decl_item()
        self.consumir(TokenType.SEMICOLON, "Esperava 'uai' após declaração")

    def decl_item(self) -> None:
        self.consumir(TokenType.IDENTIFIER, "Esperava identificador")

        if self.match(TokenType.ASSIGN):
            self.expr()

    def ident_list(self) -> None:
        self.consumir(TokenType.IDENTIFIER, "Esperava identificador")
        while self.match(TokenType.COMMA):
            self.consumir(TokenType.IDENTIFIER, "Esperava identificador após ','")

    def for_stmt(self) -> None:
        self.consumir(TokenType.FOR, "Esperava 'roda_esse_trem'")
        self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após for")

        if not self.verificar(TokenType.SEMICOLON):
            if self.atual().token in {
                TokenType.TYPE_INT,
                TokenType.TYPE_FLOAT,
                TokenType.TYPE_STRING,
                TokenType.TYPE_BOOLEAN,
                TokenType.TYPE_CHAR,
            }:
                self.for_declaration()
            else:
                self.atrib()
        self.consumir(TokenType.SEMICOLON, "Esperava separador do for")

        if not self.verificar(TokenType.SEMICOLON):
            self.expr()
        self.consumir(TokenType.SEMICOLON, "Esperava separador do for")

        if not self.verificar(TokenType.RIGHT_PAREN):
            self.atrib()
        self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' ao final do for")

        self.stmt()

    def io_stmt(self) -> None:
        if self.match(TokenType.INPUT):
            self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após 'xove'")
            self.type_()
            self.consumir(TokenType.COMMA, "Esperava ',' em xove")
            self.consumir(TokenType.IDENTIFIER, "Esperava identificador em xove")
            self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' em xove")
            self.consumir(TokenType.SEMICOLON, "Esperava 'uai' após xove")
            return

        if self.match(TokenType.OUTPUT):
            self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após 'oia_proce_ve'")
            self.out_list()
            self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' em oia_proce_ve")
            self.consumir(TokenType.SEMICOLON, "Esperava 'uai' após saída")
            return

        self.erro("Esperava comando de entrada ou saída")

    def out_list(self) -> None:
        self.out()
        while self.match(TokenType.COMMA):
            self.out()

    def out(self) -> None:
        self.fator_zin()

    def while_stmt(self) -> None:
        self.consumir(TokenType.WHILE, "Esperava 'enquanto_tiver_trem'")
        self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após while")
        self.expr()
        self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' após expressão do while")
        self.stmt()

    def if_stmt(self) -> None:
        self.consumir(TokenType.IF, "Esperava 'uai_se'")
        self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após if")
        self.expr()
        self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' após expressão do if")
        self.stmt()
        if self.match(TokenType.ELSE):
            self.stmt()

    def case_stmt(self) -> None:
        self.consumir(TokenType.SWITCH, "Esperava 'dependenu'")
        self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após switch")
        self.consumir(TokenType.IDENTIFIER, "Esperava identificador no switch")
        self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' após switch")
        self.consumir(TokenType.BEGIN_BLOCK, "Esperava 'simbora' no switch")
        self.dos_casos()
        self.consumir(TokenType.END_BLOCK, "Esperava 'cabo' no switch")

    def dos_casos(self) -> None:
        while self.verificar(TokenType.CASE) or self.verificar(TokenType.DEFAULT):
            if self.verificar(TokenType.CASE):
                self.do_caso()
            else:
                self.consumir(TokenType.DEFAULT, "Esperava 'uai_so'")
                self.consumir(TokenType.COLON, "Esperava ':' após uai_so")
                self.stmt()

    def do_caso(self) -> None:
        self.consumir(TokenType.CASE, "Esperava 'du_casu'")
        self.fator_zin()
        self.consumir(TokenType.COLON, "Esperava ':' após valor do caso")
        self.stmt()


# expressoes

    def expr(self) -> None:
        self.atrib()

    def atrib(self) -> None:
        self.or_()
        if self.match(TokenType.ASSIGN):
            self.atrib()

    def or_(self) -> None:
        self.xor()
        while self.match(TokenType.OR):
            self.xor()

    def xor(self) -> None:
        self.and_()
        while self.match(TokenType.XOR):
            self.and_()

    def and_(self) -> None:
        self.not_()
        while self.match(TokenType.AND):
            self.not_()

    def not_(self) -> None:
        if self.match(TokenType.NOT):
            self.not_()
        else:
            self.rel()

    def rel(self) -> None:
        self.add()
        while self.match(
            TokenType.EQUAL,
            TokenType.NOT_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ):
            self.add()

    def add(self) -> None:
        self.mult()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            self.mult()

    def mult(self) -> None:
        self.uno()
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MOD):
            self.uno()

    def uno(self) -> None:
        if self.match(TokenType.PLUS, TokenType.MINUS):
            self.uno()
        else:
            self.fator_zao()

    def fator_zao(self) -> None:
        if self.match(TokenType.LEFT_PAREN):
            self.atrib()
            self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' após expressão")
        else:
            self.fator_zin()

    def fator_zin(self) -> None:
        if self.match(
            TokenType.LITERAL_STRING,
            TokenType.IDENTIFIER,
            TokenType.LITERAL_INT,
            TokenType.LITERAL_FLOAT,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.LITERAL_CHAR,
        ):
            return

        self.erro("Esperava literal, identificador ou expressão entre parênteses")