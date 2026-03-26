#include "Token.hpp"

Token::Token() : lexema(""), token(0), linha(0), coluna(0) {}

Token::Token(std::string lexema, int token, int linha, int coluna)
    : lexema(lexema), token(token), linha(linha), coluna(coluna) {}

std::string Token::getLexema() const {
    return lexema;
}

int Token::getToken() const {
    return token;
}

int Token::getLinha() const {
    return linha;
}

int Token::getColuna() const {
    return coluna;
}

void Token::setLexema(const std::string& lexema) {
    this->lexema = lexema;
}

void Token::setToken(int token) {
    this->token = token;
}

void Token::setLinha(int linha) {
    this->linha = linha;
}

void Token::setColuna(int coluna) {
    this->coluna = coluna;
}