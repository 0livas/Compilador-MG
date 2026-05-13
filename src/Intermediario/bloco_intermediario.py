from dataclasses import dataclass

@dataclass
class BlocoIntermediario:
    operador: str
    resultado: str | None
    arg1: str | None
    arg2: str | None

    def __str__(self) -> str:
        return f"({self.operador}, {self.resultado}, {self.arg1}, {self.arg2})"