from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Program:
    functions: list[FunctionDecl]


@dataclass
class FunctionDecl:
    name: str
    body: Block
    linha: int = 0
    coluna: int = 0


@dataclass
class Block:
    statements: list[Statement]
    linha: int = 0
    coluna: int = 0


@dataclass
class EmptyStmt:
    linha: int = 0
    coluna: int = 0


@dataclass
class DeclarationItem:
    name: str
    initializer: Optional[Expression] = None
    linha: int = 0
    coluna: int = 0


@dataclass
class Declaration:
    var_type: str
    items: list[DeclarationItem]
    linha: int = 0
    coluna: int = 0


@dataclass
class AssignmentStmt:
    target: Identifier
    value: Expression
    linha: int = 0
    coluna: int = 0


@dataclass
class ExpressionStmt:
    expression: Expression
    linha: int = 0
    coluna: int = 0


@dataclass
class IfStmt:
    condition: Expression
    then_branch: Statement
    else_branch: Optional[Statement] = None
    linha: int = 0
    coluna: int = 0


@dataclass
class WhileStmt:
    condition: Expression
    body: Statement
    linha: int = 0
    coluna: int = 0


@dataclass
class ForStmt:
    init: Optional[Statement]
    condition: Optional[Expression]
    update: Optional[Expression]
    body: Statement
    linha: int = 0
    coluna: int = 0


@dataclass
class SwitchCase:
    value: Expression
    statements: list[Statement]
    linha: int = 0
    coluna: int = 0


@dataclass
class SwitchStmt:
    expression: Expression
    cases: list[SwitchCase]
    default_statements: list[Statement] | None = None
    linha: int = 0
    coluna: int = 0


@dataclass
class InputStmt:
    var_type: str
    target: str
    linha: int = 0
    coluna: int = 0


@dataclass
class OutputStmt:
    values: list[Expression]
    linha: int = 0
    coluna: int = 0


@dataclass
class ReturnStmt:
    value: Expression
    linha: int = 0
    coluna: int = 0


@dataclass
class BreakStmt:
    linha: int = 0
    coluna: int = 0


@dataclass
class ContinueStmt:
    linha: int = 0
    coluna: int = 0


@dataclass
class Literal:
    kind: str
    value: str
    linha: int = 0
    coluna: int = 0


@dataclass
class Identifier:
    name: str
    linha: int = 0
    coluna: int = 0


@dataclass
class UnaryExpr:
    operator: str
    operand: Expression
    linha: int = 0
    coluna: int = 0


@dataclass
class BinaryExpr:
    operator: str
    left: Expression
    right: Expression
    linha: int = 0
    coluna: int = 0


@dataclass
class AssignmentExpr:
    target: Identifier
    value: Expression
    linha: int = 0
    coluna: int = 0


Statement = (
    EmptyStmt
    | Declaration
    | AssignmentStmt
    | ExpressionStmt
    | IfStmt
    | WhileStmt
    | ForStmt
    | SwitchStmt
    | Block
    | InputStmt
    | OutputStmt
    | ReturnStmt
    | BreakStmt
    | ContinueStmt
)

Expression = Literal | Identifier | UnaryExpr | BinaryExpr | AssignmentExpr
