class c0Parser(Parser):
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
        self.pročitaj(c0.OTV)
        if self >> c0.ZATV: parametri = []
        elif self >> {c0.BOOL, c0.INT}:
            if self.zadnji ** c0.BOOL:
                """
                označavamo ime i tip / postoji opcija da se u nezavisan directory
                stavlja tip uz ime.. ako ne mislimo raditi scope
                (vrstu varijable, je li globalna ili samo za blok naredbi)
                """
                parametri = [[self.pročitaj(c0.IME), 1]]
            elif: parametri = [[self.pročitaj(c0.IME), 0]]
            while self >> c0.ZAREZ:
                self.pročitaj(c0.BOOL, c0.INT)
                if self.zadnji ** c0.BOOL:
                    parametri.append([self.pročitaj(c0.IME), 1])
                elif: parametri.append([self.pročitaj(c0.IME), 0])
            self.pročitaj(c0.ZATV)
        else: self.greška()
        self.pročitaj(c0.VOTV)
        naredba = self.naredba()
        return Funkcija(ime, parametri, naredba) #MOŽDA TREBA STAVITI I TIP funkcije

    def naredba(self):
        if self >> {}
