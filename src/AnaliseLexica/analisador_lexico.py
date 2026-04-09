from pathlib import Path
from .mineires_token import Token
from .tokenType import TokenType
from .gerenciador_tokens import GerenciadorTokens
from .validadores_numericos import ValidadorNumerico
from .gerenciador_erros import GerenciadorErros

class AnalisadorLexico:
    """Realizador da análise léxica. Lê código-fonte e produz tokens.
    
    Coordena todos os componentes:
    - GerenciadorTokens: classficação de palavras-chave e símbolos
    - ValidadorNumerico: validação de números
    - GerenciadorErros: registro de erros com contexto
    - Processadores especializados: strings, números, identificadores, etc
    """

    def __init__(self):
        self.gerenciador_tokens = GerenciadorTokens()
        self.validador_numerico = ValidadorNumerico()
        self.gerenciador_erros = GerenciadorErros()

        self.tokens: list[Token] = []
        self.codigo: str = ""
        self.linha_atual: int = 1
        self.coluna_atual: int = 0
        self.posicao: int = 0

    def analisar_arquivo(self, caminho_arquivo: str) -> tuple[list[Token], GerenciadorErros]:
        """Analisa um arquivo com código Minerês."""
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
                self.codigo = arquivo.read()
        except FileNotFoundError:
            self.gerenciador_erros.registrar_erro_customizado(
                tipo="arquivo não encontrado",
                mensagem=f"Arquivo '{caminho_arquivo}' não foi encontrado",
                linha=0,
                coluna=0,
            )
            return [], self.gerenciador_erros
        except IOError as e:
            self.gerenciador_erros.registrar_erro_customizado(
                tipo="erro ao ler arquivo",
                mensagem=f"Erro ao ler arquivo: {str(e)}",
                linha=0,
                coluna=0,
            )
            return [], self.gerenciador_erros

        self.tokens = []
        self.gerenciador_erros.limpar()
        self.linha_atual = 1
        self.coluna_atual = 0
        self.posicao = 0

        self._analisar()

        self.tokens.append(
            Token(
                lexema="",
                token=TokenType.EOF,
                linha=self.linha_atual,
                coluna=self.coluna_atual,
            )
        )

        return self.tokens, self.gerenciador_erros

    def analisar_codigo(self, codigo: str) -> tuple[list[Token], GerenciadorErros]:
        """Analisa string com código Minerês."""
    
        self.codigo = codigo
        self.tokens = []
        self.gerenciador_erros.limpar()
        self.linha_atual = 1
        self.coluna_atual = 0
        self.posicao = 0

        self._analisar()

        self.tokens.append(
            Token(
                lexema="",
                token=TokenType.EOF,
                linha=self.linha_atual,
                coluna=self.coluna_atual,
            )
        )

        return self.tokens, self.gerenciador_erros

    def _analisar(self) -> None:
        """Loop principal que tokeniza o código-fonte."""
    
        while self.posicao < len(self.codigo):
            char = self.codigo[self.posicao]

            if char == "\n":
                self.linha_atual += 1
                self.coluna_atual = 0
                self.posicao += 1
                continue

            if self.gerenciador_tokens.eh_espaco_em_branco(char):
                self._processar_espaco_em_branco(char)
                continue

            if char == '"':
                self._processar_string()
                continue

            if char == "'":
                self._processar_caractere_literal()
                continue

            if char == "/" and self.posicao + 1 < len(self.codigo):
                proximo_char = self.codigo[self.posicao + 1]
                if proximo_char == "/":
                    self._processar_comentario_linha()
                    continue

            if self.validador_numerico.eh_inicio_numero(char):
                if char == ".":
                    if self.posicao + 1 < len(self.codigo) and self.codigo[self.posicao + 1].isdigit():
                        self._processar_numero()
                        continue
                else:
                    self._processar_numero()
                    continue

            if char.isalpha() or char == "_":
                self._processar_identificador()
                continue

            if self.gerenciador_tokens.eh_delimitador(char):
                self._processar_operador()
                continue

            self.gerenciador_erros.registrar_caractere_invalido(
                char, self.linha_atual, self.coluna_atual
            )
            self.posicao += 1
            self.coluna_atual += 1

    def _processar_espaco_em_branco(self, char: str) -> None:
        """Ignora espaços em branco e atualiza contadores."""
    
        if char == "\t":
            self.coluna_atual += 4
        else:
            self.coluna_atual += 1

        self.posicao += 1

    def _processar_string(self) -> None:
        """Processa string com aspas duplas e escapes."""
    
        coluna_inicio = self.coluna_atual
        linha_inicio = self.linha_atual
        self.posicao += 1
        self.coluna_atual += 1

        lexema = ""

        while self.posicao < len(self.codigo):
            char = self.codigo[self.posicao]

            if char == "\n":
                self.gerenciador_erros.registrar_string_nao_fechada(
                    linha_inicio, coluna_inicio, self.linha_atual
                )
                self.linha_atual += 1
                self.coluna_atual = 0
                self.posicao += 1
                return

            if char == "\\":
                if self.posicao + 1 < len(self.codigo):
                    proximo = self.codigo[self.posicao + 1]
                    if proximo in "ntr\\'\"":
                        escape_map = {
                            "n": "\n",
                            "t": "\t",
                            "r": "\r",
                            "\\": "\\",
                            "'": "'",
                            '"': '"',
                        }
                        lexema += escape_map[proximo]
                        self.posicao += 2
                        self.coluna_atual += 2
                        continue

            if char == '"':
                self.posicao += 1
                self.coluna_atual += 1

                self.tokens.append(
                    Token(
                        lexema=lexema,
                        token=TokenType.LITERAL_STRING,
                        linha=linha_inicio,
                        coluna=coluna_inicio,
                    )
                )
                return

            lexema += char
            self.posicao += 1
            self.coluna_atual += 1

        self.gerenciador_erros.registrar_string_nao_fechada(
            linha_inicio, coluna_inicio, self.linha_atual
        )

    def _processar_caractere_literal(self) -> None:
        """Processa caractere com apóstrofos."""
    
        coluna_inicio = self.coluna_atual
        linha_inicio = self.linha_atual
        self.posicao += 1
        self.coluna_atual += 1

        if self.posicao >= len(self.codigo):
            self.gerenciador_erros.registrar_char_nao_fechado(
                linha_inicio, coluna_inicio, ""
            )
            return

        char = self.codigo[self.posicao]

        if char == "\n":
            self.gerenciador_erros.registrar_char_nao_fechado(
                self.linha_atual, self.coluna_atual, ""
            )
            self.linha_atual += 1
            self.coluna_atual = 0
            self.posicao += 1
            return

        lexema = ""

        if char == "\\":
            if self.posicao + 1 < len(self.codigo):
                proximo = self.codigo[self.posicao + 1]
                if proximo in "ntr\\'\"":
                    escape_map = {
                        "n": "\n",
                        "t": "\t",
                        "r": "\r",
                        "\\": "\\",
                        "'": "'",
                        '"': '"',
                    }
                    lexema = escape_map[proximo]
                    self.posicao += 2
                    self.coluna_atual += 2
                else:
                    self.gerenciador_erros.registrar_char_nao_fechado(
                        self.linha_atual, self.coluna_atual, "\\"
                    )
                    return
            else:
                self.gerenciador_erros.registrar_char_nao_fechado(
                    self.linha_atual, self.coluna_atual, "\\"
                )
                return
        else:
            lexema = char
            self.posicao += 1
            self.coluna_atual += 1

        if self.posicao < len(self.codigo) and self.codigo[self.posicao] == "'":
            self.posicao += 1
            self.coluna_atual += 1
            self.tokens.append(
                Token(
                    lexema=lexema,
                    token=TokenType.LITERAL_CHAR,
                    linha=linha_inicio,
                    coluna=coluna_inicio,
                )
            )
            return

        self.gerenciador_erros.registrar_char_nao_fechado(
            self.linha_atual, self.coluna_atual, lexema
        )

    def _processar_numero(self) -> None:
        """Processa número em múltiplas bases."""
    
        coluna_inicio = self.coluna_atual
        linha_inicio = self.linha_atual

        lexema = self._extrair_lexema_numero()

        eh_valido, tipo_numero = self.validador_numerico.validar_numero(lexema)

        if not eh_valido:
            self.gerenciador_erros.registrar_numero_invalido(
                lexema,
                linha_inicio,
                coluna_inicio,
                "sequência numérica inválida",
            )
            return

        token_type = self.validador_numerico.converter_para_token_type(tipo_numero)

        self.tokens.append(
            Token(
                lexema=lexema,
                token=token_type,
                linha=linha_inicio,
                coluna=coluna_inicio,
            )
        )

    def _extrair_lexema_numero(self) -> str:
    
        lexema = ""

        if self.posicao < len(self.codigo) and self.codigo[self.posicao] == ".":
            lexema += "."
            self.posicao += 1
            self.coluna_atual += 1

            while self.posicao < len(self.codigo) and self.codigo[self.posicao].isdigit():
                lexema += self.codigo[self.posicao]
                self.posicao += 1
                self.coluna_atual += 1

            return lexema

        if self.posicao < len(self.codigo) and self.codigo[self.posicao] == "0":
            lexema += "0"
            self.posicao += 1
            self.coluna_atual += 1

            if self.posicao < len(self.codigo) and self.codigo[self.posicao] in "xX":
                lexema += self.codigo[self.posicao]
                self.posicao += 1
                self.coluna_atual += 1

                while self.posicao < len(self.codigo):
                    char = self.codigo[self.posicao]
                    if not (char.isdigit() or char in "abcdefABCDEF"):
                        break
                    lexema += char
                    self.posicao += 1
                    self.coluna_atual += 1

                return lexema

            while self.posicao < len(self.codigo) and self.codigo[self.posicao].isdigit():
                lexema += self.codigo[self.posicao]
                self.posicao += 1
                self.coluna_atual += 1

            if self.posicao < len(self.codigo) and self.codigo[self.posicao] == ".":
                lexema += "."
                self.posicao += 1
                self.coluna_atual += 1

                while self.posicao < len(self.codigo) and self.codigo[self.posicao].isdigit():
                    lexema += self.codigo[self.posicao]
                    self.posicao += 1
                    self.coluna_atual += 1

            return lexema

        while self.posicao < len(self.codigo) and self.codigo[self.posicao].isdigit():
            lexema += self.codigo[self.posicao]
            self.posicao += 1
            self.coluna_atual += 1

        if self.posicao < len(self.codigo) and self.codigo[self.posicao] == ".":
            lexema += "."
            self.posicao += 1
            self.coluna_atual += 1

            while self.posicao < len(self.codigo) and self.codigo[self.posicao].isdigit():
                lexema += self.codigo[self.posicao]
                self.posicao += 1
                self.coluna_atual += 1

        return lexema

    def _processar_identificador(self) -> None:
        """Processa identificador ou palavra-chave."""
    
        coluna_inicio = self.coluna_atual
        linha_inicio = self.linha_atual

        lexema = ""

        while self.posicao < len(self.codigo):
            char = self.codigo[self.posicao]

            if not self.gerenciador_tokens.eh_parte_de_identificador(char):
                break

            lexema += char
            self.posicao += 1
            self.coluna_atual += 1

        if lexema.lower() == "causo":
            self._processar_comentario_bloco_mineiro(coluna_inicio, linha_inicio)
            return

        token_type = self.gerenciador_tokens.buscar_palavra_chave(lexema)

        if token_type is None:
            sugestao_keyword = self.gerenciador_tokens.sugerir_palavra_chave_proxima(lexema)
            if sugestao_keyword is not None:
                self.gerenciador_erros.registrar_erro_customizado(
                    tipo="possível typo de palavra-chave",
                    mensagem=f"Identificador '{lexema}' é semelhante a uma palavra-chave da linguagem",
                    linha=linha_inicio,
                    coluna=coluna_inicio,
                    lexema=lexema,
                    sugestao=f"Você quis dizer '{sugestao_keyword}'?",
                )
            token_type = TokenType.IDENTIFIER

        if token_type not in (TokenType.BEGIN_COMMENT, TokenType.END_COMMENT, TokenType.INLINE_COMMENT):
            self.tokens.append(
                Token(
                    lexema=lexema,
                    token=token_type,
                    linha=linha_inicio,
                    coluna=coluna_inicio,
                )
            )

    def _processar_operador(self) -> None:
        """Processa operadores e símbolos."""
    
        coluna_inicio = self.coluna_atual
        linha_inicio = self.linha_atual

        if self.posicao + 1 < len(self.codigo):
            dois_chars = self.codigo[self.posicao : self.posicao + 2]
            token_type = self.gerenciador_tokens.buscar_simbolo_composto(dois_chars)

            if token_type is not None:
                self.tokens.append(
                    Token(
                        lexema=dois_chars,
                        token=token_type,
                        linha=linha_inicio,
                        coluna=coluna_inicio,
                    )
                )
                self.posicao += 2
                self.coluna_atual += 2
                return

        char = self.codigo[self.posicao]
        token_type = self.gerenciador_tokens.buscar_simbolo_simples(char)

        if token_type is not None:
            self.tokens.append(
                Token(
                    lexema=char,
                    token=token_type,
                    linha=linha_inicio,
                    coluna=coluna_inicio,
                )
            )
            self.posicao += 1
            self.coluna_atual += 1
            return

        self.gerenciador_erros.registrar_caractere_invalido(
            char, linha_inicio, coluna_inicio
        )
        self.posicao += 1
        self.coluna_atual += 1

    def _processar_comentario_linha(self) -> None:
        """Ignora comentário de uma linha (//)."""
    
        self.posicao += 2
        self.coluna_atual += 2

        while self.posicao < len(self.codigo) and self.codigo[self.posicao] != "\n":
            self.posicao += 1
            self.coluna_atual += 1

    def _processar_comentario_bloco_mineiro(self, coluna_inicio: int, linha_inicio: int) -> None:
        """Processa comentário multilinha (causo ... fim_do_causo)."""
    
        encontrou_fim = False
        lexema_fim = "fim_do_causo"

        while self.posicao < len(self.codigo):
            char = self.codigo[self.posicao]

            if char == "\n":
                self.linha_atual += 1
                self.coluna_atual = 0
                self.posicao += 1
                continue

            if self.codigo.startswith(lexema_fim, self.posicao):
                fim_pos = self.posicao + len(lexema_fim)

                antes_ok = (
                    self.posicao == 0
                    or (not self.codigo[self.posicao - 1].isalnum() and self.codigo[self.posicao - 1] != "_")
                )

                depois_ok = (
                    fim_pos >= len(self.codigo)
                    or (not self.codigo[fim_pos].isalnum() and self.codigo[fim_pos] != "_")
                )

                if antes_ok and depois_ok:
                    self.posicao = fim_pos
                    self.coluna_atual += len(lexema_fim)
                    encontrou_fim = True
                    break

            self.posicao += 1
            self.coluna_atual += 1

        if not encontrou_fim:
            self.gerenciador_erros.registrar_erro_customizado(
                tipo="comentário não fechado",
                mensagem=f"Comentário 'causo' iniciado em linha {linha_inicio}, coluna {coluna_inicio} não foi fechado com 'fim_do_causo'",
                linha=self.linha_atual,
                coluna=self.coluna_atual,
                sugestao="Use 'fim_do_causo' para encerrar o comentário multilinha",
            )