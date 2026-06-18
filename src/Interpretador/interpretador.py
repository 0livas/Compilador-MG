from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from AnaliseSintatica.gerador_quadruplas import Quadruple


class RuntimeErrorMineires(Exception):
    def __init__(self, message: str, indice_instrucao: int | None = None):
        self.message = message
        self.indice_instrucao = indice_instrucao
        super().__init__(self.__str__())

    def __str__(self) -> str:
        if self.indice_instrucao is None:
            return f"Erro de Execução: {self.message}"
        return f"Erro de Execução na instrução {self.indice_instrucao}: {self.message}"


class Interpretador:
    def __init__(self) -> None:
        self.quadruplas: list[Quadruple] = []
        self.memoria: dict[str, Any] = {}
        self.labels: dict[str, int] = {}
        self.ip: int = 0
        self.valor_retorno: Any = None
        self.saidas: list[str] = []

    def executar(self, quadruplas: list[Quadruple]) -> Any:
        self._resetar(quadruplas)
        self._indexar_labels()
        self._posicionar_inicio()

        while 0 <= self.ip < len(self.quadruplas):
            quadrupla = self.quadruplas[self.ip]
            if self._executar_quadrupla(quadrupla):
                break

        return self.valor_retorno

    def _resetar(self, quadruplas: list[Quadruple]) -> None:
        self.quadruplas = quadruplas
        self.memoria = {}
        self.labels = {}
        self.ip = 0
        self.valor_retorno = None
        self.saidas = []

    def _indexar_labels(self) -> None:
        for indice, quadrupla in enumerate(self.quadruplas):
            if quadrupla.operacao == "label":
                self.labels[quadrupla.resultado] = indice

    def _posicionar_inicio(self) -> None:
        if "main" in self.labels:
            self.ip = self.labels["main"]
        else:
            self.ip = 0

    def _executar_quadrupla(self, quadrupla: Quadruple) -> bool:
        operacao = quadrupla.operacao

        if operacao == "label":
            self.ip += 1
            return False

        if operacao == "jump":
            self._saltar_para(quadrupla.resultado)
            return False

        if operacao == "if":
            condicao = self._resolver_operando(quadrupla.resultado)
            if self._coagir_bool(condicao):
                self._saltar_para(quadrupla.arg1)
            else:
                destino_falso = quadrupla.arg2
                if destino_falso != "null":
                    self._saltar_para(destino_falso)
                else:
                    self.ip += 1
            return False

        if operacao == "att":
            valor = self._resolver_operando(quadrupla.arg1)
            self.memoria[quadrupla.resultado] = valor
            self.ip += 1
            return False

        if operacao in {"add", "sub", "mult", "div", "divI", "mod",
                        "less", "leq", "gret", "geq", "eq", "dif",
                        "and", "or", "xor"}:
            self._executar_binaria(quadrupla)
            self.ip += 1
            return False

        if operacao == "not":
            valor = self._resolver_operando(quadrupla.arg1)
            self.memoria[quadrupla.resultado] = not self._coagir_bool(valor)
            self.ip += 1
            return False

        if operacao == "uno":
            sinal = quadrupla.arg1
            valor = self._resolver_operando(quadrupla.arg2)
            if sinal == "+":
                self.memoria[quadrupla.resultado] = +valor
            elif sinal == "-":
                self.memoria[quadrupla.resultado] = -valor
            else:
                raise RuntimeErrorMineires(f"Operador unário inválido: {sinal}", self.ip + 1)
            self.ip += 1
            return False

        if operacao == "call":
            self._executar_call(quadrupla)
            self.ip += 1
            return False

        if operacao == "ret":
            self.valor_retorno = self._resolver_operando(quadrupla.resultado)
            return True

        raise RuntimeErrorMineires(f"Operação não suportada: {operacao}", self.ip + 1)

    def _executar_binaria(self, quadrupla: Quadruple) -> None:
        esq = self._resolver_operando(quadrupla.arg1)
        dir = self._resolver_operando(quadrupla.arg2)
        op = quadrupla.operacao

        try:
            if op == "add":
                resultado = esq + dir
            elif op == "sub":
                resultado = esq - dir
            elif op == "mult":
                resultado = esq * dir
            elif op == "div":
                if dir == 0:
                    raise RuntimeErrorMineires("Divisão por zero.", self.ip + 1)
                resultado = esq / dir
            elif op == "divI":
                if dir == 0:
                    raise RuntimeErrorMineires("Divisão inteira por zero.", self.ip + 1)
                resultado = esq // dir
            elif op == "mod":
                if dir == 0:
                    raise RuntimeErrorMineires("Módulo por zero.", self.ip + 1)
                resultado = esq % dir
            elif op == "less":
                resultado = esq < dir
            elif op == "leq":
                resultado = esq <= dir
            elif op == "gret":
                resultado = esq > dir
            elif op == "geq":
                resultado = esq >= dir
            elif op == "eq":
                resultado = esq == dir
            elif op == "dif":
                resultado = esq != dir
            elif op == "and":
                resultado = self._coagir_bool(esq) and self._coagir_bool(dir)
            elif op == "or":
                resultado = self._coagir_bool(esq) or self._coagir_bool(dir)
            elif op == "xor":
                resultado = bool(self._coagir_bool(esq)) ^ bool(self._coagir_bool(dir))
            else:
                raise RuntimeErrorMineires(f"Operação binária não suportada: {op}", self.ip + 1)
        except TypeError as exc:
            raise RuntimeErrorMineires(f"Operação inválida '{op}' com operandos {esq!r} e {dir!r}.", self.ip + 1) from exc

        self.memoria[quadrupla.resultado] = resultado

    def _executar_call(self, quadrupla: Quadruple) -> None:
        funcao = quadrupla.resultado

        if funcao == "print":
            if quadrupla.arg1 != "null":
                valor = self._resolver_operando(quadrupla.arg1)
            else:
                valor = self._resolver_operando(quadrupla.arg2)

            texto = self._formatar_saida(valor)
            print(texto, end="")
            self.saidas.append(texto)
            return

        if funcao == "read":
            nome_variavel = quadrupla.arg1
            entrada = input()
            self.memoria[nome_variavel] = self._inferir_literal_entrada(entrada)
            return

        raise RuntimeErrorMineires(f"Call não suportado: {funcao}", self.ip + 1)

    def _saltar_para(self, label: str) -> None:
        if label not in self.labels:
            raise RuntimeErrorMineires(f"Label inexistente: {label}", self.ip + 1)
        self.ip = self.labels[label]

    def _resolver_operando(self, operando: str) -> Any:
        if operando == "null":
            return None

        if operando in self.memoria:
            return self.memoria[operando]

        if self._eh_string_literal(operando):
            return self._desserializar_string(operando[1:-1])

        if self._eh_char_literal(operando):
            return self._desserializar_string(operando[1:-1])

        if operando == "eh":
            return True
        if operando == "num_eh":
            return False

        if self._eh_inteiro(operando):
            return int(operando)

        if self._eh_float(operando):
            return float(operando)

        # Se não foi encontrado, tratamos como variável/temporário ausente.
        raise RuntimeErrorMineires(f"Operando '{operando}' não foi inicializado.", self.ip + 1)

    def _coagir_bool(self, valor: Any) -> bool:
        if isinstance(valor, bool):
            return valor
        if isinstance(valor, (int, float)):
            return valor != 0
        if isinstance(valor, str):
            if valor == "":
                return False
            return True
        return bool(valor)

    def _formatar_saida(self, valor: Any) -> str:
        if isinstance(valor, bool):
            return "eh" if valor else "num_eh"
        if valor is None:
            return "null"
        return str(valor)

    def _inferir_literal_entrada(self, texto: str) -> Any:
        texto = texto.strip()
        if texto == "eh":
            return True
        if texto == "num_eh":
            return False
        if self._eh_inteiro(texto):
            return int(texto)
        if self._eh_float(texto):
            return float(texto)
        return texto

    def _desserializar_string(self, texto_escapado: str) -> str:
        return bytes(texto_escapado, "utf-8").decode("unicode_escape")

    def _eh_string_literal(self, valor: str) -> bool:
        return len(valor) >= 2 and valor[0] == '"' and valor[-1] == '"'

    def _eh_char_literal(self, valor: str) -> bool:
        return len(valor) >= 2 and valor[0] == "'" and valor[-1] == "'"

    def _eh_inteiro(self, valor: str) -> bool:
        return valor.isdigit() or (valor.startswith("-") and valor[1:].isdigit())

    def _eh_float(self, valor: str) -> bool:
        if self._eh_inteiro(valor):
            return False
        try:
            float(valor)
            return True
        except ValueError:
            return False
