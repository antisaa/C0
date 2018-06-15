from pj import *

class c0(enum.Enum):
    PLUS, MINUS, PUTA, KROZ, OTV, ZATV = '+-*/()'

    class BROJ(Token):
        def vrijednost(self, mem):
            return int(self.sadržaj)



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
    def start(self):
        env = []
        while True:
            izraz = self.izraz()
            if self >> E.KRAJ: return Program(env, izraz)
            else: self.greška()

    def izraz(self):
        trenutni = self.član()
        while True:
            if self >> {c0.PLUS, c0.MINUS}:
                trenutni = Binarna(
                    op = self.zadnji,
                    lijevo = trenutni,
                    desno = self.član()
                )
            else: return trenutni

    def član(self):
        trenutni = self.faktor()
        while True:
            if self >> {c0.PUTA, c0.KROZ}:
                trenutni = Binarna(self.zadnji, trenutni, self.faktor())
            else: return trenutni

    def faktor(self):
        if self >> c0.MINUS: return Unarna(self.zadnji, self.faktor())
        baza = self.baza()
        return baza

    def baza(self):
        if self >> c0.BROJ: trenutni = self.zadnji
        elif self >> c0.OTV:
            trenutni = self.izraz()
            self.pročitaj(c0.ZATV)
        else: self.greška()
        return trenutni


class Program(AST('okolina izraz')):
    def izvrši(self):
        env = {}
        for ime, izraz in self.okolina: env[ime.sadržaj] = izraz.vrijednost(env)
        return self.izraz.vrijednost(env)

class Binarna(AST('op lijevo desno')):
    def vrijednost(self, env):
        o,x,y = self.op, self.lijevo.vrijednost(env), self.desno.vrijednost(env)
        try:
            if o ** c0.PLUS: return x + y
            elif o ** c0.MINUS: return x - y
            elif o ** c0.PUTA: return x * y
            elif o ** c0.KROZ: return x / y
            else: assert not 'slučaj'
        except ArithmeticError as ex: o.problem(*ex.args)

class Unarna(AST('op ispod')):
    def vrijednost(self, env):
        o, z = self.op, self.ispod.vrijednost(env)
        if o ** c0.MINUS: return -z


def izračunaj(string): return c0Parser.parsiraj(c0_lex(string)).izvrši()
def tokeni(string): return list(c0_lex(string))


if __name__ == '__main__':

    print(tokeni('(3+7)*4'))
    print(izračunaj('(3+7)*4'))

