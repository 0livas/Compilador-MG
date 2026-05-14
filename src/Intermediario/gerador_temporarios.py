class GeradorTemporarios:
    def __init__(self) -> None:
        self.contador = 0

    def nova_temp(self) -> str:
        self.contador += 1
        return f"t{self.contador}"

    def resetar(self) -> None:
        self.contador = 0