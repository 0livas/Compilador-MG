from Intermediario.bloco_intermediario import BlocoIntermediario
from Intermediario.gerador_temporarios import GeradorTemporarios


class GeradorIntermediario:
    def __init__(self) -> None:
        self.blocos: list[BlocoIntermediario] = []
        self.temporarios = GeradorTemporarios()

    def adicionar(self, operador: str, resultado, arg1, arg2) -> None:
        self.blocos.append(BlocoIntermediario(operador, resultado, arg1, arg2))

    def nova_temp(self) -> str:
        return self.temporarios.nova_temp()

    def limpar(self) -> None:
        self.blocos.clear()
        self.temporarios.resetar()

    def imprimir(self) -> None:
        for bloco in self.blocos:
            print(bloco)