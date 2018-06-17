### BKG (ne sasvim BK:)
# program -> ime OTV parametri? ZATV JEDNAKO naredba program?
# naredba -> pridruži | VOTV naredbe? VZATV | (AKO | DOK) (JE | NIJE) log naredba
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

class c0Parser(Parser):
    """
    označavamo ime i tip, u nezavisan directory,
    stavlja tip uz ime.. ako ne mislimo raditi scope
    (vrstu varijable, je li globalna ili samo za blok naredbi)
    """
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
        """1 = BOOL, 0 = INT"""
        tip = self.pročitaj(c0.BOOL, c0.INT)
        self.logička = bool(tip ** c0.BOOL)
        ime = self.pročitaj(c0.IME)
        tipF[ime] = tip
        self.pročitaj(c0.OTV)
        if self >> c0.ZATV: parametri = []
        elif self >> {c0.BOOL, c0.INT}:
            tip = self.zadnji
            parametri = [self.pročitaj(c0.IME)]
            if self.zadnji in tipV:
                raise SemantičkaGreška("Opetovano deklaracija.")
            tipV[self.zadnji] = tip
            while self >> PSK.ZAREZ:
                self.pročitaj(c0.BOOL, c0.INT)
                tip = self.zadnji
                parametri.append(self.pročitaj(c0.IME))
                if self.zadnji in tipV:
                    raise SemantičkaGreška("Opetovano deklaracija.")
                tipV[self.zadnji] = tip
            self.pročitaj(c0.ZATV)
        else: self.greška()
        self.pročitaj(c0.VOTV)
        stmt = self.stmt()
        self.pročitaj(c0.VZATV)
        return Funkcija(ime, parametri, stmt) #MOŽDA TREBA STAVITI I TIP funkcije


    def stmt(self):
        if self >> c0.FOR:
            return self.for_()
        elif self >> c0.IF:
            petlja = self.zadnji ** c0.WHILE
        elif self >> c0.WHILE:
            petlja = self.zadnji ** c0.WHILE

        elif self >> c0.RETURN:
        elif self >> c0.VOTV:
        else:
            self.jednostavni()

    def for_(self):
        self.pročitaj(c0.OTV)
        i = self.jednostavni()
        print(i)
        print(i.sadržaj)
        self.pročitaj(c0.JEDNAKO)
        početak = self.pročitaj(c0.BROJ)
        self.pročitaj(c0.TOČKAZ)
        i2 = self.pročitaj(c0.IME)
        if i != i2: raise SemantičkaGreška('nisu podržane različite varijable')
        self.pročitaj(c0.MANJE)
        granica = self.pročitaj(c0.BROJ)
        self.pročitaj(c0.TOČKAZ)
        i3 = self.pročitaj(c0.IME)
        if i != i3: raise SemantičkaGreška('nisu podržane različite varijable')
        if self >> c0.PLUSP: inkrement = nenavedeno
        elif self >> c0.PLUSJ: inkrement = self.pročitaj(c0.BROJ)
        self.pročitaj(c0.OZATV)
        if self >> c0.VOTV:
            blok = []
            while not self >> c0.VZATV: blok.append(self.naredba())
        else: blok = [self.naredba()]
        return Petlja(i, početak, granica, inkrement, blok)

    def jednostavni(self):
        if self >> c0.IME:
            ime = self.pročitaj(c0.IME)
            if self >> {c0.PPLUS , c0.MMINUS}:
                self.pročitaj(c0.PPLUS, c0.MMINUS)

    def naziv(self):
        if self >> c0.OTV:
            self.pročitaj(c0.OTV)
            naz = self.naziv()
            self.pročitaj(c0.ZATV)
            return naz
        else:
            naz = self.pročitaj(c0.IME)
            return naz
