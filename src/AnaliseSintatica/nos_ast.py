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


@dataclass
class Block:
    statements: list[Statement]


@dataclass
class EmptyStmt:
    pass


@dataclass
class DeclarationItem:
    name: str
    initializer: Optional[Expression] = None


@dataclass
class Declaration:
    var_type: str
    items: list[DeclarationItem]


@dataclass
class AssignmentStmt:
    target: Identifier
    value: Expression


@dataclass
class ExpressionStmt:
    expression: Expression


@dataclass
class IfStmt:
    condition: Expression
    then_branch: Statement
    else_branch: Optional[Statement] = None


@dataclass
class WhileStmt:
    condition: Expression
    body: Statement


@dataclass
class ForStmt:
    init: Optional[Statement]
    condition: Optional[Expression]
    update: Optional[Expression]
    body: Statement


@dataclass
class SwitchCase:
    value: Expression
    statements: list[Statement]


@dataclass
class SwitchStmt:
    expression: Expression
    cases: list[SwitchCase]
    default_statements: list[Statement] | None = None


@dataclass
class InputStmt:
    var_type: str
    target: str


@dataclass
class OutputStmt:
    values: list[Expression]


@dataclass
class ReturnStmt:
    value: Expression


@dataclass
class BreakStmt:
    pass


@dataclass
class ContinueStmt:
    pass


@dataclass
class Literal:
    kind: str
    value: str


@dataclass
class Identifier:
    name: str


@dataclass
class UnaryExpr:
    operator: str
    operand: Expression


@dataclass
class BinaryExpr:
    operator: str
    left: Expression
    right: Expression


@dataclass
class AssignmentExpr:
    target: Identifier
    value: Expression


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
