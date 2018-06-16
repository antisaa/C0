from pj import *

def sign(number):
    if(number < 0):
        return -1
    else:
        return 1

def modl(number, br):
    return sign(int(number)) * ( (sign(int(number)) * int(number) ) % (sign(int(br))*int(br)))

def integer(number):
    number = sign(int(number)) * ( (sign(int(number))*int(number)) % (2**32))
    if int(number) >= 2**31:
        return int(number) - 2**32
    else:
        return number

class c0(enum.Enum):
    PLUS, MINUS, PUTA, KROZ, MOD = '+-*/%'
    OTV, ZATV, VOTV, TZAREZ, ZAREZ, VZATV = '(){;,}'
    LSHIFT, RSHIFT = '<<', '>>'
    BITAND, BITOR, BITXOR = '&', '|', '^'
    LOGAND, LOGOR = '&&', '||'
    EQL, DISEQL = '==', '!='
    MANJE, VEĆE, VJEDNAKO, MJEDNAKO = '<', '>', '>=', '<='
    JEDNAKO = '='
    INT, BOOL = 'int', 'bool'
    TRUE, FALSE = 'true', 'false'
    LNOT,BNOT ='!~'
    INC,DEC = '++','--'

    class BROJ(Token):
        def vrijednost(self, mem):
            return integer(self.sadržaj)

    class IME(Token):
        def vrijednost(self,mem):
            return mem[self]



def c0_lex(string):
    lex = Tokenizer(string)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace():
            lex.token(E.PRAZNO)
        elif znak == '<':
            if lex.slijedi('<'):    yield lex.token(c0.LSHIFT)
            elif lex.slijedi('='):  yield lex.token(c0.MJEDNAKO)
            else:   yield lex.token(c0.MANJE)
        elif znak == '>':
            if lex.slijedi('>'):    yield lex.token(c0.RSHIFT)
            elif lex.slijedi('='):  yield lex.token(c0.VJEDNAKO)
            else:   yield lex.token(c0.VEĆE)
        elif znak == '=':
            if lex.slijedi('='):    yield lex.token(c0.EQL)
            else:   yield lex.token(c0.JEDNAKO)
        elif znak == '&':
            if lex.slijedi('&'):    yield lex.token(c0.LOGAND)
            else:   yield lex.token(c0.BITAND)
        elif znak == '|':
            if lex.slijedi('|'):    yield lex.token(c0.LOGOR)
            else:   yield lex.token(c0.BITOR)
        elif znak == '+':
            if lex.slijedi('+'):    yield lex.token(c0.INC)
            else:   yield lex.token(c0.PLUS)
        elif znak == '-':
            if lex.slijedi('-'):    yield lex.token(c0.DEC)
            else:   yield lex.token(c0.MINUS)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(c0.BROJ)
        elif znak.islower():
            lex.zvijezda(str.isalpha)
            yield lex.token(ključna_riječ(c0, lex.sadržaj) or c0.IME)
        else: yield lex.token(operator(c0, znak) or lex.greška())

### BKG (ne sasvim BK:)
# program -> (BOOL | INT) IME OTV parametri? ZATV VOTV naredba VZATV program?
# parametri -> (BOOL | INT) IME (ZAREZ parametri)?
# naredba -> pridruži TZAREZ| naredbe? |  VRATI izraz TZAREZ
# naredbe -> naredba (TZAREZ naredbe)?
# pridruži -> IME [BOOL|INT] JEDNAKO [aritm | log]
# log -> log ILI disjunkt | disjunkt
# disjunkt -> aritm (MANJE | JEDNAKO) aritm | LIME | LKONST |
#             LIME OTV argumenti ZATV
# aritm -> aritm PLUS član | aritm MINUS član
# član -> član ZVJEZDICA faktor | faktor | MINUS faktor
# faktor -> BROJ | AIME | OTV aritm ZATV | AIME OTV argumenti ZATV
# argumenti -> izraz (ZAREZ argumenti)?
# izraz -> aritm |! log [KONTEKST!]




### Beskontekstna gramatika
# start -> bit_or                                                                           CHECK
# bit_or -> bit_or BITOR bit_xor | bit_xor                                                  CHECK
# bit_xor -> bit_xor BITXOR bit_and | bit_and                                               CHECK
# bit_and ->  bit_and BITAND shift_izraz | shift_izraz                                      CHECK
# shift_izraz -> shift_izraz LSHIFT izraz | shift_izraz RSHIFT izraz | izraz                CHECK
# izraz -> izraz PLUS član | izraz MINUS član | član                                        CHECK
# član -> član PUTA faktor | član KROZ faktor | član MOD faktor | faktor                    CHECK
# faktor ->   baza | MINUS faktor | LNOT faktor | BNOT faktor | INC faktor | DEC faktor     CHECK
# baza -> BROJ | OTV bit_or ZATV                                                            CHECK

class c0Parser(Parser):
    def start(self):
        env = []
        while True:
            bit_or = self.bit_or()
            if self >> E.KRAJ: return Program(env, bit_or)
            else: self.greška()

    def bit_or(self):
        trenutni = self.bit_xor()
        while True:
            if self >> c0.BITOR:
                trenutni = Binarna(
                    op = self.zadnji,
                    lijevo = trenutni,
                    desno = self.bit_xor()
                )
            else: return trenutni

    def bit_xor(self):
        trenutni = self.bit_and()
        while True:
            if self >> c0.BITXOR:
                trenutni = Binarna(
                    op = self.zadnji,
                    lijevo = trenutni,
                    desno = self.bit_and()
                )
            else: return trenutni


    def bit_and(self):
        trenutni = self.shift_izraz()
        while True:
            if self >> c0.BITAND:
                trenutni = Binarna(
                    op = self.zadnji,
                    lijevo = trenutni,
                    desno = self.shift_izraz()
                )
            else: return trenutni

    def shift_izraz(self):
        trenutni = self.izraz()
        while True:
            if self >> {c0.RSHIFT, c0.LSHIFT}:
                trenutni = Binarna(
                    op = self.zadnji,
                    lijevo = trenutni,
                    desno = self.izraz()
                )
            else: return trenutni

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
            if self >> {c0.PUTA, c0.KROZ, c0.MOD}:
                trenutni = Binarna(self.zadnji, trenutni, self.faktor())
            else: return trenutni


    def faktor(self):
        if self >> c0.MINUS: return Unarna(self.zadnji, self.faktor())
        elif self >> c0.LNOT: return Unarna(self.zadnji, self.faktor())
        elif self >> c0.BNOT: return Unarna(self.zadnji, self.faktor())
        elif self >> c0.INC: return Unarna(self.zadnji, self.faktor())
        elif self >> c0.DEC: return Unarna(self.zadnji, self.faktor())


        baza = self.baza()
        return baza

    def baza(self):
        if self >> c0.BROJ: trenutni = self.zadnji
        elif self >> c0.OTV:
            trenutni = self.bit_or()
            self.pročitaj(c0.ZATV)
        else: self.greška()
        return trenutni


class Program(AST('okolina bit_or')):
    def izvrši(self):
        env = {}
        for ime, bit_or in self.okolina: env[ime.sadržaj] = bit_or.vrijednost(env)
        return self.bit_or.vrijednost(env)

class Binarna(AST('op lijevo desno')):
    def vrijednost(self, env):
        o,x,y = self.op, self.lijevo.vrijednost(env), self.desno.vrijednost(env)
        try:
            if o ** c0.BITOR: return integer(x) | integer(y)
            elif o ** c0.BITXOR: return integer(x) ^ integer(y)
            elif o ** c0.BITAND: return integer(x) & integer(y)
            elif o ** c0.RSHIFT:
                if y < 0: raise SemantičkaGreška("right shift count is negative")
                elif y > 31: raise SemantičkaGreška("right shift count >= width of type")
                else: return integer(x // (2**y))
            elif o ** c0.LSHIFT:
                if y < 0: raise SemantičkaGreška("left shift count is negative")
                elif y > 31: raise SemantičkaGreška("left shift count >= width of type")
                else: return integer(x * (2**y))
            elif o ** c0.PLUS: return integer(x + y)
            elif o ** c0.MINUS: return integer(x - y)
            elif o ** c0.PUTA: return integer(x * y)
            elif o ** c0.KROZ:
                if y == 0 : raise SemantičkaGreška("Dijeljenje s nulom.")
                elif integer(x) == -2**31 and integer(y) == -1 : raise SemantičkaGreška("Greška: overflow.")
                return integer(sign(x) * sign(y) * ( (sign(x)*x) // (sign(y)*y)) ) #handlaj  dijeljenje nulom
            elif o ** c0.MOD:
                if y == 0 : raise SemantičkaGreška("Dijeljenje s nulom.")
                elif integer(x) == -2**31 and integer(y) == -1 : raise SemantičkaGreška("Greška: overflow.")
                return integer(sign(x) * ( (sign(x)*x) % (sign(y)*y)) ) #handlaj  dijeljenje nulom
            else: assert not 'slučaj'
        except ArithmeticError as ex: o.problem(*ex.args)

class Unarna(AST('op ispod')):
    def vrijednost(self, env):
        o, z = self.op, self.ispod.vrijednost(env)
        if o ** c0.MINUS: return -z
        elif o ** c0.LNOT: return int(not z)
        elif o ** c0.BNOT: return ~z
        elif o ** c0.INC: return z+1
        elif o ** c0.DEC: return z-1


def izračunaj(string): return c0Parser.parsiraj(c0_lex(string)).izvrši()
def tokeni(string): return list(c0_lex(string))


if __name__ == '__main__':

    print(tokeni('(3+7)%3'))
    print()
    print(izračunaj('(3+7)%3'))
    print(integer(2**31+1))
    print(izračunaj('-37% 5'))
    print(izračunaj('-37/ 5'))
    #print(izračunaj('-2147483648/-1'))
    print(-37 % 5)
    print(-37 // 5)
    print(sign(-5))
    print(-2**31)
    print(integer(-2**31))
    print(int(-2**31)%(2**32))
    print(modl(-37,-5))

    #print(izračunaj('1>>-1'))
    print(izračunaj('1>>0'))
    #print(izračunaj('1>>32'))
    #print(izračunaj('1<<-1'))
    print(izračunaj('1<<0'))
    print(izračunaj('1<<31'))
    #print(izračunaj('1<<32'))
    print(integer(2**31))

    print(izračunaj('21474^0'))
    print(izračunaj('2147483647|-1'))
    print()
    print(tokeni('(212<<4&3134|133>>2^121356543)<<(3^7)>>(45689&25<<7)'))
    print(izračunaj('(212<<4&3134|133>>2^121356543)<<(3^7)>>(45689&25<<7)'))
    print()
    print(izračunaj('45689&25<<7'))
    print(izračunaj('(3^7)'))
    print(izračunaj('212<<4&3134|133>>2^121356543'))
    print(izračunaj('3134|133>>2^121356543'))
    print()
    print(izračunaj('212<<4&3134'))
    print(izračunaj('133>>2'))
    print(izračunaj('2^121356543'))
    print(izračunaj('3134|133>>2'))
    print(izračunaj('-(15<<13)/(3+4|3<<9)>>28-26'))
    print()
    print(izračunaj('!3'))
    print(izračunaj('!7'))
    print(izračunaj('!0'))
    print(izračunaj('++7'))
    print(izračunaj('(--0)*3+8*(++7)'))
    print(izračunaj('~5'))
    print()
    print(*tokeni('''int main()
{
  int g;
  g = 7;
  bool mirko = true;
  funkcije(7,true, 25 << 3);
  return 0;
}'''))
