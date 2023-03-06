# program bude verziovaný v GIT
import random
from enum import Enum
import time
import datetime

class Hodnota_pole(Enum):
    neprirazene = "-"
    krizek = "X"
    kolecko = "O"
    
class Hraci_pole():
    # třída pro základní prvek hracího plánu
    def __init__(self):
        self.stav = Hodnota_pole.neprirazene

    def __get__(self):
        return self.stav

    def __set__(self, stav):
        if self.stav == Hodnota_pole.neprirazene:
            self.stav = stav
            return True
        return False
    
    def __str__(self):
        return " {0} ".format(self.stav.value)


class Hraci_plan():
    # třída pro hrací plán s metodami pro vykreslování plánu, kontroly výhry
    # sjednocuje všechny metody obsluhující pracovní plán

    pocet_obsazenych_poli = 0
    pocet = 0
    zprava = ""
    
    def __init__(self, rozmer):
        self.rozmer = rozmer
        self.plan = []
        for _ in range(rozmer):
            radek = []
            for _ in range(rozmer):
                radek.append(Hraci_pole())
            self.plan.append(radek)

    

    def _vycisti_obrazovku(self):
        import sys as _sys
        import subprocess as _subprocess
        if _sys.platform.startswith("win"):
            _subprocess.call(["cmd.exe", "/C", "cls"])
        else:
            _subprocess.call(["clear"])
        print("* * * * * * * * * * * * * * * * * * * * *")
        print("        P  I  š  K  V  O  R  K  Y        ")
        print("* * * * * * * * * * * * * * * * * * * * *")

    
    def zobraz_akt_stav(self):
        self._vycisti_obrazovku()
        for i in range(self.rozmer):
            for j in range(self.rozmer):
                print(self.plan[i][j], end = " ")
            print("\n")
            
    def aktualizuj_plan(self, x, y, symbol):
        if self.plan[x][y].__set__(symbol):
            self.pocet_obsazenych_poli += 1
            return True
        return False

    def validuj(self, x, y, symbol):
        # validační metoda na shodu symbolu a konce hry
        if self.plan[x][y].__get__() == symbol:
            self.pocet += 1
            if self.pocet == 5:
                return True
        else:
            self.pocet = 0
        return False

    def radek(self, x, symbol):
        # kontrola výhry v řádku
        # kontrola probíha jenom v řádku, kde proběhnul tah
        self.pocet = 0
        for i in range(self.rozmer):
            if self.validuj(x, i, symbol):
                self.zprava = "výhra v řádku {0}".format(x + 1)
                return True
        return False

    def sloupec(self, y, symbol):
        # kontrola výhry v sloupci
        # kontrola probíha jenom v sloupci, kde proběhnul tah
        self.pocet = 0
        for i in range(self.rozmer):
            if self.validuj(i, y, symbol):
                self.zprava = "výhra v sloupci {0}".format(y + 1)
                return True
        return False
    
    def souradnice_xy(self, x, y, typ):
        # nastavení krajního bodu pro validaci diagonály
        if typ == "D":
            if y >= x:
                # vpravo od hlavní diagonály
                self.x = 0
                self.y = y - x
            else:
                # vlevo od hlavní diagonály
                self.x = x - y
                self.y = 0
        else:
            if y <= self.rozmer - x:
                # vlevo od hlavní diagonály
                self.x = x + y - 1
                self.y = 0
            else:
                # vpravo od hlavní diagonály
                self.x = self.rozmer - 1
                self.y = y - (self.rozmer - x - 1)


    def diagonala_dolu(self, x, y, symbol):
        # kontrola výhry v diagonále směrem dolů
        # kontrola probíha jenom v diagonále, kde proběhnul tah
        self.souradnice_xy(x, y, "D")
        self.pocet = 0
        while self.x < self.rozmer and self.y < self.rozmer:
            if self.validuj(self.x, self.y, symbol):
                self.zprava = "výhra v diagonále zleva doprava směrem dolů procházející posledním hraným bodem [{0},{1}]".format(x + 1, y + 1)
                return True
            self.x += 1
            self.y += 1
        return False
    
    def diagonala_nahoru(self, x, y, symbol):
        # kontrola výhry v diagonále směrem nahoru
        # kontrola probíha jenom v diagonále, kde proběhnul tah
        self.souradnice_xy(x, y, "N")
        self.pocet = 0
        while self.x >= 0 and self.y < self.rozmer:
            if self.validuj(self.x, self.y, symbol):
                self.zprava = "výhra v diagonále zleva doprava směrem nahoru procházející posledním hraným bodem [{0},{1}] ".format(x + 1, y + 1)
                return True
            self.x -= 1
            self.y += 1
        return False
    
    def diagonala(self, x, y, symbol):
        # sjednocení validace diagonál
        return self.diagonala_dolu(x, y, symbol) or self.diagonala_nahoru(x, y, symbol)
    
    def konec_hry(self, x, y, symbol):
        # validace ukončení hry
        return self.radek(x, symbol) or self.sloupec(y, symbol) or self.diagonala(x, y, symbol)



   
class Hrac():
    # třída pro instanci hráče
    def __init__(self, jmeno, symbol):
        self.jmeno = jmeno
        self.symbol = symbol
        
    def __str__(self):
        return "{0} hraje se symbolem {1}".format(self.jmeno, self.symbol.value)

class Hra():
    # třída pro hru piškvorky
    # sjednocuje metody pro řízení hry kromě metody pro realizaci tahu hráče - definovaná v potomkovi
    def __init__(self, hraci_plan):
        self.hraci_plan = hraci_plan
    
    @staticmethod
    def nacti_cislo(text_zadani, text_chyba, rozsah):
        # validace vstupních údajů z klávesnice
        spatne = True
        while spatne:
            try:
                cislo = int(input(text_zadani))
                spatne = False
            except ValueError:
                print(text_chyba)
            else:
                if cislo < 0 or cislo > rozsah:
                    print("cislo musi byt v intervale od 1-{0}".format(rozsah - 1))
                    spatne = True
        else:
            return cislo - 1
    
    def zobraz_vysledky(self, hrac):
        # výstup výsledků hry na obrazovku
        print("* * * * * * * * * * * * * * * * * * * * *")
        if self.hraci_plan.zprava == "":
            if self.hraci_plan.pocet_obsazenych_poli == self.hraci_plan.rozmer ** 2:
                print("KONEC HRY - hra nemá vítěze")
        else:
            print("KONEC HRY:\n - vyhrál/a {0}\n - {1}".format(hrac.jmeno, self.hraci_plan.zprava))
        print(" - počet vyplněných polí: {0}\n".format(self.hraci_plan.pocet_obsazenych_poli))
        print("* * * * * * * * * * * * * * * * * * * * *")


    def odpocitavani(self):
        print("POZOR - za 3 sekundy štartujeme")
        time.sleep(3)

    def spusti_hru(self):
        # obsluha hry Piškvorky
        hrac = self.hrac1
        self.tah(hrac)
        while not self.hraci_plan.konec_hry(self.x, self.y, hrac.symbol):
            if hrac == self.hrac1:
                hrac = self.hrac2
            else:
                hrac = self.hrac1
            self.tah(hrac)
        self.zobraz_vysledky(hrac)

class Hra_automat(Hra):
    # potomek třídy Hra
    # rozšiřuje předka o metodu simulující tahu hráče automaticky
    def __init__(self, hraci_plan):
        super().__init__(hraci_plan)

    def tah(self, hrac):
        # metoda simuluje tah hráče automaticky(generování náhodných čísel)
        self.x = random.randint(0, self.hraci_plan.rozmer-1)
        self.y = random.randint(0, self.hraci_plan.rozmer-1)
        while not self.hraci_plan.aktualizuj_plan(self.x, self.y, hrac.symbol):
            self.x = random.randint(0, self.hraci_plan.rozmer-1)
            self.y = random.randint(0, self.hraci_plan.rozmer-1)
        self.hraci_plan.zobraz_akt_stav()
    
    def inicializace_hrace(self):
        self.hrac1 = Hrac("Spejbl", Hodnota_pole.krizek)
        self.hrac2 = Hrac("Hurvínek", Hodnota_pole.kolecko)
        print(self.hrac1)
        print(self.hrac2)
        self.odpocitavani()

class Hra_manual(Hra):
    # potomek třídy Hra
    # rozšiřuje předka o metodu simulující tahu hráče manuálně

    def __init__(self, hraci_plan):
        super().__init__(hraci_plan)

    def tah(self, hrac):
        # metoda simuluje tah hráče manuálne (z klávesnice)
        print(hrac)
        self.x = self.nacti_cislo("Zadej suřadnici x: ", "Nezadali jste číslo", self.hraci_plan.rozmer)
        self.y = self.nacti_cislo("zZadej suřadnici y: ", "Nezadali jste číslo", self.hraci_plan.rozmer)
        while not self.hraci_plan.aktualizuj_plan(self.x, self.y, hrac.symbol):
            self.x = self.nacti_cislo("Zadej suřadnici x: ", "Nezadali jste číslo", self.hraci_plan.rozmer)
            self.y = self.nacti_cislo("Zadej suřadnici y: ", "Nezadali jste číslo", self.hraci_plan.rozmer)
        self.hraci_plan.zobraz_akt_stav()
    
    def inicializace_hrace(self):
        jmeno = input("Zadej jméno prvního hráče: ")
        self.hrac1 = Hrac(jmeno, Hodnota_pole.krizek)
        jmeno = input("Zadej jméno druhého hráče: ")
        self.hrac2 = Hrac(jmeno, Hodnota_pole.kolecko)
        print(self.hrac1)
        print(self.hrac2)
        self.odpocitavani()

def main():
    hraci_plan = Hraci_plan(10)
    hraci_plan._vycisti_obrazovku()
    zpusob_hry = input("\nZvol způsob hry - automat/manuál (A/M): ")
    zpusob_hry = zpusob_hry.lower()
    if zpusob_hry == "a":
        hra = Hra_automat(hraci_plan)
        hra.inicializace_hrace()
    else:
        hra = Hra_manual(hraci_plan)
        hra.inicializace_hrace()
    hra.spusti_hru()

main()

