from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from AnaliseLexica.mineires_token import Token
from AnaliseLexica.tokenType import TokenType

from .nos_ast import (
    AssignmentExpr,
    AssignmentStmt,
    BinaryExpr,
    Block,
    BreakStmt,
    ContinueStmt,
    Declaration,
    DeclarationItem,
    EmptyStmt,
    Expression,
    ExpressionStmt,
    ForStmt,
    FunctionDecl,
    Identifier,
    IfStmt,
    InputStmt,
    Literal,
    OutputStmt,
    Program,
    ReturnStmt,
    Statement,
    SwitchCase,
    SwitchStmt,
    UnaryExpr,
    WhileStmt,
)


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
        self.programa: Program | None = None
        self._stmt_callbacks = {
            TokenType.FOR: self.for_stmt,
            TokenType.INPUT: self.io_stmt,
            TokenType.OUTPUT: self.io_stmt,
            TokenType.WHILE: self.while_stmt,
            TokenType.IF: self.if_stmt,
            TokenType.SWITCH: self.case_stmt,
            TokenType.BEGIN_BLOCK: self.bloco,
            TokenType.BREAK: self._break_stmt,
            TokenType.CONTINUE: self._continue_stmt,
            TokenType.RETURN: self._return_stmt,
            TokenType.SEMICOLON: self._empty_stmt,
            TokenType.TYPE_INT: self.declaration,
            TokenType.TYPE_FLOAT: self.declaration,
            TokenType.TYPE_STRING: self.declaration,
            TokenType.TYPE_BOOLEAN: self.declaration,
            TokenType.TYPE_CHAR: self.declaration,
        }

    def analisar(self) -> Program:
        programa = self.programa_()
        self.programa = programa
        return programa

    def programa_(self) -> Program:
        funcoes: list[FunctionDecl] = []

        if not self.verificar(TokenType.FUNCTION):
            self.erro("Esperava declaração de função iniciando com 'bora_cumpade'")

        while self.verificar(TokenType.FUNCTION):
            funcoes.append(self.function_())

        if not any(funcao.name == "main" for funcao in funcoes):
            self.erro("Esperava ao menos uma função 'main'")

        self.consumir(TokenType.EOF)
        return Program(funcoes)

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
                mensagem=mensagem or "Token inesperado",
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

    def function_(self) -> FunctionDecl:
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
        corpo = self.bloco()
        return FunctionDecl(nome_funcao, corpo)

    def type_(self) -> str:
        token = self.atual()
        if self.match(
            TokenType.TYPE_INT,
            TokenType.TYPE_FLOAT,
            TokenType.TYPE_STRING,
            TokenType.TYPE_BOOLEAN,
            TokenType.TYPE_CHAR,
        ):
            return token.lexema or token.token.name

        self.erro("Esperava um tipo válido")
        return ""

    def bloco(self) -> Block:
        self.consumir(TokenType.BEGIN_BLOCK, "Esperava 'simbora'")
        statements = self.stmt_list({TokenType.END_BLOCK})
        self.consumir(TokenType.END_BLOCK, "Esperava 'cabo'")
        return Block(statements)

    def stmt_list(self, terminadores: set[TokenType]) -> list[Statement]:
        statements: list[Statement] = []
        while not self.esta_no_fim() and self.atual().token not in terminadores:
            statements.append(self.stmt())
        return statements

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

    def stmt(self) -> Statement:
        token_type = self.atual().token
        callback = self._stmt_callbacks.get(token_type)
        if callback is not None:
            return callback()

        expression = self.expr()
        self.consumir(TokenType.SEMICOLON, "Esperava 'uai' após atribuição")
        return self._expressao_para_stmt(expression)

    def _break_stmt(self) -> BreakStmt:
        self.avancar()
        self.consumir(TokenType.SEMICOLON, "Esperava 'uai' após 'para_o_trem'")
        return BreakStmt()

    def _continue_stmt(self) -> ContinueStmt:
        self.avancar()
        self.consumir(TokenType.SEMICOLON, "Esperava 'uai' após 'toca_o_trem'")
        return ContinueStmt()

    def _return_stmt(self) -> ReturnStmt:
        self.avancar()
        value = self.expr()
        self.consumir(TokenType.SEMICOLON, "Esperava 'uai' após retorno")
        return ReturnStmt(value)

    def _empty_stmt(self) -> EmptyStmt:
        self.avancar()
        return EmptyStmt()

    def _expressao_para_stmt(self, expression: Expression) -> Statement:
        if isinstance(expression, AssignmentExpr):
            return AssignmentStmt(expression.target, expression.value)
        return ExpressionStmt(expression)

    def for_declaration(self) -> Declaration:
        return self.declaration(require_semicolon=False)

    def declaration(self, require_semicolon: bool = True) -> Declaration:
        tipo = self.type_()
        items = [self.decl_item()]
        while self.match(TokenType.COMMA):
            items.append(self.decl_item())

        if require_semicolon:
            self.consumir(TokenType.SEMICOLON, "Esperava 'uai' após declaração")
        return Declaration(tipo, items)

    def decl_item(self) -> DeclarationItem:
        token_nome = self.consumir(TokenType.IDENTIFIER, "Esperava identificador")
        initializer = None

        if self.match(TokenType.ASSIGN):
            initializer = self.expr()

        return DeclarationItem(token_nome.lexema, initializer)

    def ident_list(self) -> list[str]:
        identifiers = [self.consumir(TokenType.IDENTIFIER, "Esperava identificador").lexema]
        while self.match(TokenType.COMMA):
            identifiers.append(self.consumir(TokenType.IDENTIFIER, "Esperava identificador após ','").lexema)
        return identifiers

    def for_stmt(self) -> ForStmt:
        self.consumir(TokenType.FOR, "Esperava 'roda_esse_trem'")
        self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após for")

        init: Statement | None = None
        if not self.verificar(TokenType.SEMICOLON):
            if self.atual().token in {
                TokenType.TYPE_INT,
                TokenType.TYPE_FLOAT,
                TokenType.TYPE_STRING,
                TokenType.TYPE_BOOLEAN,
                TokenType.TYPE_CHAR,
            }:
                init = self.for_declaration()
            else:
                init = self._expressao_para_stmt(self.expr())
        self.consumir(TokenType.SEMICOLON, "Esperava separador do for")

        condition = None
        if not self.verificar(TokenType.SEMICOLON):
            condition = self.expr()
        self.consumir(TokenType.SEMICOLON, "Esperava separador do for")

        update = None
        if not self.verificar(TokenType.RIGHT_PAREN):
            update = self.expr()
        self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' ao final do for")

        body = self.stmt()
        return ForStmt(init, condition, update, body)

    def io_stmt(self) -> Statement:
        if self.match(TokenType.INPUT):
            self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após 'xove'")
            tipo = ""
            if self.atual().token in {
                TokenType.TYPE_INT,
                TokenType.TYPE_FLOAT,
                TokenType.TYPE_STRING,
                TokenType.TYPE_BOOLEAN,
                TokenType.TYPE_CHAR,
            }:
                tipo = self.type_()
                self.consumir(TokenType.COMMA, "Esperava ',' em xove")
            token_nome = self.consumir(TokenType.IDENTIFIER, "Esperava identificador em xove")
            self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' em xove")
            self.consumir(TokenType.SEMICOLON, "Esperava 'uai' após xove")
            return InputStmt(tipo, token_nome.lexema)

        if self.match(TokenType.OUTPUT):
            self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após 'oia_proce_ve'")
            values = self.out_list()
            self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' em oia_proce_ve")
            self.consumir(TokenType.SEMICOLON, "Esperava 'uai' após saída")
            return OutputStmt(values)

        self.erro("Esperava comando de entrada ou saída")
        return EmptyStmt()

    def out_list(self) -> list[Expression]:
        values = [self.out()]
        while self.match(TokenType.COMMA):
            values.append(self.out())
        return values

    def out(self) -> Expression:
        return self.expr()

    def while_stmt(self) -> WhileStmt:
        self.consumir(TokenType.WHILE, "Esperava 'enquanto_tiver_trem'")
        self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após while")
        condition = self.expr()
        self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' após expressão do while")
        body = self.stmt()
        return WhileStmt(condition, body)

    def if_stmt(self) -> IfStmt:
        self.consumir(TokenType.IF, "Esperava 'uai_se'")
        self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após if")
        condition = self.expr()
        self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' após expressão do if")
        then_branch = self.stmt()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.stmt()
        return IfStmt(condition, then_branch, else_branch)

    def case_stmt(self) -> SwitchStmt:
        self.consumir(TokenType.SWITCH, "Esperava 'dependenu'")
        self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após switch")
        expression = self.expr()
        self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' após switch")
        self.consumir(TokenType.BEGIN_BLOCK, "Esperava 'simbora' no switch")

        cases: list[SwitchCase] = []
        default_statements: list[Statement] | None = None

        while not self.esta_no_fim() and not self.verificar(TokenType.END_BLOCK):
            if self.verificar(TokenType.CASE):
                cases.append(self.do_caso())
                continue

            if self.verificar(TokenType.DEFAULT):
                if default_statements is not None:
                    self.erro("Encontrado mais de um 'uai_so' no switch")
                self.consumir(TokenType.DEFAULT, "Esperava 'uai_so'")
                self.consumir(TokenType.COLON, "Esperava ':' após uai_so")
                default_statements = self.stmt_list({TokenType.END_BLOCK})
                continue

            self.erro("Esperava 'du_casu' ou 'uai_so' no switch")

        self.consumir(TokenType.END_BLOCK, "Esperava 'cabo' no switch")
        return SwitchStmt(expression, cases, default_statements)

    def do_caso(self) -> SwitchCase:
        self.consumir(TokenType.CASE, "Esperava 'du_casu'")
        value = self.expr()
        self.consumir(TokenType.COLON, "Esperava ':' após valor do caso")
        statements = self.stmt_list({TokenType.CASE, TokenType.DEFAULT, TokenType.END_BLOCK})
        return SwitchCase(value, statements)

    def expr(self) -> Expression:
        return self.atrib()

    def atrib(self) -> Expression:
        left = self.or_()
        if self.match(TokenType.ASSIGN):
            if not isinstance(left, Identifier):
                self.erro("Esperava identificador à esquerda de atribuição")
            value = self.atrib()
            return AssignmentExpr(left, value)
        return left

    def or_(self) -> Expression:
        expression = self.xor()
        while self.match(TokenType.OR):
            operator = self.anterior().token.name
            right = self.xor()
            expression = BinaryExpr(operator, expression, right)
        return expression

    def xor(self) -> Expression:
        expression = self.and_()
        while self.match(TokenType.XOR):
            operator = self.anterior().token.name
            right = self.and_()
            expression = BinaryExpr(operator, expression, right)
        return expression

    def and_(self) -> Expression:
        expression = self.not_()
        while self.match(TokenType.AND):
            operator = self.anterior().token.name
            right = self.not_()
            expression = BinaryExpr(operator, expression, right)
        return expression

    def not_(self) -> Expression:
        if self.match(TokenType.NOT):
            operator = self.anterior().token.name
            return UnaryExpr(operator, self.not_())
        return self.rel()

    def rel(self) -> Expression:
        expression = self.add()
        while self.match(
            TokenType.EQUAL,
            TokenType.NOT_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ):
            operator = self.anterior().token.name
            right = self.add()
            expression = BinaryExpr(operator, expression, right)
        return expression

    def add(self) -> Expression:
        expression = self.mult()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.anterior().token.name
            right = self.mult()
            expression = BinaryExpr(operator, expression, right)
        return expression

    def mult(self) -> Expression:
        expression = self.uno()
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MOD):
            operator = self.anterior().token.name
            right = self.uno()
            expression = BinaryExpr(operator, expression, right)
        return expression

    def uno(self) -> Expression:
        if self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.anterior().token.name
            return UnaryExpr(operator, self.uno())
        return self.fator_zao()

    def fator_zao(self) -> Expression:
        if self.match(TokenType.LEFT_PAREN):
            expression = self.atrib()
            self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' após expressão")
            return expression
        return self.fator_zin()

    def fator_zin(self) -> Expression:
        if self.match(TokenType.LITERAL_STRING):
            token = self.anterior()
            return Literal(token.token.name, token.lexema)

        if self.match(TokenType.LITERAL_INT):
            token = self.anterior()
            return Literal(token.token.name, token.lexema)

        if self.match(TokenType.LITERAL_FLOAT):
            token = self.anterior()
            return Literal(token.token.name, token.lexema)

        if self.match(TokenType.LITERAL_CHAR):
            token = self.anterior()
            return Literal(token.token.name, token.lexema)

        if self.match(TokenType.TRUE):
            token = self.anterior()
            return Literal(token.token.name, token.lexema)

        if self.match(TokenType.FALSE):
            token = self.anterior()
            return Literal(token.token.name, token.lexema)

        if self.match(TokenType.IDENTIFIER):
            token = self.anterior()
            return Identifier(token.lexema)

        self.erro("Esperava literal, identificador ou expressão entre parênteses")
        return Literal("LITERAL_INT", "0")