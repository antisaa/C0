from pj import *

class c0(enum.Enum):
    PLUS, MINUS, PUTA, KROZ = '+-*/'

    class BROJ(Token):
        def vrijednost(self, mem):
            return mem[self]



def c0_lex(string):
    lex = Tokenizer(string)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace():
            lex.token(E.PRAZNO)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(c0.BROJ)
        else: yield lex.token(operator(c0, znak) or lex.greška())

### Beskontekstna gramatika
# start ->  izraz
# izraz -> izraz PLUS član | izraz MINUS član | član
# član -> član PUTA faktor | član KROZ faktor | faktor
# faktor ->  baza | MINUS faktor
# baza -> BROJ | OTV izraz ZATV


if __name__ == '__main__':
    tokeni = c0_lex('3+7*4')
    print(list(tokeni))

