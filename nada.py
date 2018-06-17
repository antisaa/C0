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
        tipF.append(ime.sadržaj : tip.sadržaj)
        self.pročitaj(c0.OTV)
        if self >> c0.ZATV: parametri = []
        elif self >> {c0.BOOL, c0.INT}:
            tip = self.zadnji.sadržaj
            parametri = [self.pročitaj(c0.IME)]
            tipV.append(self.zadnji.sadržaj : tip)
            while self >> PSK.ZAREZ:
                self.pročitaj(c0.BOOL, c0.INT)
                tip = self.zadnji.sadržaj
                parametri.append(self.pročitaj(c0.IME))
                tipV.append(self.zadnji.sadržaj : tip)
            self.pročitaj(c0.ZATV)
        else: self.greška()
        self.pročitaj(c0.VOTV)
        naredba = self.naredba()
        self.pročitaj(c0.VZATV)
        return Funkcija(ime, parametri, naredba) #MOŽDA TREBA STAVITI I TIP funkcije


    def naredba(self):
        if self >> {c0.IF, c0.WHILE}:
            petlja = self.zadnji ** c0.WHILE
