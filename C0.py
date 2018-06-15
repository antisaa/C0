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
# start ->  izraz                                           KVAČICA
# izraz -> izraz PLUS član | izraz MINUS član | član        KVAČICA
# član -> član PUTA faktor | član KROZ faktor | faktor      KVAČICA
# faktor ->  baza | MINUS faktor                            KVAČICA
# baza -> BROJ | OTV izraz ZATV                             KVAČICA

class c0Parser(Parser):
    def izraz(self):
        trenutni = self.član()
        while True:
            if self >> {AC.PLUS, AC.MINUS}:
                trenutni = Binarna(
                    op = self.zadnji,
                    lijevo = trenutni,
                    desno = self.član()
                )
            else: return trenutni

    def član(self):
        trenutni = self.faktor()
        while True:
            if self >> {AC.PUTA, AC.KROZ}:
                trenutni = Binarna(self.zadnji, trenutni, self.faktor())
            else: return trenutni

    def faktor(self):
        if self >> AC.MINUS: return Unarna(self.zadnji, self.faktor())
        baza = self.baza()
        return baza

    def baza(self):
        if self >> AC.BROJ: trenutni = self.zadnji
        elif self >> AC.OTV:
            trenutni = self.izraz()
            self.pročitaj(AC.ZATV)
        else: self.greška()
        return trenutni

    start = izraz



class Binarna(AST('op lijevo desno')):
    def vrijednost(self, env):
        o,x,y = self.op, self.lijevo.vrijednost(env), self.desno.vrijednost(env)
        try:
            if o ** AC.PLUS: return x + y
            elif o ** AC.MINUS: return x - y
            elif o ** AC.PUTA: return x * y
            elif o ** AC.KROZ: return x / y
            else: assert not 'slučaj'
        except ArithmeticError as ex: o.problem(*ex.args)

class Unarna(AST('op ispod')):
    def vrijednost(self, env):
        o, z = self.op, self.ispod.vrijednost(env)
        if o ** AC.MINUS: return -z


def izračunaj(string): return ACParser.parsiraj(ac_lex(string)).izvrši()

if __name__ == '__main__':
    tokeni = c0_lex('3+7*4')
    print(list(tokeni))
    print(izračunaj('3+7*4'))

