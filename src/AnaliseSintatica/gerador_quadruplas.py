from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from AnaliseSintatica.nos_ast import (
    AssignmentExpr,
    AssignmentStmt,
    BinaryExpr,
    Block,
    BreakStmt,
    ContinueStmt,
    Declaration,
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
    SwitchStmt,
    UnaryExpr,
    WhileStmt,
)

from AnaliseSemantica.analisador_semantico import AnalisadorSemantico, SemanticError


@dataclass
class Quadruple:
    operacao: str
    resultado: str = "null"
    arg1: str = "null"
    arg2: str = "null"

    def __str__(self) -> str:
        return f"({self.operacao}, {self.resultado}, {self.arg1}, {self.arg2})"


@dataclass
class _ContextoControle:
    break_label: str
    continue_label: Optional[str] = None


class GeradorQuadruplas:
    def __init__(self):
        self.quadruplas: list[Quadruple] = []
        self._temporario_atual = 0
        self._rotulo_atual = 0
        self._contextos: list[_ContextoControle] = []
        self.semantico = AnalisadorSemantico()

    def gerar(self, programa: Program) -> list[Quadruple]:
        self.quadruplas = []
        self._temporario_atual = 0
        self._rotulo_atual = 0
        self._contextos = []
        self.semantico = AnalisadorSemantico()

        for funcao in programa.functions:
            self._gerar_funcao(funcao)

        return self.quadruplas

    def formatar(self) -> str:
        linhas = []
        for indice, quadrupla in enumerate(self.quadruplas, start=1):
            linhas.append(f"{indice:03}: {quadrupla}")
        return "\n".join(linhas)

    def _gerar_funcao(self, funcao: FunctionDecl) -> None:
        self._emitir("label", funcao.name)
        # O corpo da função é um Block, que já gerencia o escopo
        self._gerar_stmt(funcao.body)

    def _gerar_stmt(self, stmt: Statement) -> None:
        if isinstance(stmt, EmptyStmt):
            return

        if isinstance(stmt, Block):
            self.semantico.entrar_escopo()
            for statement in stmt.statements:
                self._gerar_stmt(statement)
            self.semantico.sair_escopo()
            return

        if isinstance(stmt, Declaration):
            self._gerar_declaracao(stmt)
            return

        if isinstance(stmt, AssignmentStmt):
            valor, tipo_valor = self._gerar_expr(stmt.value)
            tipo_alvo = self.semantico.obter_tipo_variavel(stmt.target.name, getattr(stmt, 'linha', 0), getattr(stmt, 'coluna', 0))
            
            if tipo_alvo != tipo_valor:
                raise SemanticError(f"Atribuição inválida: não é possível atribuir {tipo_valor} para {tipo_alvo} ('{stmt.target.name}')", getattr(stmt, 'linha', 0), getattr(stmt, 'coluna', 0))
            
            self._emitir("att", stmt.target.name, valor)
            return

        if isinstance(stmt, ExpressionStmt):
            self._gerar_expr(stmt.expression)
            return

        if isinstance(stmt, InputStmt):
            self.semantico.declarar_variavel(stmt.target, stmt.var_type)
            self._emitir("call", "read", stmt.target, "null")
            return

        if isinstance(stmt, OutputStmt):
            for value in stmt.values:
                valor, _ = self._gerar_expr(value)
                if self._eh_textual(value):
                    self._emitir("call", "print", "null", valor)
                else:
                    self._emitir("call", "print", valor, "null")
            return

        if isinstance(stmt, ReturnStmt):
            valor, _ = self._gerar_expr(stmt.value)
            self._emitir("ret", valor)
            return

        if isinstance(stmt, BreakStmt):
            self._emitir("jump", self._break_label())
            return

        if isinstance(stmt, ContinueStmt):
            self._emitir("jump", self._continue_label())
            return

        if isinstance(stmt, IfStmt):
            self._gerar_if(stmt)
            return

        if isinstance(stmt, WhileStmt):
            self._gerar_while(stmt)
            return

        if isinstance(stmt, ForStmt):
            self._gerar_for(stmt)
            return

        if isinstance(stmt, SwitchStmt):
            self._gerar_switch(stmt)
            return

        raise TypeError(f"Tipo de statement não suportado: {type(stmt)!r}")

    def _gerar_declaracao(self, declaracao: Declaration) -> None:
        for item in declaracao.items:
            self.semantico.declarar_variavel(item.name, declaracao.var_type, getattr(item, 'linha', 0), getattr(item, 'coluna', 0))
            if item.initializer is not None:
                valor, tipo_valor = self._gerar_expr(item.initializer)
                tipo_var = self.semantico.obter_tipo_variavel(item.name, getattr(item, 'linha', 0), getattr(item, 'coluna', 0))
                
                if tipo_var != tipo_valor:
                    raise SemanticError(f"Inicialização inválida: variável '{item.name}' é {tipo_var} mas recebeu {tipo_valor}", getattr(item, 'linha', 0), getattr(item, 'coluna', 0))
                
                self._emitir("att", item.name, valor)

    def _gerar_if(self, stmt: IfStmt) -> None:
        then_label = self._novo_rotulo()
        else_label = self._novo_rotulo()
        end_label = self._novo_rotulo() if stmt.else_branch is not None else else_label

        condicao, tipo_cond = self._gerar_expr(stmt.condition)
        if tipo_cond != "BOOL":
            raise SemanticError(f"Condição do 'uai_se' deve ser BOOL, não {tipo_cond}", getattr(stmt, 'linha', 0), getattr(stmt, 'coluna', 0))

        self._emitir("if", condicao, then_label, else_label)
        self._emitir("label", then_label)
        self._gerar_stmt(stmt.then_branch)

        if stmt.else_branch is not None:
            self._emitir("jump", end_label)
            self._emitir("label", else_label)
            self._gerar_stmt(stmt.else_branch)
            self._emitir("label", end_label)
        else:
            self._emitir("label", else_label)

    def _gerar_while(self, stmt: WhileStmt) -> None:
        inicio_label = self._novo_rotulo()
        corpo_label = self._novo_rotulo()
        fim_label = self._novo_rotulo()

        self._emitir("label", inicio_label)
        condicao, tipo_cond = self._gerar_expr(stmt.condition)
        if tipo_cond != "BOOL":
             raise SemanticError(f"Condição do 'enquanto_tiver_trem' deve ser BOOL, não {tipo_cond}", getattr(stmt, 'linha', 0), getattr(stmt, 'coluna', 0))

        self._emitir("if", condicao, corpo_label, fim_label)
        self._emitir("label", corpo_label)

        self._contextos.append(_ContextoControle(break_label=fim_label, continue_label=inicio_label))
        self._gerar_stmt(stmt.body)
        self._contextos.pop()

        self._emitir("jump", inicio_label)
        self._emitir("label", fim_label)

    def _gerar_for(self, stmt: ForStmt) -> None:
        self.semantico.entrar_escopo()
        
        if stmt.init is not None:
            self._gerar_stmt(stmt.init)

        teste_label = self._novo_rotulo()
        corpo_label = self._novo_rotulo()
        update_label = self._novo_rotulo()
        fim_label = self._novo_rotulo()

        self._emitir("label", teste_label)
        if stmt.condition is not None:
            condicao, tipo_cond = self._gerar_expr(stmt.condition)
            if tipo_cond != "BOOL":
                raise SemanticError(f"Condição do 'roda_esse_trem' deve ser BOOL, não {tipo_cond}", getattr(stmt, 'linha', 0), getattr(stmt, 'coluna', 0))
            self._emitir("if", condicao, corpo_label, fim_label)
        else:
            self._emitir("jump", corpo_label)

        self._emitir("label", corpo_label)
        self._contextos.append(_ContextoControle(break_label=fim_label, continue_label=update_label))
        self._gerar_stmt(stmt.body)
        self._contextos.pop()

        self._emitir("label", update_label)
        if stmt.update is not None:
            self._gerar_expr(stmt.update)
        self._emitir("jump", teste_label)
        self._emitir("label", fim_label)
        
        self.semantico.sair_escopo()

    def _gerar_switch(self, stmt: SwitchStmt) -> None:
        valor_switch, tipo_switch = self._gerar_expr(stmt.expression)
        fim_label = self._novo_rotulo()
        case_labels = [self._novo_rotulo() for _ in stmt.cases]
        default_label = self._novo_rotulo() if stmt.default_statements is not None else fim_label

        for case, case_label in zip(stmt.cases, case_labels):
            valor_caso, tipo_caso = self._gerar_expr(case.value)
            if tipo_switch != tipo_caso:
                raise SemanticError(f"Tipo do case ({tipo_caso}) incompatível com o switch ({tipo_switch})", getattr(stmt, 'linha', 0), getattr(stmt, 'coluna', 0))
                
            comparacao = self._novo_temporario()
            self._emitir("eq", comparacao, valor_switch, valor_caso)
            self._emitir("if", comparacao, case_label, "null")

        self._emitir("jump", default_label)

        for case, case_label in zip(stmt.cases, case_labels):
            self._emitir("label", case_label)
            self.semantico.entrar_escopo()
            self._contextos.append(_ContextoControle(break_label=fim_label))
            for statement in case.statements:
                self._gerar_stmt(statement)
            self._contextos.pop()
            self.semantico.sair_escopo()
            if not self._termina_em_fluxo_saida(case.statements):
                self._emitir("jump", fim_label)

        if stmt.default_statements is not None:
            self._emitir("label", default_label)
            self.semantico.entrar_escopo()
            self._contextos.append(_ContextoControle(break_label=fim_label))
            for statement in stmt.default_statements:
                self._gerar_stmt(statement)
            self._contextos.pop()
            self.semantico.sair_escopo()
            if not self._termina_em_fluxo_saida(stmt.default_statements):
                self._emitir("jump", fim_label)

        self._emitir("label", fim_label)

    def _gerar_expr(self, expression: Expression) -> Tuple[str, str]:
        if isinstance(expression, Literal):
            valor_conv, tipo = self.semantico.converter_e_obter_tipo_literal(expression)
            if tipo in ["STRING", "CHAR"]:
                 return self._formatar_literal_valor(tipo, valor_conv), tipo
            return valor_conv, tipo

        if isinstance(expression, Identifier):
            tipo = self.semantico.obter_tipo_variavel(expression.name, getattr(expression, 'linha', 0), getattr(expression, 'coluna', 0))
            return expression.name, tipo

        if isinstance(expression, AssignmentExpr):
            valor, tipo_valor = self._gerar_expr(expression.value)
            tipo_alvo = self.semantico.obter_tipo_variavel(expression.target.name, getattr(expression, 'linha', 0), getattr(expression, 'coluna', 0))
            
            if tipo_alvo != tipo_valor:
                raise SemanticError(f"Atribuição inválida na expressão: não é possível atribuir {tipo_valor} para {tipo_alvo} ('{expression.target.name}')", getattr(expression, 'linha', 0), getattr(expression, 'coluna', 0))
                
            self._emitir("att", expression.target.name, valor)
            return expression.target.name, tipo_alvo

        if isinstance(expression, UnaryExpr):
            operando, tipo_op = self._gerar_expr(expression.operand)
            tipo_result = self.semantico.validar_operacao_unaria(expression.operator, tipo_op, getattr(expression, 'linha', 0), getattr(expression, 'coluna', 0))
            
            temp = self._novo_temporario()
            if expression.operator == "PLUS":
                self._emitir("uno", temp, "+", operando)
            elif expression.operator == "MINUS":
                self._emitir("uno", temp, "-", operando)
            elif expression.operator == "NOT":
                self._emitir("not", temp, operando)
            else:
                raise TypeError(f"Operador unário não suportado: {expression.operator}")
            return temp, tipo_result

        if isinstance(expression, BinaryExpr):
            esquerdo, tipo_esq = self._gerar_expr(expression.left)
            direito, tipo_dir = self._gerar_expr(expression.right)
            
            tipo_result = self.semantico.validar_operacao_binaria(expression.operator, tipo_esq, tipo_dir, getattr(expression, 'linha', 0), getattr(expression, 'coluna', 0))
            
            operador = self._mapear_operador_binario(expression.operator)
            temporario = self._novo_temporario()
            self._emitir(operador, temporario, esquerdo, direito)
            return temporario, tipo_result

        raise TypeError(f"Tipo de expressão não suportado: {type(expression)!r}")

    def _mapear_operador_binario(self, operador: str) -> str:
        mapa = {
            "PLUS": "add",
            "MINUS": "sub",
            "MULTIPLY": "mult",
            "DIVIDE": "div",
            "WHOLE_DIVISION": "divI",
            "MOD": "mod",
            "LESS": "less",
            "LESS_EQUAL": "leq",
            "GREATER": "gret",
            "GREATER_EQUAL": "geq",
            "EQUAL": "eq",
            "NOT_EQUAL": "dif",
            "AND": "and",
            "OR": "or",
            "XOR": "xor",
        }
        if operador not in mapa:
            raise TypeError(f"Operador binário não suportado: {operador}")
        return mapa[operador]

    def _eh_textual(self, expression: Expression) -> bool:
        if isinstance(expression, Literal):
            return expression.kind in {"LITERAL_STRING", "LITERAL_CHAR"}
        return False

    def _formatar_literal_valor(self, tipo: str, valor: str) -> str:
        if tipo == "STRING":
            texto = valor.encode("unicode_escape").decode("ascii")
            return f'"{texto}"'
        if tipo == "CHAR":
            texto = valor.encode("unicode_escape").decode("ascii")
            return f"'{texto}'"
        return valor

    def _emitir(self, operacao: str, resultado: str = "null", arg1: str = "null", arg2: str = "null") -> None:
        self.quadruplas.append(Quadruple(operacao, resultado, arg1, arg2))

    def _novo_temporario(self) -> str:
        self._temporario_atual += 1
        return f"t{self._temporario_atual}"

    def _novo_rotulo(self) -> str:
        self._rotulo_atual += 1
        return f"L{self._rotulo_atual}"

    def _break_label(self) -> str:
        for contexto in reversed(self._contextos):
            if contexto.break_label:
                return contexto.break_label
        raise RuntimeError("'para_o_trem' fora de uma estrutura que permita break")

    def _continue_label(self) -> str:
        for contexto in reversed(self._contextos):
            if contexto.continue_label is not None:
                return contexto.continue_label
        raise RuntimeError("'toca_o_trem' fora de um laço")

    def _termina_em_fluxo_saida(self, statements: list[Statement]) -> bool:
        if not statements:
            return False

        ultimo = statements[-1]
        return isinstance(ultimo, (BreakStmt, ReturnStmt, ContinueStmt))
