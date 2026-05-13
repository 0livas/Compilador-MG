from dataclasses import dataclass
from typing import Optional

from AnaliseLexica.mineires_token import Token
from AnaliseLexica.tokenType import TokenType
from AnaliseLexica.gerenciador_tokens import GerenciadorTokens
from Intermediario.gerador_intermediario import GeradorIntermediario

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
        self.gerenciador_tokens = GerenciadorTokens()
        self.gerador = GeradorIntermediario()

    def analisar(self) -> bool:
        self.function_list()
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

    def function_list(self) -> None:
        while self.verificar(TokenType.FUNCTION):
            self.function_()

    def nome_funcao(self) -> Token:
        if self.verificar(TokenType.MAIN):
            return self.avancar()

        return self.consumir(
            TokenType.IDENTIFIER,
            "Esperava o nome da função"
        )

    def function_(self) -> None:
        self.consumir(TokenType.FUNCTION, "Esperava 'bora_cumpade'")
        self.nome_funcao()
        self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após o nome da função")
        self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' após '('")
        self.bloco()

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
            self.consumir_uai("Esperava 'uai' após 'para_o_trem'")
        elif self.verificar(TokenType.CONTINUE):
            self.avancar()
            self.consumir_uai("Esperava 'uai' após 'toca_o_trem'")
        elif self.verificar(TokenType.RETURN):
            self.avancar()
            valor = self.expr()
            self.consumir_uai("Esperava 'uai' após retorno")
            self.gerador.adicionar("ret", valor, None, None)
        elif self.verificar(TokenType.SEMICOLON):
            self.consumir_uai("Esperava 'uai'")
        elif self.atual().token in {
            TokenType.TYPE_INT,
            TokenType.TYPE_FLOAT,
            TokenType.TYPE_STRING,
            TokenType.TYPE_BOOLEAN,
            TokenType.TYPE_CHAR,
        }:
            self.declaration()
        else:
            self.verificar_keyword_parecida_no_inicio_stmt()
            self.atrib()
            self.consumir_uai("Esperava 'uai' após atribuição")

    # descricao das instrucoes

    def declaration(self) -> None:
        self.type_()
        self.decl_item()
        while self.match(TokenType.COMMA):
            self.decl_item()
        self.consumir_uai("Esperava 'uai' após declaração")

    def decl_item(self) -> None:
        identificador = self.consumir(TokenType.IDENTIFIER, "Esperava identificador").lexema
        if self.match(TokenType.ASSIGN):
            valor = self.expr()
            self.gerador.adicionar("att", identificador, valor, None)

    def for_declaration(self) -> None:
        self.type_()
        self.decl_item()
        while self.match(TokenType.COMMA):
            self.decl_item()

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
        self.consumir_ponto_virgula_for("Esperava ';' como separador do for")

        if not self.verificar(TokenType.SEMICOLON):
            self.expr()
        self.consumir_ponto_virgula_for("Esperava ';' como separador do for")

        if not self.verificar(TokenType.RIGHT_PAREN):
            self.atrib()
        self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' ao final do for")

        self.stmt()

    def io_stmt(self) -> None:
        if self.match(TokenType.INPUT):
            self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após 'xove'")
            self.type_()
            self.consumir(TokenType.COMMA, "Esperava ',' em xove")
            identificador = self.consumir(TokenType.IDENTIFIER, "Esperava identificador em xove").lexema
            self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' em xove")
            self.consumir_uai("Esperava 'uai' após xove")
            self.gerador.adicionar("call", "read", identificador, None)
            return

        if self.match(TokenType.OUTPUT):
            self.consumir(TokenType.LEFT_PAREN, "Esperava '(' após 'oia_proce_ve'")
            valores = self.out_list()
            self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' em oia_proce_ve")
            self.consumir_uai("Esperava 'uai' após saída")

            for valor in valores:
                self.gerador.adicionar("call", "print", valor, None)
            return

        self.erro("Esperava comando de entrada ou saída")

    def out_list(self) -> list[str]:
        valores = [self.out()]
        while self.match(TokenType.COMMA):
            valores.append(self.out())
        return valores

    def out(self) -> str:
        return self.fator_zin()

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
                self.default_case()

    def corpo_case(self) -> None:
        while (
            self.inicio_de_stmt()
            and not self.verificar(TokenType.CASE)
            and not self.verificar(TokenType.DEFAULT)
            and not self.verificar(TokenType.END_BLOCK)
        ):
            self.stmt()

    def do_caso(self) -> None:
        self.consumir(TokenType.CASE, "Esperava 'du_casu'")
        self.fator_zin()
        self.consumir(TokenType.COLON, "Esperava ':' após valor do caso")
        self.corpo_case()

    def default_case(self) -> None:
        self.consumir(TokenType.DEFAULT, "Esperava 'uai_so'")
        self.consumir(TokenType.COLON, "Esperava ':' após uai_so")
        self.corpo_case()

   
    # expressoes

    def expr(self) -> str:
        return self.atrib()

    def atrib(self) -> str:
        esquerda = self.or_()

        if self.match(TokenType.ASSIGN):
            if not self.variavel_valida_para_atribuicao(esquerda):
                self.erro("Lado esquerdo da atribuição inválido")

            valor = self.atrib()
            self.gerador.adicionar("att", esquerda, valor, None)
            return esquerda

        return esquerda
    
    def variavel_valida_para_atribuicao(self, nome: str) -> bool:
        if not nome:
            return False
        if nome.startswith("t"):
            return True
        return nome.isidentifier()

    def or_(self) -> str:
        esquerda = self.xor()

        while self.match(TokenType.OR):
            direita = self.xor()
            temp = self.gerador.nova_temp()
            self.gerador.adicionar("or", temp, esquerda, direita)
            esquerda = temp

        return esquerda

    def xor(self) -> str:
        esquerda = self.and_()

        while self.match(TokenType.XOR):
            direita = self.and_()
            temp = self.gerador.nova_temp()
            self.gerador.adicionar("xor", temp, esquerda, direita)
            esquerda = temp

        return esquerda

    def and_(self) -> str:
        esquerda = self.not_()

        while self.match(TokenType.AND):
            direita = self.not_()
            temp = self.gerador.nova_temp()
            self.gerador.adicionar("and", temp, esquerda, direita)
            esquerda = temp

        return esquerda

    def not_(self) -> str:
        if self.match(TokenType.NOT):
            op1 = self.not_()
            temp = self.gerador.nova_temp()
            self.gerador.adicionar("not", temp, op1, None)
            return temp

        return self.rel()

    def rel(self) -> str:
        esquerda = self.add()

        while self.match(
            TokenType.EQUAL,
            TokenType.NOT_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ):
            operador_token = self.anterior().token
            direita = self.add()
            temp = self.gerador.nova_temp()

            mapa = {
                TokenType.EQUAL: "eq",
                TokenType.NOT_EQUAL: "dif",
                TokenType.LESS: "less",
                TokenType.LESS_EQUAL: "leq",
                TokenType.GREATER: "gret",
                TokenType.GREATER_EQUAL: "geq",
            }

            self.gerador.adicionar(mapa[operador_token], temp, esquerda, direita)
            esquerda = temp

        return esquerda

    def add(self) -> str:
        esquerda = self.mult()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            operador_token = self.anterior().token
            direita = self.mult()
            temp = self.gerador.nova_temp()

            mapa = {
                TokenType.PLUS: "add",
                TokenType.MINUS: "sub",
            }

            self.gerador.adicionar(mapa[operador_token], temp, esquerda, direita)
            esquerda = temp

        return esquerda

    def mult(self) -> str:
        esquerda = self.uno()

        while self.match(
            TokenType.MULTIPLY,
            TokenType.DIVIDE,
            TokenType.WHOLE_DIVISION,
            TokenType.MOD
        ):
            operador_token = self.anterior().token
            direita = self.uno()
            temp = self.gerador.nova_temp()

            mapa = {
                TokenType.MULTIPLY: "mult",
                TokenType.DIVIDE: "div",
                TokenType.WHOLE_DIVISION: "divI",
                TokenType.MOD: "mod",
            }

            self.gerador.adicionar(mapa[operador_token], temp, esquerda, direita)
            esquerda = temp

        return esquerda

    def uno(self) -> str:
        if self.match(TokenType.PLUS):
            op1 = self.uno()
            temp = self.gerador.nova_temp()
            self.gerador.adicionar("uno", temp, "+", op1)
            return temp

        if self.match(TokenType.MINUS):
            op1 = self.uno()
            temp = self.gerador.nova_temp()
            self.gerador.adicionar("uno", temp, "-", op1)
            return temp

        return self.fator_zao()

    def fator_zao(self) -> str:
        if self.match(TokenType.LEFT_PAREN):
            valor = self.atrib()
            self.consumir(TokenType.RIGHT_PAREN, "Esperava ')' após expressão")
            return valor
        else:
            return self.fator_zin()

    def fator_zin(self) -> str:
        if self.match(TokenType.LITERAL_STRING):
            return repr(self.anterior().lexema)

        if self.match(TokenType.IDENTIFIER):
            return self.anterior().lexema

        if self.match(TokenType.LITERAL_INT):
            return self.anterior().lexema

        if self.match(TokenType.LITERAL_FLOAT):
            return self.anterior().lexema

        if self.match(TokenType.TRUE):
            return self.anterior().lexema

        if self.match(TokenType.FALSE):
            return self.anterior().lexema

        if self.match(TokenType.LITERAL_CHAR):
            return repr(self.anterior().lexema)

        self.erro("Esperava literal, identificador ou expressão entre parênteses")