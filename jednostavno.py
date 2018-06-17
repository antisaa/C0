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
    OTV, ZATV, VOTV, TZAREZ, ZAREZ, VZATV, UPITNIK, DVOTOCKA = '(){;,}?:'
    LSHIFT, RSHIFT = '<<', '>>'
    BITAND, BITOR, BITXOR = '&', '|', '^'
    LOGAND, LOGOR = '&&', '||'
    EQL, DISEQL = '==', '!='
    MANJE, VEĆE, VJEDNAKO, MJEDNAKO = '<', '>', '>=', '<='
    JEDNAKO = '='
    INT, BOOL = 'int', 'bool'
    TRUE, FALSE = 'true', 'false'
    FOR, WHILE, IF, ELSE = 'for', 'while', 'if', 'else'
    LNOT,BNOT ='!~'
    INC,DEC = '++','--'

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

class PseudokodParser(Parser):
    self.tipF = {}
    self.tipV = {}

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
        self.logička = bool(ime ** PSK.LIME)
        self.pročitaj(PSK.OTV)
        tipF[ime.sadržaj] = ime
        if self >> PSK.ZATV: parametri = []
        elif self >> {c0.BOOL, c0.INT}:
            if self.zadnji == c0.BOOL:
                ime = Token(c0.LIME, self.pročitaj(c0.IME).sadržaj)
            elif self.zadnji == c0.INT:
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
            self.pročitaj(PSK.ZATV)
        else: self.greška()
        self.pročitaj(c0.VOTV)
        naredba = self.naredba()
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
            return For(jednostavnii, izraz, jednostavni2, naredba)
        elif self >> c0.RETURN:
            izraz = self.izraz()
            self.pročitaj(c0.TZAREZ)
            return Return(izraz)
        elif self >> c0.VOTV:
            naredba = self.naredba()
            self.pročitaj(c0.VZATV)
            return VNarV(naredba)
        else:
            jednostavni = self.jednostavni()
            self.pročitaj(c0.TZAREZ)
            return Jednostavni(jednostavni)

    def jednostavni(self):
        if self >> c0.BOOL:
            ime = Token(c0.LIME, self.pročitaj(c0.IME).sadržaj)
            tipV[ime.sadržaj] = ime
            if self >> c0.JEDNAKO:
                izraz = self.izraz()
                return Jednostavni(ime, izraz)
            else:
                return Jednostavni(ime, c0.FALSE)
        elif self >> c0.INT:
            ime = Token(c0.AIME, self.pročitaj(c0.IME).sadržaj)
            tipV[ime.sadržaj] = ime
            if self >> c0.JEDNAKO:
                izraz = self.izraz()
                """treba postaviti vrijednost tokena na 0, odnosno nesto"""
                return Jednostavni(ime, izraz)
            else:
                return Jednostavni(ime, '0')
        elif self.pogledaj() == c0.OTV or self.pogledaj() == c0.IME:
            naziv = self.naziv()
            if self >> c0.PPLUS:
                return PPlus(naziv)
            elif self >> c0.MMINUS:
                return MMinus(naziv)
            else:
                asnop = self.asnop()
                izraz = self.izraz()
                return Asnop(naziv, asnop, izraz)
        else:
            izraz = self.izraz()
            return Izraz(izraz)

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
        elif self >> c0.IME:
            ime = c0.IME
            if self >> c0.OTV:
                izraz = [self.izraz()]
                while self >> c0.ZAREZ:
                    izraz.append(self.izraz())
                self.pročitaj(c0.ZATV)
                ime = tipF[ime.sadržaj]
                return Poziv(ime izraz)
            elif ime.sadržaj in tipV:
                return tipV[ime.sadržaj]
            elif ime.sadržaj in tipF:
                return tipF[ime.sadržaj]
            else:
                self.greška()
        elif self >> c0.OTV:
            izraz = self.izraz()
            self.pročitaj(c0.ZATV)
            return Izraz(izraz)
        elif self >> {c0.LNOT, c0.BNOT, c0.MINUS}:
            op = self.zadnji
            izraz = self.izraz()
            return Unarna(op, izraz)
        elif:
            izraz = self.izraz()
            if self >> c0.UPITNIK:
                izraz2 = self.izraz()
                self.pročitaj(c0.DVOTOCKA)
                izraz3 = self.izraz()
                return Trinar(izraz, izraz2, izraz3)
        else:
            """
            izraz = self.izraz()
            binop = self.binop()
            izraz2 = self.izraz2()
            return Binop(izraz, binop, izraz2)
"""
    def asnop(self):
        if self >> {c0.JEDNAKO}:
            return self.zadnji

    def binop(self):
        """




DO TUD





        """
    def naredbe(self):
        naredbe = [self.naredba()]
        while self >> PSK.ZAREZ:
            if self >= PSK.ZATV: return Blok(naredbe)
            naredbe.append(self.naredba())
        return Blok(naredbe)

    def log(self):
        disjunkti = [self.disjunkt()]
        while self >> PSK.ILI: disjunkti.append(self.disjunkt())
        return disjunkti[0] if len(disjunkti) == 1 else Disjunkcija(disjunkti)

    def disjunkt(self):
        if self >> PSK.LKONST: return self.zadnji
        elif self >> PSK.LIME:
            ime = self.zadnji
            if self >= PSK.OTV: return self.poziv(ime)
            else: return ime
        lijevo = self.aritm()
        manje = self.pročitaj(PSK.JEDNAKO, PSK.MANJE) ** PSK.MANJE
        desno = self.aritm()
        return Usporedba(bool(manje), lijevo, desno)

    def poziv(self, ime):
        if ime in self.funkcije: funkcija = self.funkcije[ime]
        else: raise SemantičkaGreška(
            'Nedeklarirana funkcija ' + ime.sadržaj)
        return Poziv(funkcija, self.argumenti(funkcija.parametri))

    def argumenti(self, parametri):
        arg = []
        prvi = True
        for parametar in parametri:
            self.pročitaj(PSK.OTV if prvi else PSK.ZAREZ)
            prvi = False
            if parametar ** PSK.LIME: arg.append(self.log())
            else: arg.append(self.aritm())
        self.pročitaj(PSK.ZATV)
        return arg

    def aritm(self):
        članovi = [self.član()]
        while self >> {PSK.PLUS, PSK.MINUS}:
            operator = self.zadnji
            dalje = self.član()
            članovi.append(dalje if operator ** PSK.PLUS else Suprotan(dalje))
        return članovi[0] if len(članovi) == 1 else Zbroj(članovi)

    def član(self):
        if self >> PSK.MINUS: return Suprotan(self.faktor())
        faktori = [self.faktor()]
        while self >> PSK.ZVJEZDICA: faktori.append(self.faktor())
        return faktori[0] if len(faktori) == 1 else Umnožak(faktori)

    def faktor(self):
        if self >> PSK.BROJ: return self.zadnji
        elif self >> PSK.AIME:
            ime = self.zadnji
            if self >= PSK.OTV: return self.poziv(ime)
            else: return ime
        else:
            self.pročitaj(PSK.OTV)
            u_zagradi = self.aritm()
            self.pročitaj(PSK.ZATV)
            return u_zagradi

    start = program


def izvrši(funkcije, *argv):
    program = Token(PSK.AIME, 'program')
    if program in funkcije:
        izlazna_vrijednost = funkcije[program].pozovi(argv)
        print('Program je vratio: ', izlazna_vrijednost)
    else: raise SemantičkaGreška('Nema glavne funkcije "program"')


class Funkcija(AST('ime parametri naredba')):
    def pozovi(self, argumenti):
        lokalni = dict(zip(self.parametri, argumenti))
        print(self.parametri)
        print("ASURBANIPAL",argumenti)
        print(lokalni)
        print()
        try: self.naredba.izvrši(lokalni)
        except Povratak as exc: return exc.povratna_vrijednost

class Poziv(AST('funkcija argumenti')):
    def vrijednost(self, mem):
        print(self.argumenti)
        print(mem)

        print()
        arg = [argument.vrijednost(mem) for argument in self.argumenti]
        return self.funkcija.pozovi(arg)

class Grananje(AST('uvjet željeno naredba inače')):
    def izvrši(self, mem):
        print("mem",mem)
        if self.uvjet.vrijednost(mem) == self.željeno: self.naredba.izvrši(mem)
        else: self.inače.izvrši(mem)

class Petlja(AST('uvjet željeno naredba')):
    def izvrši(self, mem):
        while self.uvjet.vrijednost(mem) == self.željeno:
            self.naredba.izvrši(mem)

class Blok(AST('naredbe')):
    def izvrši(self, mem):
        for naredba in self.naredbe: naredba.izvrši(mem)

class Pridruživanje(AST('ime pridruženo')):
    def izvrši(self, mem):
        mem[self.ime] = self.pridruženo.vrijednost(mem)
        print(self.ime.sadržaj)
        print("go_____r______e")

class Vrati(AST('što')):
    def izvrši(self, mem):
        print(self.što)
        print(self.što.vrijednost(mem))
        raise Povratak(self.što.vrijednost(mem))

class Disjunkcija(AST('disjunkti')):
    def vrijednost(self, mem):
        return any(disjunkt.vrijednost(mem) for disjunkt in self.disjunkti)

class Usporedba(AST('manje lijevo desno')):
    def vrijednost(self, mem):
        l, d = self.lijevo.vrijednost(mem), self.desno.vrijednost(mem)
        return l < d if self.manje else l == d

class Zbroj(AST('pribrojnici')):
    def vrijednost(self, mem):
        return sum(pribroj.vrijednost(mem) for pribroj in self.pribrojnici)

class Suprotan(AST('od')):
    def vrijednost(self, mem): return -self.od.vrijednost(mem)

class Umnožak(AST('faktori')):
    def vrijednost(self, mem):
        p = 1
        for faktor in self.faktori: p *= faktor.vrijednost(mem)
        return p


class Povratak(Exception):
    @property
    def povratna_vrijednost(self): return self.args[0]


faktorijela = PseudokodParser.parsiraj(pseudokod_lexer('''
fakt(x) = (
    f = 1,
    dok nije x = 0 (
        f = f*x,
        x = x-1
    ),
    vrati f
)
Neparan(x) = (
    N = laž,
    dok nije x = 0 (
        x = x - 1,
        ako je N N = laž inače N = istina
    ),
    vrati N
)
program() = (
    s = 0,
    t = 0,
    a = 14,
    b=7,
    dok je t < 9 (
        ako je Neparan(t) s = s + fakt(t),
        t = t + 1
    ),
    vrati s
)
'''))
print(faktorijela)
print()
izvrši(faktorijela, {})
