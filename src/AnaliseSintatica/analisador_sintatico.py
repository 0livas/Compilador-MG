from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from AnaliseLexica.mineires_token import Token
from AnaliseLexica.tokenType import TokenType
from AnaliseLexica.gerenciador_tokens import GerenciadorTokens
from AnaliseSintatica.nos_ast import (
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
        self.gerenciador_tokens = GerenciadorTokens()

    def analisar(self) -> Program:
        programa = self.programa_()
        self.programa = programa
        return programa

    def programa_(self) -> Program:
        funcoes = self.function_list()

        if not funcoes:
            self.erro("Esperava declaração de função iniciando com 'bora_cumpade'")

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
        sugestao = self.sugestao_para_token_atual()

        encontrado = f"{token.token.name} ('{token.lexema}')"
        if sugestao:
            encontrado += f" | talvez você quis dizer '{sugestao}'"

        raise ExcecaoSintatica(
            ErroSintatico(
                mensagem=mensagem or "Token inesperado",
                linha=token.linha,
                coluna=token.coluna,
                esperado=tipo.name,
                encontrado=encontrado,
            )
        )

    def consumir_uai(self, mensagem: str) -> Token:
        token = self.consumir(TokenType.SEMICOLON, mensagem)
        if token.lexema != "uai":
            raise ExcecaoSintatica(
                ErroSintatico(
                    mensagem=mensagem,
                    linha=token.linha,
                    coluna=token.coluna,
                    esperado="uai",
                    encontrado=f"{token.token.name} ('{token.lexema}')",
                )
            )
        return token

    def consumir_ponto_virgula_for(self, mensagem: str) -> Token:
        token = self.consumir(TokenType.SEMICOLON, mensagem)
        if token.lexema != ";":
            raise ExcecaoSintatica(
                ErroSintatico(
                    mensagem=mensagem,
                    linha=token.linha,
                    coluna=token.coluna,
                    esperado=";",
                    encontrado=f"{token.token.name} ('{token.lexema}')",
                )
            )
        return token

    def sugestao_para_token_atual(self) -> str | None:
        token = self.atual()
        if token.token != TokenType.IDENTIFIER:
            return None
        return self.gerenciador_tokens.sugerir_palavra_chave(token.lexema)
    
    def verificar_keyword_parecida_no_inicio_stmt(self) -> None:
        token = self.atual()

        if token.token != TokenType.IDENTIFIER:
            return

        sugestao = self.gerenciador_tokens.sugerir_palavra_chave(token.lexema)
        if not sugestao:
            return

        keywords_inicio_stmt = {
            "trem_di_numeru",
            "trem_cum_virgula",
            "trem_discrita",
            "trem_discolhe",
            "trosso",
            "uai_se",
            "uai_senao",
            "roda_esse_trem",
            "enquanto_tiver_trem",
            "dependenu",
            "xove",
            "oia_proce_ve",
            "ta_bao",
            "para_o_trem",
            "toca_o_trem",
            "simbora",
        }

        if sugestao in keywords_inicio_stmt:
            raise ExcecaoSintatica(
                ErroSintatico(
                    mensagem="Palavra-chave inválida no início do comando",
                    linha=token.linha,
                    coluna=token.coluna,
                    esperado="uma palavra-chave válida da linguagem",
                    encontrado=f"{token.token.name} ('{token.lexema}') | talvez você quis dizer '{sugestao}'",
                )
            )

    def erro(self, mensagem: str) -> None:
        token = self.atual()
        sugestao = self.sugestao_para_token_atual()

        encontrado = f"{token.token.name} ('{token.lexema}')"
        if sugestao:
            encontrado += f" | talvez você quis dizer '{sugestao}'"

        raise ExcecaoSintatica(
            ErroSintatico(
                mensagem=mensagem,
                linha=token.linha,
                coluna=token.coluna,
                encontrado=encontrado,
            )
        )

    def function_list(self) -> list[FunctionDecl]:
        funcoes: list[FunctionDecl] = []
        while self.verificar(TokenType.FUNCTION):
            funcoes.append(self.function_())
        return funcoes

    def nome_funcao(self) -> Token:
        if self.verificar(TokenType.MAIN):
            return self.avancar()

        return self.consumir(
            TokenType.IDENTIFIER,
            "Esperava o nome da função"
        )

    def function_(self) -> FunctionDecl:
        self.consumir(TokenType.FUNCTION, "Esperava 'bora_cumpade'")
        token_nome = self.nome_funcao()
        self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após o nome da função")
        self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' após '('")
        corpo = self.bloco()
        return FunctionDecl(token_nome.lexema, corpo)

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
        if self.verificar(TokenType.FOR):
            return self.for_stmt()
        elif self.verificar(TokenType.INPUT) or self.verificar(TokenType.OUTPUT):
            return self.io_stmt()
        elif self.verificar(TokenType.WHILE):
            return self.while_stmt()
        elif self.verificar(TokenType.IF):
            return self.if_stmt()
        elif self.verificar(TokenType.SWITCH):
            return self.case_stmt()
        elif self.verificar(TokenType.BEGIN_BLOCK):
            return self.bloco()
        elif self.verificar(TokenType.BREAK):
            token_inicio = self.avancar()
            self.consumir_uai("Esperava 'uai' após 'para_o_trem'")
            return BreakStmt(linha=token_inicio.linha, coluna=token_inicio.coluna)
        elif self.verificar(TokenType.CONTINUE):
            token_inicio = self.avancar()
            self.consumir_uai("Esperava 'uai' após 'toca_o_trem'")
            return ContinueStmt(linha=token_inicio.linha, coluna=token_inicio.coluna)
        elif self.verificar(TokenType.RETURN):
            token_inicio = self.avancar()
            valor = self.expr()
            self.consumir_uai("Esperava 'uai' após retorno")
            return ReturnStmt(valor, linha=token_inicio.linha, coluna=token_inicio.coluna)
        elif self.verificar(TokenType.SEMICOLON):
            self.consumir_uai("Esperava 'uai'")
            return EmptyStmt()
        elif self.atual().token in {
            TokenType.TYPE_INT,
            TokenType.TYPE_FLOAT,
            TokenType.TYPE_STRING,
            TokenType.TYPE_BOOLEAN,
            TokenType.TYPE_CHAR,
        }:
            return self.declaration()
        else:
            self.verificar_keyword_parecida_no_inicio_stmt()
            expressao = self.expr()
            self.consumir_uai("Esperava 'uai' após atribuição")
            if isinstance(expressao, AssignmentExpr):
                return AssignmentStmt(expressao.target, expressao.value, linha=expressao.linha, coluna=expressao.coluna)
            return ExpressionStmt(expressao)

    # descricao das instrucoes

    def declaration(self) -> Declaration:
        token_inicio = self.atual()
        var_type = self.type_()
        items = [self.decl_item()]
        while self.match(TokenType.COMMA):
            items.append(self.decl_item())
        self.consumir_uai("Esperava 'uai' após declaração")
        return Declaration(var_type, items, linha=token_inicio.linha, coluna=token_inicio.coluna)

    def decl_item(self) -> DeclarationItem:
        token_ident = self.atual()
        identificador = self.consumir(TokenType.IDENTIFIER, "Esperava identificador").lexema
        if self.match(TokenType.ASSIGN):
            valor = self.expr()
            return DeclarationItem(identificador, valor, linha=token_ident.linha, coluna=token_ident.coluna)
        return DeclarationItem(identificador, linha=token_ident.linha, coluna=token_ident.coluna)

    def for_declaration(self) -> Declaration:
        token_inicio = self.atual()
        var_type = self.type_()
        items = [self.decl_item()]
        while self.match(TokenType.COMMA):
            items.append(self.decl_item())
        return Declaration(var_type, items, linha=token_inicio.linha, coluna=token_inicio.coluna)

    def for_stmt(self) -> ForStmt:
        token_inicio = self.atual()
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
                init = ExpressionStmt(self.expr(), linha=self.atual().linha, coluna=self.atual().coluna)
        self.consumir_ponto_virgula_for("Esperava ';' como separador do for")

        condition: Expression | None = None
        if not self.verificar(TokenType.SEMICOLON):
            condition = self.expr()
        self.consumir_ponto_virgula_for("Esperava ';' como separador do for")

        update: Expression | None = None
        if not self.verificar(TokenType.RIGHT_PAREN):
            update = self.expr()
        self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' ao final do for")

        body = self.stmt()
        return ForStmt(init, condition, update, body, linha=token_inicio.linha, coluna=token_inicio.coluna)

    def io_stmt(self) -> Statement:
        if self.match(TokenType.INPUT):
            token_inicio = self.anterior()
            self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após 'xove'")
            var_type = self.type_()
            self.consumir(TokenType.COMMA, "Esperava ',' em xove")
            identificador = self.consumir(TokenType.IDENTIFIER, "Esperava identificador em xove").lexema
            self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' em xove")
            self.consumir_uai("Esperava 'uai' após xove")
            return InputStmt(var_type, identificador, linha=token_inicio.linha, coluna=token_inicio.coluna)

        if self.match(TokenType.OUTPUT):
            token_inicio = self.anterior()
            self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após 'oia_proce_ve'")
            valores = self.out_list()
            self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' em oia_proce_ve")
            self.consumir_uai("Esperava 'uai' após saída")

            return OutputStmt(valores, linha=token_inicio.linha, coluna=token_inicio.coluna)

        self.erro("Esperava comando de entrada ou saída")
        return EmptyStmt()

    def out_list(self) -> list[Expression]:
        valores = [self.out()]
        while self.match(TokenType.COMMA):
            valores.append(self.out())
        return valores

    def out(self) -> Expression:
        return self.fator_zin()

    def while_stmt(self) -> WhileStmt:
        token_inicio = self.atual()
        self.consumir(TokenType.WHILE, "Esperava 'enquanto_tiver_trem'")
        self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após while")
        condition = self.expr()
        self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' após expressão do while")
        body = self.stmt()
        return WhileStmt(condition, body, linha=token_inicio.linha, coluna=token_inicio.coluna)

    def if_stmt(self) -> IfStmt:
        token_inicio = self.atual()
        self.consumir(TokenType.IF, "Esperava 'uai_se'")
        self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após if")
        condition = self.expr()
        self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' após expressão do if")
        then_branch = self.stmt()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.stmt()
        return IfStmt(condition, then_branch, else_branch, linha=token_inicio.linha, coluna=token_inicio.coluna)

    def case_stmt(self) -> SwitchStmt:
        token_inicio = self.atual()
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
            else:
                default_statements = self.default_case()

        self.consumir(TokenType.END_BLOCK, "Esperava 'cabo' no switch")
        return SwitchStmt(expression, cases, default_statements, linha=token_inicio.linha, coluna=token_inicio.coluna)

    def corpo_case(self) -> list[Statement]:
        statements: list[Statement] = []
        while (
            self.inicio_de_stmt()
            and not self.verificar(TokenType.CASE)
            and not self.verificar(TokenType.DEFAULT)
            and not self.verificar(TokenType.END_BLOCK)
        ):
            statements.append(self.stmt())
        return statements

    def do_caso(self) -> SwitchCase:
        token_inicio = self.atual()
        self.consumir(TokenType.CASE, "Esperava 'du_casu'")
        value = self.expr()
        self.consumir(TokenType.COLON, "Esperava ':' após valor do caso")
        statements = self.corpo_case()
        return SwitchCase(value, statements, linha=token_inicio.linha, coluna=token_inicio.coluna)

    def default_case(self) -> list[Statement]:
        self.consumir(TokenType.DEFAULT, "Esperava 'uai_so'")
        self.consumir(TokenType.COLON, "Esperava ':' após uai_so")
        return self.corpo_case()

   
    # expressoes

    def expr(self) -> Expression:
        return self.atrib()

    def atrib(self) -> Expression:
        esquerda = self.or_()

        if self.match(TokenType.ASSIGN):
            if not isinstance(esquerda, Identifier):
                self.erro("Lado esquerdo da atribuição inválido")

            token_operador = self.anterior()
            valor = self.atrib()
            return AssignmentExpr(esquerda, valor, linha=token_operador.linha, coluna=token_operador.coluna)

        return esquerda

    def or_(self) -> Expression:
        esquerda = self.xor()

        while self.match(TokenType.OR):
            operador_token = self.anterior()
            direita = self.xor()
            esquerda = BinaryExpr("OR", esquerda, direita, linha=operador_token.linha, coluna=operador_token.coluna)

        return esquerda

    def xor(self) -> Expression:
        esquerda = self.and_()

        while self.match(TokenType.XOR):
            operador_token = self.anterior()
            direita = self.and_()
            esquerda = BinaryExpr("XOR", esquerda, direita, linha=operador_token.linha, coluna=operador_token.coluna)

        return esquerda

    def and_(self) -> Expression:
        esquerda = self.not_()

        while self.match(TokenType.AND):
            operador_token = self.anterior()
            direita = self.not_()
            esquerda = BinaryExpr("AND", esquerda, direita, linha=operador_token.linha, coluna=operador_token.coluna)

        return esquerda

    def not_(self) -> Expression:
        if self.match(TokenType.NOT):
            operador_token = self.anterior()
            op1 = self.not_()
            return UnaryExpr("NOT", op1, linha=operador_token.linha, coluna=operador_token.coluna)

        return self.rel()

    def rel(self) -> Expression:
        esquerda = self.add()

        while self.match(
            TokenType.EQUAL,
            TokenType.NOT_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ):
            operador_token = self.anterior()
            direita = self.add()
            esquerda = BinaryExpr(operador_token.token.name, esquerda, direita, linha=operador_token.linha, coluna=operador_token.coluna)

        return esquerda

    def add(self) -> Expression:
        esquerda = self.mult()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            operador_token = self.anterior()
            direita = self.mult()
            esquerda = BinaryExpr(operador_token.token.name, esquerda, direita, linha=operador_token.linha, coluna=operador_token.coluna)

        return esquerda

    def mult(self) -> Expression:
        esquerda = self.uno()

        while self.match(
            TokenType.MULTIPLY,
            TokenType.DIVIDE,
            TokenType.WHOLE_DIVISION,
            TokenType.MOD
        ):
            operador_token = self.anterior()
            direita = self.uno()
            esquerda = BinaryExpr(operador_token.token.name, esquerda, direita, linha=operador_token.linha, coluna=operador_token.coluna)

        return esquerda

    def uno(self) -> Expression:
        if self.match(TokenType.PLUS):
            operador_token = self.anterior()
            op1 = self.uno()
            return UnaryExpr("PLUS", op1, linha=operador_token.linha, coluna=operador_token.coluna)

        if self.match(TokenType.MINUS):
            operador_token = self.anterior()
            op1 = self.uno()
            return UnaryExpr("MINUS", op1, linha=operador_token.linha, coluna=operador_token.coluna)

        return self.fator_zao()

    def fator_zao(self) -> Expression:
        if self.match(TokenType.LEFT_PAREN):
            valor = self.atrib()
            self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' após expressão")
            return valor
        else:
            return self.fator_zin()

    def fator_zin(self) -> Expression:
        if self.match(TokenType.LITERAL_STRING):
            token = self.anterior()
            return Literal("LITERAL_STRING", token.lexema, linha=token.linha, coluna=token.coluna)

        if self.match(TokenType.IDENTIFIER):
            token = self.anterior()
            return Identifier(token.lexema, linha=token.linha, coluna=token.coluna)

        if self.match(TokenType.LITERAL_INT):
            token = self.anterior()
            return Literal("LITERAL_INT", token.lexema, linha=token.linha, coluna=token.coluna)

        if self.match(TokenType.LITERAL_FLOAT):
            token = self.anterior()
            return Literal("LITERAL_FLOAT", token.lexema, linha=token.linha, coluna=token.coluna)

        if self.match(TokenType.TRUE):
            token = self.anterior()
            return Literal("TRUE", token.lexema, linha=token.linha, coluna=token.coluna)

        if self.match(TokenType.FALSE):
            token = self.anterior()
            return Literal("FALSE", token.lexema, linha=token.linha, coluna=token.coluna)

        if self.match(TokenType.LITERAL_CHAR):
            token = self.anterior()
            return Literal("LITERAL_CHAR", token.lexema, linha=token.linha, coluna=token.coluna)

        self.erro("Esperava literal, identificador ou expressão entre parênteses")
        token = self.atual()
        return Literal("LITERAL_INT", "0", linha=token.linha, coluna=token.coluna)