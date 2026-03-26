#ifndef TOKEN_HPP
#define TOKEN_HPP

#include <string>

class Token {
private:
    std::string lexema; 
    int token;
    int linha;
    int coluna;

public:

    Token();
    Token(std::string lexema, int token, int linha, int coluna);

    std::string getLexema() const;
    int getToken() const;
    int getLinha() const;
    int getColuna() const;

    void setLexema(const std::string& lexema);
    void setToken(int token);
    void setLinha(int linha);
    void setColuna(int coluna);
};

#endif 