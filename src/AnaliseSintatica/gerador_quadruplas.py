from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .nos_ast import (
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
    SwitchCase,
    SwitchStmt,
    UnaryExpr,
    WhileStmt,
)


@dataclass
class Quadruple:
    operacao: str
    arg1: str = "-"
    arg2: str = "-"
    resultado: str = "-"

    def __str__(self) -> str:
        return f"({self.operacao}, {self.arg1}, {self.arg2}, {self.resultado})"


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

    def gerar(self, programa: Program) -> list[Quadruple]:
        self.quadruplas = []
        self._temporario_atual = 0
        self._rotulo_atual = 0
        self._contextos = []

        for funcao in programa.functions:
            self._gerar_funcao(funcao)

        return self.quadruplas

    def formatar(self) -> str:
        linhas = []
        for indice, quadrupla in enumerate(self.quadruplas, start=1):
            linhas.append(f"{indice:03}: {quadrupla}")
        return "\n".join(linhas)

    def _gerar_funcao(self, funcao: FunctionDecl) -> None:
        self._emitir("FUNC", funcao.name)
        self._gerar_stmt(funcao.body)
        self._emitir("END_FUNC", funcao.name)

    def _gerar_stmt(self, stmt: Statement) -> None:
        if isinstance(stmt, EmptyStmt):
            return

        if isinstance(stmt, Block):
            for statement in stmt.statements:
                self._gerar_stmt(statement)
            return

        if isinstance(stmt, Declaration):
            self._gerar_declaracao(stmt)
            return

        if isinstance(stmt, AssignmentStmt):
            valor = self._gerar_expr(stmt.value)
            self._emitir("ASSIGN", valor, "-", stmt.target.name)
            return

        if isinstance(stmt, ExpressionStmt):
            self._gerar_expr(stmt.expression)
            return

        if isinstance(stmt, InputStmt):
            self._emitir("INPUT", stmt.var_type or "-", "-", stmt.target)
            return

        if isinstance(stmt, OutputStmt):
            for value in stmt.values:
                self._emitir("OUTPUT", self._gerar_expr(value))
            return

        if isinstance(stmt, ReturnStmt):
            self._emitir("RETURN", self._gerar_expr(stmt.value))
            return

        if isinstance(stmt, BreakStmt):
            self._emitir("GOTO", "-", "-", self._break_label())
            return

        if isinstance(stmt, ContinueStmt):
            self._emitir("GOTO", "-", "-", self._continue_label())
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
            self._emitir("DECL", declaracao.var_type, "-", item.name)
            if item.initializer is not None:
                valor = self._gerar_expr(item.initializer)
                self._emitir("ASSIGN", valor, "-", item.name)

    def _gerar_if(self, stmt: IfStmt) -> None:
        else_label = self._novo_rotulo()
        end_label = self._novo_rotulo() if stmt.else_branch is not None else else_label

        condicao = self._gerar_expr(stmt.condition)
        self._emitir("IFFALSE", condicao, "-", else_label)
        self._gerar_stmt(stmt.then_branch)

        if stmt.else_branch is not None:
            self._emitir("GOTO", "-", "-", end_label)
            self._emitir("LABEL", "-", "-", else_label)
            self._gerar_stmt(stmt.else_branch)
            self._emitir("LABEL", "-", "-", end_label)
        else:
            self._emitir("LABEL", "-", "-", else_label)

    def _gerar_while(self, stmt: WhileStmt) -> None:
        inicio_label = self._novo_rotulo()
        fim_label = self._novo_rotulo()

        self._emitir("LABEL", "-", "-", inicio_label)
        condicao = self._gerar_expr(stmt.condition)
        self._emitir("IFFALSE", condicao, "-", fim_label)

        self._contextos.append(_ContextoControle(break_label=fim_label, continue_label=inicio_label))
        self._gerar_stmt(stmt.body)
        self._contextos.pop()

        self._emitir("GOTO", "-", "-", inicio_label)
        self._emitir("LABEL", "-", "-", fim_label)

    def _gerar_for(self, stmt: ForStmt) -> None:
        if stmt.init is not None:
            self._gerar_stmt(stmt.init)

        inicio_label = self._novo_rotulo()
        update_label = self._novo_rotulo()
        fim_label = self._novo_rotulo()

        self._emitir("LABEL", "-", "-", inicio_label)
        if stmt.condition is not None:
            condicao = self._gerar_expr(stmt.condition)
            self._emitir("IFFALSE", condicao, "-", fim_label)

        self._contextos.append(_ContextoControle(break_label=fim_label, continue_label=update_label))
        self._gerar_stmt(stmt.body)
        self._contextos.pop()

        self._emitir("LABEL", "-", "-", update_label)
        if stmt.update is not None:
            self._gerar_expr(stmt.update)
        self._emitir("GOTO", "-", "-", inicio_label)
        self._emitir("LABEL", "-", "-", fim_label)

    def _gerar_switch(self, stmt: SwitchStmt) -> None:
        valor_switch = self._gerar_expr(stmt.expression)
        fim_label = self._novo_rotulo()
        case_labels = [self._novo_rotulo() for _ in stmt.cases]
        default_label = self._novo_rotulo() if stmt.default_statements is not None else fim_label

        for case, case_label in zip(stmt.cases, case_labels):
            valor_caso = self._gerar_expr(case.value)
            comparacao = self._novo_temporario()
            self._emitir("EQ", valor_switch, valor_caso, comparacao)
            self._emitir("IFTRUE", comparacao, "-", case_label)

        self._emitir("GOTO", "-", "-", default_label)

        for case, case_label in zip(stmt.cases, case_labels):
            self._emitir("LABEL", "-", "-", case_label)
            self._contextos.append(_ContextoControle(break_label=fim_label))
            for statement in case.statements:
                self._gerar_stmt(statement)
            self._contextos.pop()
            if not self._termina_em_fluxo_saida(case.statements):
                self._emitir("GOTO", "-", "-", fim_label)

        if stmt.default_statements is not None:
            self._emitir("LABEL", "-", "-", default_label)
            self._contextos.append(_ContextoControle(break_label=fim_label))
            for statement in stmt.default_statements:
                self._gerar_stmt(statement)
            self._contextos.pop()
            if not self._termina_em_fluxo_saida(stmt.default_statements):
                self._emitir("GOTO", "-", "-", fim_label)

        self._emitir("LABEL", "-", "-", fim_label)

    def _gerar_expr(self, expression: Expression) -> str:
        if isinstance(expression, Literal):
            return self._formatar_literal(expression)

        if isinstance(expression, Identifier):
            return expression.name

        if isinstance(expression, AssignmentExpr):
            valor = self._gerar_expr(expression.value)
            self._emitir("ASSIGN", valor, "-", expression.target.name)
            return expression.target.name

        if isinstance(expression, UnaryExpr):
            operando = self._gerar_expr(expression.operand)
            if expression.operator == "PLUS":
                return operando

            operador = {"MINUS": "NEG", "NOT": "NOT"}.get(expression.operator)
            if operador is None:
                raise TypeError(f"Operador unário não suportado: {expression.operator}")

            temporario = self._novo_temporario()
            self._emitir(operador, operando, "-", temporario)
            return temporario

        if isinstance(expression, BinaryExpr):
            esquerdo = self._gerar_expr(expression.left)
            direito = self._gerar_expr(expression.right)
            operador = self._mapear_operador_binario(expression.operator)
            temporario = self._novo_temporario()
            self._emitir(operador, esquerdo, direito, temporario)
            return temporario

        raise TypeError(f"Tipo de expressão não suportado: {type(expression)!r}")

    def _mapear_operador_binario(self, operador: str) -> str:
        mapa = {
            "PLUS": "ADD",
            "MINUS": "SUB",
            "MULTIPLY": "MUL",
            "DIVIDE": "DIV",
            "MOD": "MOD",
            "LESS": "LT",
            "LESS_EQUAL": "LE",
            "GREATER": "GT",
            "GREATER_EQUAL": "GE",
            "EQUAL": "EQ",
            "NOT_EQUAL": "NE",
            "AND": "AND",
            "OR": "OR",
            "XOR": "XOR",
        }
        if operador not in mapa:
            raise TypeError(f"Operador binário não suportado: {operador}")
        return mapa[operador]

    def _formatar_literal(self, literal: Literal) -> str:
        if literal.kind == "LITERAL_STRING":
            texto = literal.value.encode("unicode_escape").decode("ascii")
            return f'"{texto}"'
        if literal.kind == "LITERAL_CHAR":
            texto = literal.value.encode("unicode_escape").decode("ascii")
            return f"'{texto}'"
        return literal.value

    def _emitir(self, operacao: str, arg1: str = "-", arg2: str = "-", resultado: str = "-") -> None:
        self.quadruplas.append(Quadruple(operacao, arg1, arg2, resultado))

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
