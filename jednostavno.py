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
    OTV, ZATV, VOTV, TZAREZ, ZAREZ, VZATV, UPITNIK, DVOTOČKA = '(){;,}?:'
    LSHIFT, RSHIFT = '<<', '>>'
    BITAND, BITOR, BITXOR = '&', '|', '^'
    LOGAND, LOGOR = '&&', '||'
    JJEDNAKO, RAZLIČITO = '==', '!='
    MANJE, VEĆE, VJEDNAKO, MJEDNAKO = '<', '>', '>=', '<='
    JEDNAKO = '='
    INT, BOOL = 'int', 'bool'
    TRUE, FALSE = 'true', 'false'
    FOR, WHILE, IF, ELSE = 'for', 'while', 'if', 'else'
    LNOT,BNOT ='!~'
    PPLUS,MMINUS = '++','--'

    class BROJ(Token):
        def vrijednost(self, mem):
            return integer(self.sadržaj)

    class IME(Token):
        def vrijednost(self,mem):
            return mem[self]

    class AIME(Token):
        def vrijednost(self,mem):
            return mem[self]

    class LIME(Token):
        def vrijednost(self,mem):
            return mem[self]

    class BREAK(Token):
        def izvrši(self, mem):
            raise BreakException

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
            if lex.slijedi('='):    yield lex.token(c0.JJEDNAKO)
            else:   yield lex.token(c0.JEDNAKO)
        elif znak == '&':
            if lex.slijedi('&'):    yield lex.token(c0.LOGAND)
            else:   yield lex.token(c0.BITAND)
        elif znak == '|':
            if lex.slijedi('|'):    yield lex.token(c0.LOGOR)
            else:   yield lex.token(c0.BITOR)
        elif znak == '+':
            if lex.slijedi('+'):    yield lex.token(c0.PPLUS)
            else:   yield lex.token(c0.PLUS)
        elif znak == '-':
            if lex.slijedi('-'):    yield lex.token(c0.MMINUS)
            else:   yield lex.token(c0.MINUS)
        elif znak == '!':
            if lex.slijedi('='):    yield lex.token(c0.RAZLIČITO)
            else:   yield lex.token(c0.LNOT)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            if lex.sadržaj == '0' or lex.sadržaj[0] != '0':
                yield lex.token(c0.BROJ)
            else: lex.greška('druge baze nisu podržane')
        elif znak.islower():
            lex.zvijezda(str.isalpha)
            if lex.sadržaj == 'break': yield lex.token(c0.BREAK)
            yield lex.token(ključna_riječ(c0, lex.sadržaj) or c0.IME)
        else: yield lex.token(operator(c0, znak) or lex.greška())

### BKG (ne sasvim BK:)
# program -> ime OTV parametri? ZATV JEDNAKO naredba program?
# naredba -> pridruži | OTV naredbe? ZATV | (AKO | DOK) (JE | NIJE) log naredba
#            | AKO JE log naredba INAČE naredba | VRATI izraz
# ime -> AIME | LIME
# parametri -> ime (ZAREZ parametri)?
# naredbe -> naredba (ZAREZ naredbe)?
# pridruži -> AIME JEDNAKO aritm | LIME JEDNAKO log
# log -> log ILI disjunkt | disjunkt
# disjunkt -> aritm (MANJE | JEDNAKO) aritm | LIME | LKONST |
#             LIME OTV argumenti ZATV
# aritm -> aritm PLUS član | aritm MINUS član
# član -> član ZVJEZDICA faktor | faktor | MINUS faktor
# faktor -> BROJ | AIME | OTV aritm ZATV | AIME OTV argumenti ZATV
# argumenti -> izraz (ZAREZ argumenti)?
# izraz -> aritm |! log [KONTEKST!]
tipF = {}
tipV = {}
class c0Parser(Parser):
    """self.tipF = {}
    self.tipV = {}
"""
    def program(self):
        self.funkcije = {}
        while not self >> E.KRAJ:
            funkcija = self.funkcija()
            imef = funkcija.ime
            if imef in self.funkcije: raise SemantičkaGreška(
                'Dvaput definirana funkcija ' + imef.sadržaj)
            self.funkcije[imef] = funkcija
        return self.funkcije

    def funkcija(self):
        if self >> c0.BOOL:
            ime = Token(c0.LIME, self.pročitaj(c0.IME).sadržaj)
        elif self >> c0.INT:
            ime = Token(c0.AIME, self.pročitaj(c0.IME).sadržaj)
        else: self.greška()
        self.logička = bool(ime ** c0.LIME)
        tipF[ime.sadržaj] = ime
        self.pročitaj(c0.OTV)
        if self >> c0.ZATV: parametri = []
        elif self >> {c0.BOOL, c0.INT}:
            if self.zadnji.sadržaj == 'bool':
                ime = Token(c0.LIME, self.pročitaj(c0.IME).sadržaj)
            elif self.zadnji.sadržaj == 'int':
                ime = Token(c0.AIME, self.pročitaj(c0.IME).sadržaj)
            else: self.greška()
            tipV[ime.sadržaj] = ime
            parametri = [ime]
            print('...................................parametri', parametri)
            """parametri"""
            while self >> c0.ZAREZ:
                if self >> c0.BOOL:
                    ime = Token(c0.LIME, self.pročitaj(c0.IME).sadržaj)
                elif self >> c0.INT:
                    ime = Token(c0.AIME, self.pročitaj(c0.IME).sadržaj)
                else: self.greška()
                tipV[ime.sadržaj] = ime
                parametri.append(ime)
            self.pročitaj(c0.ZATV)
        else: self.greška()
        self.pročitaj(c0.VOTV)
        naredba = self.naredbe()
        self.pročitaj(c0.VZATV)
        return Funkcija(ime, parametri, naredba)


    def naredba(self):
        if self >> c0.WHILE:
            self.pročitaj(c0.OTV)
            izraz = self.izraz()
            self.pročitaj(c0.ZATV)
            naredba = self.naredba()
            return While(izraz, naredba)
        elif self >> c0.IF:
            self.pročitaj(c0.OTV)
            izraz = self.izraz()
            self.pročitaj(c0.ZATV)
            naredba = self.naredba()
            if self >> c0.ELSE:
                naredba2 = self.naredba()
                return If2(izraz, naredba, naredba2)
            else:
                return If(izraz, naredba)
        elif self >> c0.FOR:
            self.pročitaj(c0.OTV)
            jednostavni = self.jednostavni()
            self.pročitaj(c0.TZAREZ)
            izraz = self.izraz()
            self.pročitaj(c0.TZAREZ)
            jednostavni2 = self.jednostavni()
            self.pročitaj(c0.ZATV)
            naredba = self.naredba()
            return For(jednostavni, izraz, jednostavni2, naredba)
        elif self >> c0.BREAK:
            br = self.zadnji
            self.pročitaj(c0.TOČKAZ)
            return br
        elif self >> c0.RETURN:
            """izraz = self.izraz()
            self.pročitaj(c0.TZAREZ)"""
            return Return(self.izraz)
        elif self >> c0.VOTV:
            naredba = self.naredbe()
            self.pročitaj(c0.VZATV)
            return naredba
        else:
            jednostavni = self.jednostavni()
            self.pročitaj(c0.TZAREZ)
            return jednostavni

    def naredbe(self):
        naredbe = [self.naredba()]
        while self >> c0.TZAREZ:
            if self >= c0.ZATV: return Blok(naredbe)
            naredbe.append(self.naredba())
        return Blok(naredbe)

    def jednostavni(self):
        if self >> c0.BOOL:
            ime = Token(c0.LIME, self.pročitaj(c0.IME).sadržaj)
            tipV[ime.sadržaj] = ime
            if self >> c0.JEDNAKO:
                izraz = self.izraz()
                return Pridruživanje(ime, izraz)
            else:
                return Pridruživanje(ime, c0.FALSE)
        elif self >> c0.INT:
            ime = Token(c0.AIME, self.pročitaj(c0.IME).sadržaj)
            tipV[ime.sadržaj] = ime
            if self >> c0.JEDNAKO:
                izraz = self.izraz()
                """treba postaviti vrijednost tokena na 0, odnosno nesto"""
                return Pridruživanje(ime, izraz)
            else:
                return Pridruživanje(ime, '0')
        elif self.pogledaj().sadržaj == '(' or self.pogledaj() ** c0.IME:
            print("anteskasdad",self.pogledaj().sadržaj == '(' or self.pogledaj() ** c0.IME)
            naziv = self.naziv()
            asnop = self.asnop()
            izraz = self.izraz()
            return Pridruživanje2(naziv, asnop, izraz)
        else:
            izraz = self.izraz()
            return izraz

    def naziv(self):
        if self >> c0.OTV:
            ime = self.naziv()
            self.pročitaj(c0.ZATV)
            return ime
        elif self >> c0.IME:
            ime = self.zadnji
            if ime.sadržaj in tipV:
                return tipV[ime.sadržaj]
            if ime.sadržaj in tipF:
                return tipF[ime.sadržaj]
        else:
            self.greška()

    def izraz(self):
        if self >> {c0.BROJ, c0.TRUE, c0.FALSE}:
            return self.zadnji
        elif self >> c0.OTV:
            izraz = self.izraz()
            self.pročitaj(c0.ZATV)
            return izraz
        elif self >> c0.IME:
            ime = self.zadnji
            if self >= c0.OTV:
                ime = tipF[ime.sadržaj]
                return self.poziv(ime)
            elif ime.sadržaj in tipV:
                return tipV[ime.sadržaj]
            elif ime.sadržaj in tipF:
                return tipF[ime.sadržaj]
            else:
                self.greška()
        else:
            bit_or = self.bit_or()
            return bit_or
            """izraz = self.izraz()
            if self >> c0.UPITNIK:
                izraz2 = self.izraz()
                self.pročitaj(c0.DVOTOČKA)
                izraz3 = self.izraz()
                return Trinar(izraz, izraz2, izraz3)
            else:"""
            """binop = self.binop(izraz)
                izraz2 = self.izraz2()
                return Binop(izraz, binop, izraz2)
                izraz = [self.izraz()]
                while self >> c0.ZAREZ:
                    izraz.append(self.izraz())
                self.pročitaj(c0.ZATV)
                ime = tipF[ime.sadržaj]
                if ime in self.funkcije: funkcija = self.funkcije[ime]
                else: raise SemantičkaGreška(
                    'Nedeklarirana funkcija ' + ime.sadržaj)
                return Poziv(funkcija, self.argumenti(funkcija.parametri))
                return Poziv(ime, izraz)"""

    def poziv(self, ime):
        if ime in self.funkcije: funkcija = self.funkcije[ime]
        else: raise SemantičkaGreška(
            'Nedeklarirana funkcija ' + ime.sadržaj)
        return Poziv(funkcija, self.argumenti(funkcija.parametri))


    def argumenti(self, parametri):
        arg = []
        prvi = True
        for parametar in parametri:
            self.pročitaj(c0.OTV if prvi else c0.ZAREZ)
            prvi = False
            if parametar ** c0.LIME: arg.append(self.izraz())
            else: arg.append(self.izraz())
        self.pročitaj(c0.ZATV)
        return arg

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
        trenutni = self.osnovne()
        while True:
            if self >> {c0.RSHIFT, c0.LSHIFT}:
                trenutni = Binarna(
                    op = self.zadnji,
                    lijevo = trenutni,
                    desno = self.osnovne()
                )
            else: return trenutni

    def osnovne(self):
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
        elif self >> c0.PPLUS: return Unarna(self.zadnji, self.faktor())
        elif self >> c0.MMINUS: return Unarna(self.zadnji, self.faktor())


        baza = self.izraz()
        return baza

    """def baza(self):
        if self >> c0.BROJ: trenutni = self.zadnji
        elif self >> c0.OTV:
            trenutni = self.bit_or()
            self.pročitaj(c0.ZATV)
        else: self.greška()
        return trenutni"""


    def asnop(self):
        if self >> c0.JEDNAKO:
            return self.zadnji

    start = program

def izvrši(funkcije, *argv):
    program = Token(c0.AIME, 'main')
    if program in funkcije:
        izlazna_vrijednost = funkcije[program].pozovi(argv)
        print('Program je vratio: ', izlazna_vrijednost)
    else: raise SemantičkaGreška('Nema glavne funkcije "main"')



class Funkcija(AST('ime parametri naredba')):
    def pozovi(self, argumenti):
        lokalni = dict(zip(self.parametri, argumenti))
        print(self.parametri)
        print("ASURBANIPAL",argumenti)
        print(lokalni)
        print()
        try: self.naredba.izvrši(lokalni)
        except Povratak as exc:
            if exc.povratna_vrijednost == None:
                print("None")
                return 0;
            else:
                return exc.povratna_vrijednost

class Poziv(AST('funkcija argumenti')):
    def vrijednost(self, mem):
        print(self.argumenti)
        print(mem)

        print()
        arg = [argument.vrijednost(mem) for argument in self.argumenti]
        return self.funkcija.pozovi(arg)

class While(AST('uvjet naredba')):
    def izvrši(self, mem):
        while self.uvjet.vrijednost(mem):
            try:
                self.naredba.izvrši(mem)
            except BreakException: break

class If(AST('izraz, naredba')):
    def izvrši(self, mem):
        print("mem",mem)
        if self.izraz.vrijednost(mem): self.naredba.izvrši(mem)

class If2(AST('izraz, naredba, naredba2')):
    def izvrši(self, mem):
        print("mem",mem)
        if self.izraz.vrijednost(mem): self.naredba.izvrši(mem)
        else: self.naredba2.izvrši(mem)

class For(AST('jednostavni, izraz, jednostavni2, naredba')):
    def izvrši(self, mem):
        self.jednostavni.izvrši(mem)
        while self.izraz.vrijednost(mem):
            try:
                self.naredba.izvrši(mem)
                self.jednostavni2.izvrši(mem)
            except BreakException: break

class BreakException(Exception): pass

class Return(AST('što')):
    def izvrši(self, mem):
        print(self.što)
        print(self.što.vrijednost(mem))
        if self.što.vrijednost(mem) == None:
            raise Povratak2()
        raise Povratak(self.što.vrijednost(mem))

class Blok(AST('naredbe')):
    def izvrši(self, mem):
        for naredba in self.naredbe: naredba.izvrši(mem)


class Pridruživanje(AST('ime pridruženo')):
    def izvrši(self, mem):
        if tipV[self.ime.sadržaj].sadržaj == 'false' or tipV[self.ime.sadržaj].sadržaj == 'true':
            tip = 1
        else: tip = 0
        if self.pridruženo.vrijednost(mem) == 'false' or self.pridruženo.vrijednost(mem) == 'true':
            vrj = 1
        else: vrj = 0
        if(vrj != tip):
            raise SemantičkaGreška("Ne podudaraju se tipovi")
        mem[self.ime] = self.pridruženo.vrijednost(mem)
        print(self.ime.sadržaj)
        print("go_____r______e")

class Pridruživanje2(AST('ime op pridruženo')):
    def izvrši(self, mem):
        if tipV[self.ime.sadržaj].sadržaj == 'false' or tipV[self.ime.sadržaj].sadržaj == 'true':
            tip = 1
        else: tip = 0
        if self.pridruženo.vrijednost(mem) == 'false' or self.pridruženo.vrijednost(mem) == 'true':
            vrj = 1
        else: vrj = 0
        if(vrj != tip):
            raise SemantičkaGreška("Ne podudaraju se tipovi")
        if self.op.sadržaj == '=':
            mem[self.ime] = self.pridruženo.vrijednost(mem)
        print(self.ime.sadržaj)
        print("go_____r______e")

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
        elif o ** c0.PPLUS: return z+1
        elif o ** c0.MMINUS: return z-1

class Povratak2(Exception): pass
class Povratak(Exception):
    @property
    def povratna_vrijednost(self): return self.args[0]

"""
def binop(self, izraz):



DO TUD

"""

def izračunaj(string): return c0Parser.parsiraj(c0_lex(string)).izvrši()
def tokeni(string): return list(c0_lex(string))

#izvrši(faktorijela, {})

if __name__ == '__main__':
    print(tokeni('(3+7)%3'))
    print()
    print(tokeni('(3+7)%3'))
    print(integer(2**31+1))
    print(tokeni('-37% 5'))
    print(tokeni('-37/ 5'))
    #print(tokeni('-2147483648/-1'))
    print(-37 % 5)
    print(-37 // 5)
    print(sign(-5))
    print(-2**31)
    print(integer(-2**31))
    print(int(-2**31)%(2**32))
    print(modl(-37,-5))

    #print(tokeni('1>>-1'))
    print(tokeni('1>>0'))
    #print(tokeni('1>>32'))
    #print(tokeni('1<<-1'))
    print(tokeni('1<<0'))
    print(tokeni('1<<31'))
    #print(tokeni('1<<32'))
    print(integer(2**31))

    print(tokeni('21474^0'))
    print(tokeni('2147483647|-1'))
    print()
    print(tokeni('(212<<4&3134|133>>2^121356543)<<(3^7)>>(45689&25<<7)'))
    print(tokeni('(212<<4&3134|133>>2^121356543)<<(3^7)>>(45689&25<<7)'))
    print()
    print(tokeni('45689&25<<7'))
    print(tokeni('(3^7)'))
    print(tokeni('212<<4&3134|133>>2^121356543'))
    print(tokeni('3134|133>>2^121356543'))
    print()
    print(tokeni('212<<4&3134'))
    print(tokeni('133>>2'))
    print(tokeni('2^121356543'))
    print(tokeni('3134|133>>2'))
    print(tokeni('-(15<<13)/(3+4|3<<9)>>28-26'))
    print()
    print(tokeni('!3'))
    print(tokeni('!7'))
    print(tokeni('!0'))
    print(tokeni('++7'))
    print(tokeni('(--0)*3+8*(++7)'))
    print(tokeni('~5'))
    print()
    print(*tokeni('''int main()
{
  int g;
  g = 7;
  bool mirko = true;
  funkcije(7,true, 25 << 3);
  return 0;
}'''))
    print(tokeni('''
    int f( int x, int y){
    int i;
    for(i = 10; i)
    }
    int main () {
    int x = 2;

    return x;
    }'''))

    faktorijela = c0Parser.parsiraj(c0_lex('''
    int main () {
    int x = 2;
    x;
    int a;
    (a);
    }'''))
    print(faktorijela)
    print()
    izvrši(faktorijela, {})
