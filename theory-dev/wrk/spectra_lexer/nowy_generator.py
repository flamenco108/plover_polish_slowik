#!/usr/bin/env python3
import argparse
import collections
import os
import re


# {"Fonem": ("Lewa ręka", "Prawa ręka")}
fonemy_spółgłoskowe = {"b": ("P~", "B"),
                       "bi": ("PJ~", "BW"),
                       "c": ("ZT", "C"),
                       "ci": ("ZTJ", "CW"),
                       "ch": ("X", "CB"),
                       "chi": ("XJ", "CBW"),
                       "cz": ("PV", "CL"),
                       "czi": ("PVJ", "CLW"),
                       "ć": ("TJ", "TW"),
                       "d": ("T~", "BT"),
                       "di": ("TJ~", "BTW"),
                       "dz": ("ZT~", "C"),  # Dodałem
                       "dzi": ("ZTJ~", "CW"),  # Dodałem
                       "dź": ("ZTJ~", "LST"),
                       "dż": ("PV~", "CLW"),
                       "f": ("F", "W"),
                       "fi": ("FJ", "W"),
                       "g": ("K~", "G"),
                       "gi": ("KJ~", "GW"),
                       "h": ("X~", "CBW"),  # Zamieniłem z XK~
                       "hi": ("XJ~", "CBW"),  # Zamieniłem z XKJ~
                       "j": ("J", "CR"),
                       "ji": ("J", "CRW"),
                       "k": ("K", "GW"),
                       "ki": ("KJ", "GW"),
                       "l": ("L", "L"),
                       "li": ("LJ", "LW"),
                       "ł": ("LJ", "LB"),
                       "łi": ("LJ", "LBW"),
                       "m": ("KP", "CS"),
                       "mi": ("KPJ", "CSW"),
                       "n": ("TV", "CL"),
                       "ni": ("TVJ", "CLW"),
                       "ń": ("TVJ", "CLW"),
                       # Tu zmieniłem prawą, bo nie ma "P" po prawej stronie
                       "p": ("P", "RG"),
                       "pi": ("PJ", "RGW"),
                       "q": ("KV", "GWY"),
                       "r": ("R", "R"),
                       "ri": ("RJ", "RW"),
                       "rz": ("RJ", "RBW"),
                       "s": ("S", "S"),
                       "si": ("SJ", "SW"),
                       "sz": ("TP", "RB"),
                       "ś": ("SJ", "SW"),
                       "t": ("T", "T"),
                       "ti": ("TJ", "TW"),
                       "v": ("V", "W"),
                       "vi": ("VJ", "W"),
                       "w": ("V", "W"),
                       "wi": ("VJ", "W"),
                       "x": ("SK", "BSG"),
                       "xi": ("SKJ", "BSGW"),
                       "z": ("Z", "BS"),
                       "zi": ("ZJ", "BSW"),
                       "ź": ("ZJ", "BSW"),
                       "ż": ("TP~", "RBW")}


# {"Fonem": ("Środek", "Prawa ręka")}
fonemy_samogłoskowe = {"a": ("A", "TO"),
                       "ą": ("~O", "TW"),
                       "e": ("E", "TWOY"),
                       "ę": ("E~", "OY"),
                       "i": ("I", ""),
                       "o": ("AU", "O"),
                       "ó": ("U", ""),
                       # Tutaj zabrałem prawą rękę z "i"
                       "u": ("U", "WY"),
                       "y": ("IAU", "Y")}


# indeksy kolumn po lewej stronie od 0
lewe_indeksy_klawiszy = {"X": 0, "F": 0, "XF": 0, "XZ": 0, "FS": 0, "XFZS": 0,
                         "Z": 1, "S": 1, "ZS": 1,
                         "K": 2, "T": 2, "KT": 2,
                         "P": 3, "V": 3, "PV": 3,
                         "L": 4, "R": 4, "LR": 4,
                         "~": 5, "*": 5,
                         "J": 6}


# indeksy kolumn po prawej stronie od 0
prawe_indeksy_klawiszy = {"~": 5, "*": 5,
                          "C": 6, "R": 6, "CR": 6,
                          "L": 7, "B": 7, "LB": 7,
                          "S": 8, "G": 8, "SG": 8,
                          "T": 9, "W": 9, "TW": 9, "TO": 9, "WY": 9, "TWOY": 9,
                          "O": 10, "Y": 10, "OY": 10}

def niemalejące(fonemy_lewe, fonemy_prawe):
    inwersja_użyta = False
    indeksy = lewe_indeksy_klawiszy
    indeksy_fonemów_lewe = [(0, "", "")]
    for i in range(len(fonemy_lewe)):
        fonem = fonemy_lewe[i]
        minimalny_indeks_klawisza = 5
        print(f"Fonem:{fonem} w {fonemy_lewe}")
        for klawisz in fonemy_spółgłoskowe[fonem][0]:
            bieżący_indeks = indeksy[klawisz]
            if bieżący_indeks < minimalny_indeks_klawisza:
                minimalny_indeks_klawisza = bieżący_indeks
        if minimalny_indeks_klawisza != indeksy_fonemów_lewe[-1][0]:
            indeksy_fonemów_lewe.append((minimalny_indeks_klawisza, i, fonem))
    indeksy_fonemów_lewe = indeksy_fonemów_lewe[1:]
    (jest_niemalejący, gdzie_nie_jest) = ciąg_niemalejący(indeksy_fonemów_lewe[1:])
    if not jest_niemalejący:
        tymczasowy = indeksy_fonemów_lewe[gdzie_nie_jest[1] - 1]
        indeksy_fonemów_lewe[gdzie_nie_jest[1] - 1] = indeksy_fonemów_lewe[gdzie_nie_jest[1]]
        indeksy_fonemów_lewe[gdzie_nie_jest[1]] = tymczasowy
        inwersja_użyta = True
        (jest_niemalejący, gdzie_nie_jest) = ciąg_niemalejący(indeksy_fonemów_lewe)
        if not jest_niemalejący:
            return (False, 0, gdzie_nie_jest)

    indeksy = prawe_indeksy_klawiszy
    indeksy_fonemów_prawe = [(5, "", "")]
    for i in range(len(fonemy_prawe)):
        fonem = fonemy_prawe[i]
        minimalny_indeks_klawisza = 10
        for klawisz in fonemy_spółgłoskowe[fonem][1]:
            bieżący_indeks = indeksy[klawisz]
            if bieżący_indeks < minimalny_indeks_klawisza:
                minimalny_indeks_klawisza = bieżący_indeks
        if minimalny_indeks_klawisza != indeksy_fonemów_prawe[-1][0]:
            indeksy_fonemów_prawe.append((minimalny_indeks_klawisza, i, fonem))
    indeksy_fonemów_prawe = indeksy_fonemów_prawe[1:]
    (jest_niemalejący, gdzie_nie_jest) = ciąg_niemalejący(indeksy_fonemów_prawe)
    if not jest_niemalejący and not inwersja_użyta:
        tymczasowy = indeksy_fonemów_prawe[gdzie_nie_jest[1] - 1]
        indeksy_fonemów_prawe[gdzie_nie_jest[1] - 1] = indeksy_fonemów_prawe[gdzie_nie_jest[1]]
        indeksy_fonemów_prawe[gdzie_nie_jest[1]] = tymczasowy
        inwersja_użyta = True
        (jest_niemalejący, gdzie_nie_jest) = ciąg_niemalejący(indeksy_fonemów_prawe)
        if not jest_niemalejący:
            return (False, 1, gdzie_nie_jest)
        return (True, None, None)
    elif jest_niemalejący:
        return (True, None, None)
    return (False, 1, gdzie_nie_jest)

def ciąg_niemalejący(ciąg):
    długość_ciągu = len(ciąg)
    if długość_ciągu < 2:
        return (True, None)
    else:
        for i in range(1, długość_ciągu):
            if ciąg[i][0] < ciąg[i-1][0]:
                return (False, ciąg[i])
    return (True, None)

class Logger:
    def __init__(self, plik_logowania, rozmiar_bufora=1024, pisz_na_ekran=True):
        self.plik_logowania = open(plik_logowania, 'a', buffering=rozmiar_bufora)
        self.pisz_na_ekran = pisz_na_ekran

    def __exit__(self):
        self.plik_logowania.flush()
        self.plik_logowania.close()

    def _loguj(self, poziom_logowania, dane):
        self.plik_logowania.write(f"{poziom_logowania}: {dane}\n")

    def info(self, dane):
        self._loguj("INF", dane)
        if self.pisz_na_ekran:
            print(f"INF: {dane}")

    def debug(self, dane):
        self._loguj("DBG", dane)

    def error(self, dane):
        self._loguj("ERR", dane)
        if self.pisz_na_ekran:
            print(f"ERR: {dane}")


class SłownikDomyślny(collections.UserDict):
    def __init__(self, domyślna_fabryka=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not callable(domyślna_fabryka) and domyślna_fabryka is not None:
            raise TypeError('Pierwszy argument musi być wykonywalny albo None')
        self.domyślna_fabryka = domyślna_fabryka

    def __missing__(self, klucz):
        if self.domyślna_fabryka is None:
            raise KeyError(klucz)
        if klucz not in self:
            self[klucz] = self.domyślna_fabryka(klucz)
        return self[klucz]


class Generator():
    def __init__(self, log, słownik_ostateczny, sylaby_słowa):
        self.log = log
        # {tekst: {"Kombinacja": niedopasowanie}}
        self.słownik = słownik_ostateczny
        self._samogłoski = re.compile(r'[aąeęioóuy]+')
        self.sylaby_słowa = sylaby_słowa
        self.fonemy_sylaby = SłownikDomyślny(lambda x: self.rozłóż_sylabę(x))
        self.kombinacje = dict()
        self._zainicjalizuj_kombinacje()
        self.loguj_postęp_co = 10000 # Będzie log po tylu wygenerowanych słowach
        self.postęp = 0
        self.debug_niedodane = 0
        self.minimum_kombinacji_per_słowo = 1

    def _zainicjalizuj_kombinacje(self):
        self.log.info("Inicjalizuję bazę generatora")
        for (tekst, kombinacje) in self.słownik.items():
            for kombinacja in kombinacje.keys():
                self.kombinacje[kombinacja] = tekst
        self.log.info("Baza zainicjalizowana w pamięci")

    def rozłóż_sylabę(self, sylaba: str):
        m = self._samogłoski.search(sylaba)
        if not m:
            błąd = f"sylaba {sylaba} bez samogłosek"
            self.log.debug(błąd)
            return (sylaba, "", "")
        śródgłos = fonemy(m.group(0))

        # Wykryj "i" które tylko zmiękcza, przesuń je do nagłosu
        zmiękczenie = False
        if len(śródgłos) > 1 and śródgłos[0].startswith('i'):
            śródgłos = śródgłos[1:]
            zmiękczenie = True
        nagłos = fonemy(re.split(self._samogłoski, sylaba)[0], zmiękczenie)
        wygłos = fonemy(re.split(self._samogłoski, sylaba)[1])

        self.log.debug(f"Rozłożyłem {sylaba} na N: {nagłos} Ś: {śródgłos} W: {wygłos}")
        return (nagłos, śródgłos, wygłos)

    def _dopasuj_kombinacje(self, tekst, kombinacje):
        for (kombinacja, niedopasowanie) in kombinacje:
            obecny_właściciel = None
            if kombinacja not in self.kombinacje.keys():
                self.kombinacje[kombinacja] = tekst
            else:
                obecny_właściciel = self.kombinacje[kombinacja]
                if obecny_właściciel == tekst:
                    continue
                kombinacje_właściciela = self.słownik[obecny_właściciel]
                ilość_kombinacji_właściciela = len(kombinacje_właściciela.keys())
                if ilość_kombinacji_właściciela <= self.minimum_kombinacji_per_słowo:
                    continue
                else:
                    obecne_niedopasowanie = kombinacje_właściciela[kombinacja]
                    minimalne_niedopasowanie_u_właściciela = obecne_niedopasowanie
                    for obca_kominacja, obce_niedopasowanie in kombinacje_właściciela.items():
                        if obce_niedopasowanie < minimalne_niedopasowanie_u_właściciela:
                            minimalne_niedopasowanie_u_właściciela = obce_niedopasowanie
                            break
                        elif obce_niedopasowanie == minimalne_niedopasowanie_u_właściciela and\
                             obca_kombinacja != kombinacja:
                            minimalne_niedopasowanie_u_właściciela = obce_niedopasowanie -1
                            break
                    if obecne_niedopasowanie > minimalne_niedopasowanie_u_właściciela:
                        kombinacje_właściciela.pop(kombinacja)
                        self.słownik(tekst)[kombinacja] = niedopasowanie
                        self.kombinacje[kombinacja] = tekst
                
    def wygeneruj_kombinacje(self, słowo, limit_prób=1):
        self.postęp += 1
        # TODO:
        # - rozdzielić obliczanie kombinacji dla lewej i prawej ręki (i dla środka)
        # - dodawanie * i ~ powinno być opóźnione, żeby wsadzić je w środek kombinacji
        # - zaimplementować kombinacje z rosnącą liczbą wykluczonych fonemów
        # - zaimplementować sprawdzanie czy kombinacja jest uporządkowana
        # - zaimplementować Inversion Rule
        # - przywrócić obliczanie niedopasowania na zasadzie ile brakuje fonemów w kombinacji
        # Wtedy dodawanie wyrazów więcej niż jednosylabowych powinno być prostsze

        # Dla 'w', 'z'
        try:
            sylaby = self.sylaby_słowa[słowo]
        except KeyError as e:
            if len(słowo) == 1:
                sylaby = [słowo]
            else:
                raise KeyError(f"Nie znam sylab, {e}")
        ilość_sylab = len(sylaby)
        kombinacje = []
        if ilość_sylab == 1:
            # Wszystkie literki powinny być dopasowane
            # nagłos - lewa, śródgłos - kciuk(i), wygłos - prawa
            self.log.debug(f"Sylaby: {sylaby}")
            (nagłos, śródgłos, wygłos) = self.fonemy_sylaby[sylaby[0]]
            ręka_lewa = RękaLewa(self.log)
            ręka_prawa = RękaPrawa(self.log)
    
            kombinacja_środkowa = ""
            # kombinacja_prawa = ""
            # wagi_lewe = collections.defaultdict(lambda:0)
            wagi_środek = collections.defaultdict(lambda:0)
            # wagi_prawe = collections.defaultdict(lambda:0)
            pierwsza = True
            ostatnia = False
            self.log.info(f"{słowo}")
            (czy_niemalejące, który_nie, gdzie_nie) = niemalejące(nagłos, wygłos)
            if not czy_niemalejące:
                if który_nie == 0:  # coś z nagłosem nie tak
                    nowy_nagłos = []
                    for fonem in nagłos:
                        if fonem == gdzie_nie[2]:
                            continue
                        nowy_nagłos.append(fonem)
                        nagłos = nowy_nagłos
                else:  # coś z wygłosem nie tak
                    nowy_wygłos = []
                    for fonem in wygłos:
                        if fonem == gdzie_nie[2]:
                            continue
                        nowy_wygłos.append(fonem)
                        wygłos = nowy_wygłos
                (czy_niemalejące, który_nie, gdzie_nie) = niemalejące(nagłos, wygłos)
            if czy_niemalejące:
                for fonem in nagłos:
                    znaki = fonemy_spółgłoskowe[fonem][0]
                    # for znak in znaki:
                        # wagi_lewe[klawisz] += 1
                        # kombinacja_lewa += klawisz
                    ręka_lewa.zbuduj_kombinację(znaki, pierwsza)
                    pierwsza = False
                for fonem in śródgłos:
                    znaki = fonemy_samogłoskowe[fonem][0]
                    for znak in znaki:
                        wagi_środek[znak] += 1
                    kombinacja_środkowa += znaki
                długość_wygłosu = len(wygłos)
                for i in range(długość_wygłosu):
                    fonem = wygłos[i]
                    if i + 1 == długość_wygłosu:
                        ostatnia = True
                    znaki = fonemy_spółgłoskowe[fonem][1]
                    # for klawisz in klawisze:
                    #     wagi_prawe[klawisz] += 1
                    # kombinacja_prawa += klawisze
                    ręka_prawa.zbuduj_kombinację(znaki, ostatnia)
                    kombinacje.append((ręka_lewa.akord_lewy() + kombinacja_środkowa + ręka_prawa.akord_prawy(), 0))
            else:
                self.log.error(f"{słowo} - niepowodzenie generacji {który_nie}{gdzie_nie} ({nagłos}|{wygłos})")

            # TODO: trzeba zbudować kombinacje z klawiszy w sposób zorganizowany
            # jest_tylda = False
            # if "~" in kombinacja_lewa + kombinacja_prawa:
            #     jest_tylda = True
            #     kombinacja_lewa = usuń_tyldy(kombinacja_lewa)
            #     kombinacja_prawa = usuń_tyldy(kombinacja_prawa)
            #     kombinacja_środkowa = dodaj_tyldę(kombinacja_środkowa)
            # if niemalejąca(kombinacja_lewa) and niemalejąca(kombinacja_prawa, prawa=True):
                # kombinacje.append((palce(kombinacja_lewa, lewa=True) + palce(kombinacja_środkowa) + palce(kombinacja_prawa, prawa=True), 0))
                # pass
                
            # else:
            #     # Tu kombinuj
            #     self.debug_niedodane += 1
            #     self.log.error(f"Nie dodałbym kombinacji dla {słowo}")

        elif ilość_sylab == 2:
            pass
            # Może zabraknąć U (i Ó) na końcU
            # Nagłos pierwszej - lewa, jej śródgłos - kciuk(i), wygłos i druga sylaba - prawa
            kombinacja_lewa = ""
            kombinacja_środkowa = ""
            kombinacja_prawa = ""
            self.log.debug(f"rozbijam {sylaby[0]}")
            (nagłos, śródgłos, wygłos) = self.fonemy_sylaby[sylaby[0]]
            for litera in nagłos:
                # self.log.debug(f"N: {litera}")
                kombinacja_lewa += fonemy_spółgłoskowe[litera][0]
                # self.log.debug(f"2>1N:{kombinacja_lewa}")
            for litera in śródgłos:
                # self.log.debug(f"Ś: {litera}")
                kombinacja_środkowa += fonemy_samogłoskowe[litera][0]
                # self.log.debug(f"2>1Ś:{kombinacja_środkowa}")
            for litera in wygłos:
                # self.log.debug(f"W: {litera}")
                kombinacja_prawa += fonemy_spółgłoskowe[litera][1]
                # self.log.debug(f"2>1W:{kombinacja_prawa}")

            (nagłos, śródgłos, wygłos) = self.fonemy_sylaby[sylaby[1]]
            for litera in nagłos:
                kombinacja_prawa += fonemy_spółgłoskowe[litera][1]
                # self.log.debug(f"2>2N:{kombinacja_prawa}")
            for litera in śródgłos:
                kombinacja_prawa += fonemy_samogłoskowe[litera][1]
                # self.log.debug(f"2>2Ś:{kombinacja_prawa}")
            for litera in wygłos:
                kombinacja_prawa += fonemy_spółgłoskowe[litera][1]
                # self.log.debug(f"2>2W:{kombinacja_prawa}")

            kombinacja_lewa = dedup(kombinacja_lewa)  # TODO docelowo wywalić
            kombinacja_środkowa = dedup(kombinacja_środkowa)  # TODO docelowo wywalić
            kombinacja_prawa = dedup(kombinacja_prawa)  # TODO docelowo wywalić
            kombinacja = kombinacja_lewa+kombinacja_środkowa+kombinacja_prawa
            kombinacje.append((kombinacja, 0))
            self.log.info(f"2> {słowo}: {kombinacja}")
        elif ilość_sylab == 3:
            # Pierwsza sylaba bez samogłosek, druga na pograniczu z samogłoską na kciukach
            # Trzecia w prawej ręce
            pass
        else:
            # Tylko dwie ostatnie sylaby z samogłoskami (chyba, że bez końcowego U)
            # Zaczynają się Briefy...
            pass
        if kombinacje:
            self._dopasuj_kombinacje(słowo, kombinacje)
            
        if self.postęp % self.loguj_postęp_co == 0:
            self.log.info(f"{self.postęp}: {słowo} - wygenerowano")

    # Ponieważ sortowanie może trochę zająć, warto zapisać co już mamy
    # w razie gdyby skończył się zapas RAMu
    def generuj_do_pliku(self):
        for (kombinacja, tekst) in self.kombinacje.items():
            yield f'"{kombinacja}": "{tekst}"\n'


def main():
    parser = argparse.ArgumentParser(
        description='Generuj słownik na podstawie słów podzielonych na sylaby',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--log', default='wyniki/generuj_slownik.log',
                        help='log przebiegu generacji słownika')
    parser.add_argument('--frekwencja', default='../../data/frekwencja_Kazojc.csv',
                        help='dane frekwencyjne (w formacie linii csv: "słowo",częstość)')
    parser.add_argument('--slowa', default='../../data/slownik',
                        help='słowa do utworzenia słownika podzielone na sy=la=by')
    parser.add_argument('--baza', default='',#wyniki/spektralny-slowik.json',
                        help='początkowy plik słownika w formacie JSON')
    parser.add_argument('--slownik', default='wyniki/spektralny-slowik.json',
                        help='wynikowy plik JSON do załadowania do Plovera')
    args = parser.parse_args()

    # Upewnij się że foldery istnieją
    for plik_wyjściowy in [args.log, args.slownik]:
        folder = os.path.dirname(plik_wyjściowy)
        if folder != '':
            os.makedirs(folder, exist_ok=True)

    # Spróbuj otworzyć plik logu
    log = Logger(args.log)
    log.info(f'Argumenty: {str(args)[10:-1]}')

    # Słownik wyjściowy, dane w formie:
    # {tekst: {"Kombinacja": niedopasowanie}}
    słownik = collections.defaultdict(dict)
    numer_linii = 0
    if args.baza:
        log.info(f"Czytam bazę słownika z {args.baza}")
        for linia in czytaj_linie_pliku(args.baza):
            numer_linii += 1
            linia = linia.strip()
            if not linia or linia.startswith('#') or linia.startswith('{') or linia.startswith('}') :
                continue
            (kombinacja, wyraz) = czytaj_znaki_między_cudzysłowem(linia)
            słownik[wyraz] = {kombinacja: 0}
        log.info(f"Baza wczytana")

    sylaby_słowa = dict()
    numer_linii = 0
    for linia in czytaj_linie_pliku(args.slowa):
        numer_linii += 1
        linia = linia.strip()
        if linia.startswith('#'):
            continue

        sylaby = linia.split('=')
        tekst = ''.join(sylaby)
        sylaby_słowa[tekst] = sylaby #klawisze_słowa
        if numer_linii % 10000 == 0 and numer_linii != 0:
            log.info(f'Przetwarzanie linii {numer_linii}: {linia}')

    log.info("Wczytałem sylaby, generuję klawisze...")
    istniejące_słowa = słownik.keys()
    generator = Generator(log, słownik, sylaby_słowa)
    for linia in czytaj_linie_pliku(args.frekwencja):
        linia = linia.strip()
        słowo = linia.split('"')[1]
        frekwencja = int(linia.split(',')[1])
        if słowo in istniejące_słowa or słowo.isnumeric():
            continue
        generator.wygeneruj_kombinacje(słowo)
    # log.info(f"Niedodanych jednosylabowych: {generator.debug_niedodane}")

    log.info("Słownik utworzony, zapisuję...")
    with open(args.slownik[:-5]+"_niesortowany.json", 'w', buffering=1024000) as plik_wynikowy:
        plik_wynikowy.write('{\n')
        for linia in generator.generuj_do_pliku():
            plik_wynikowy.write(linia)
        plik_wynikowy.write('}\n')

    # Posortuj słowa według kolejności klawiszy
    log.info("Zapis niesortowanego słownika zakończony, sortuję...")
    kolejność = '/#XFZSKTPVLR-JE~*IAUCRLBSGTWOY'
    posortowany_słownik = collections.OrderedDict(
        sorted(generator.kombinacje.items(), key=lambda wpis:
               [kolejność.index(k) for k in wpis[0]]))

    log.info("Sortowanie zakończone, zapisuję...")
    with open(args.slownik, 'w', buffering=1024000) as plik_wynikowy:
        plik_wynikowy.write('{\n')
        for klawisze, tekst in posortowany_słownik.items():
            plik_wynikowy.write(f'"{klawisze}": "{tekst}"\n')
        plik_wynikowy.write('}\n')
    log.info("Fajrant")


def czytaj_znaki_między_cudzysłowem(wiersz):
    lista = []
    token = ""
    cudzysłów_otwarty = False
    poprzedni_backslash = False
    for znak in wiersz:
        if cudzysłów_otwarty and znak != '"':
            token+=znak
            poprzedni_backslash = False
        elif cudzysłów_otwarty and znak == '"' and not poprzedni_backslash:
            lista.append(token)
            token = ""
            cudzysłów_otwarty = False
        elif cudzysłów_otwarty and znak == '"' and poprzedni_backslash:
            token+=znak
            poprzedni_backslash = False
        elif cudzysłów_otwarty and znak == '\\':
            token+=znak
            poprzedni_backslash = True
        elif not cudzysłów_otwarty and znak == '"':
            cudzysłów_otwarty = True
            poprzedni_backslash = False
        elif not cudzysłów_otwarty and znak != '"':
            poprzedni_backslash = False
            continue
    return lista


# TODO tego nie powinno tu być wcale
def dedup(string):
    s = set()
    list = []
    for ch in string:
        if ch not in s:
            s.add(ch)
            list.append(ch)

    return ''.join(list)        


def split(word):
    return [char for char in word]


def fonemy(string, zmiękczenie = False):
    fonemy_dwuznakowe = {"b": ["i"],
                         "c": ["h", "i", "z"],
                         "d": ["i", "z", "ź", "ż"],
                         "f": ["i"],
                         "g": ["i"],
                         "h": ["i"],
                         "j": ["i"],
                         "k": ["i"],
                         "l": ["i"],
                         "ł": ["i"],
                         "m": ["i"],
                         "n": ["i"],
                         "p": ["i"],
                         "r": ["i", "z"],
                         "s": ["i", "z"],
                         "t": ["i"],
                         "w": ["i"],
                         "z": ["i"]}
    znaki = split(string)
    if zmiękczenie:
        znaki.append("i")

    wynik = []
    i = 0
    ilość_znaków = len(znaki)
    while i < ilość_znaków:
        znak = znaki[i]
        if znak in fonemy_dwuznakowe.keys():
            if (i+1 < ilość_znaków) and znaki[i+1] in fonemy_dwuznakowe[znak]:
                następny_znak = znaki[i+1]
                if zmiękczenie and ((znak == "c" and następny_znak in ["z", "h"])\
                  or (znak == "d" and następny_znak =="z")):
                    if (i+2 < ilość_znaków) and znaki[i+2] == "i":
                        i += 3
                        wynik.append(znak + następny_znak + "i")
                    else:
                        i += 2
                        wynik.append(znak + następny_znak)
                else:
                    i += 2
                    wynik.append(znak + następny_znak)
            else:
                i += 1
                wynik.append(znak)
        else:
            i += 1
            wynik.append(znak)
    return wynik


def czytaj_linie_pliku(plik):
    for linia in open(plik, "r"):
        yield linia


# def dodaj_tyldę(kombinacja):
#     wynik = ""
#     for i in range(len(kombinacja)):
#         if kombinacja[i] in ["J", "E"]:
#             wynik += kombinacja[i]
#     wynik += kombinacja
#     return wynik+kombinacja[len(wynik):]


# def usuń_tyldy(kombinacja):
#     wynik = []
#     for znak in kombinacja:
#         if znak != "~":
#             wynik.append(znak)
#     return wynik


# def palce(kombinacja, lewa=False, prawa=False):
#     if lewa:
#         ręka_lewa = collections.defaultdict(set)
#         indeksy = lewe_indeksy_klawiszy
#         for klawisze in kombinacja:
            

class Klawisz:
    def __init__(self, znak, indeks, kombinacja_id, waga=1, samodzielny=0, początkowy=False, końcowy=False):
        self.znak = znak
        self.waga = waga
        if początkowy or końcowy:
            self.waga += 1
        self.indeks = indeks
        self.kombinacja = set()
        self.kombinacja.add(kombinacja_id)
        self.początkowy = początkowy
        self.końcowy = końcowy
        self.samodzielny = samodzielny

    def aktualizuj(self, inny_klawisz, id_kombinacji, długość_kombinacji):
        self.kombinacja.add(id_kombinacji)
        samodzielny = 0
        if długość_kombinacji == 1:
            samodzielny = 1
        self.samodzielny += samodzielny
        if inny_klawisz.początkowy:
            self.początkowy = True
        if inny_klawisz.końcowy:
            self.końcowy = True

class Kombinacja:
    def __init__(self, id_kombinacji, znaki, prawa=False,
                 pierwsza_kombinacja=False,
                 ostatnia_kombinacja=False):
        self.indeksy = lewe_indeksy_klawiszy
        if prawa:
            self.indeksy = prawe_indeksy_klawiszy
        self.id_kombinacji = id_kombinacji
        self.klawisze = dict()
        self.długość_kombinacji = len(znaki)
        for znak in znaki:
            indeks = self.indeksy[znak]
            samodzielny = 0
            waga = 1
            if self.długość_kombinacji == 1:
                samodzielny = 1
            self.klawisze[znak] = Klawisz(znak,
                                          indeks,
                                          id_kombinacji,
                                          waga,
                                          samodzielny,
                                          pierwsza_kombinacja,
                                          ostatnia_kombinacja)
    def zwróć_klawisze(self):
        for klawisz in self.klawisze.values():
            yield klawisz
            

class RękaLewa:
    def __init__(self, log):
        self.log = log
        self.palec_mały = Palec(log, ["X", "F", "Z", "S"])
        self.palec_serdeczny = Palec(log, ["K", "T"])
        self.palec_środkowy = Palec(log, ["P", "V"])
        self.palec_wskazujący = Palec(log, ["L", "R", "~", "*"])
        self.kciuk_lewy = Palec(log, ["J", "E"])  # tutaj do logiki ważne jest tylko "J"
        self.kombinacje = []  # Można tylko dodawać elementy do kombinacji, żeby IDki się zgadzały!!!
        self.dostępne_id_kombinacji = 0

    def zbuduj_kombinację(self, znaki, pierwsza=False, ostatnia=False):
        id_kombinacji = self.dostępne_id_kombinacji
        self.dostępne_id_kombinacji += 1
        kombinacja = Kombinacja(self, id_kombinacji,
                                znaki, prawa=False,
                                pierwsza_kombinacja=pierwsza,
                                ostatnia_kombinacja=ostatnia)

    def palec_dla_indeksu(self, indeks):
        if indeks in [0, 1]:
            return self.palec_mały
        elif indeks == 2:
            return self.palec_serdeczny
        elif indeks == 3:
            return self.palec_środkowy
        elif indeks in [4, 5]:
            return self.palec_wskazujący
        elif indeks == 6:
            return self.kciuk_lewy
        else:
            self.log.error(f"Lewa ręka nie ma palca dla indeksu: {indeks}")


    def zbuduj_kombinację(self, znaki, pierwsza=False):
        id_kombinacji = self.dostępne_id_kombinacji
        self.dostępne_id_kombinacji += 1
    # def __init__(self, id_kombinacji, znaki, prawa=False,
    #              pierwsza_kombinacja=False,
    #              ostatnia_kombinacja=False):
        kombinacja = Kombinacja(id_kombinacji,
                                znaki, prawa=False,
                                pierwsza_kombinacja=pierwsza,
                                ostatnia_kombinacja=False)
        self.dodaj_kombinację(kombinacja)

    def dodaj_kombinację(self, kombinacja):
        self.kombinacje.append(kombinacja)
        for klawisz in kombinacja.zwróć_klawisze():
            palec = self.palec_dla_indeksu(klawisz.indeks)
            if klawisz.znak not in palec.wspierane_kombinacje:
                self.log.error(f"Nie mogę dodać klawisza {klawisz.znak} {klawisz.indeks}")
            else:
                palec.dodaj_klawisz(klawisz, kombinacja.id_kombinacji, kombinacja.długość_kombinacji)

    def akord_lewy(self):
        tekst = self.palec_mały.tekst()
        tekst += self.palec_serdeczny.tekst()
        tekst += self.palec_środkowy.tekst()
        tekst += self.palec_wskazujący.tekst()
        tekst += self.kciuk_lewy.tekst()
        return tekst
        
    # def dodaj_tyldę(self):
    #     # TODO zrobić obsługę tyldy
    #     return False
        
    # def dodaj_gwiazdkę(self):
    #     # TODO zrobić obsługę tyldy
    #     return False
        

class RękaPrawa:
    def __init__(self, log):
        self.log = log
        self.palec_wskazujący = Palec(log, ["~", "*", "C", "R"])
        self.palec_środkowy = Palec(log, ["L", "B"])
        self.palec_serdeczny = Palec(log, ["S", "G"])
        self.palec_mały = Palec(log, ["T", "W", "O", "Y"])
        self.kombinacje = []  # Można tylko dodawać elementy do kombinacji, żeby IDki się zgadzały!!!
        self.dostępne_id_kombinacji = 0

    def palec_dla_indeksu(self, indeks):
        if indeks in [5, 6]:
            return self.palec_wskazujący
        elif indeks == 7:
            return self.palec_środkowy
        elif indeks == 8:
            return self.palec_serdeczny
        elif indeks in [9, 10]:
            return self.palec_mały
        else:
            self.log.error(f"Prawa ręka nie ma palca dla indeksu: {indeks}")

    def zbuduj_kombinację(self, znaki, ostatnia=False):
        id_kombinacji = self.dostępne_id_kombinacji
        self.dostępne_id_kombinacji += 1
        kombinacja = Kombinacja(id_kombinacji,
                                znaki, prawa=True,
                                pierwsza_kombinacja=False,
                                ostatnia_kombinacja=ostatnia)
        self.dodaj_kombinację(kombinacja)

    def dodaj_kombinację(self, kombinacja):
        self.kombinacje.append(kombinacja)
        for klawisz in kombinacja.zwróć_klawisze():
            palec = self.palec_dla_indeksu(klawisz.indeks)
            if klawisz.znak not in palec.wspierane_kombinacje:
                self.log.error(f"Nie mogę dodać klawisza {klawisz.znak} {klawisz.indeks}")
            else:
                palec.dodaj_klawisz(klawisz, kombinacja.id_kombinacji, kombinacja.długość_kombinacji)

    def akord_prawy(self):
        tekst = self.palec_wskazujący.tekst()
        tekst += self.palec_środkowy.tekst()
        tekst += self.palec_serdeczny.tekst()
        tekst += self.palec_mały.tekst()
        return tekst

    # def dodaj_tyldę(self):
    #     # TODO zrobić obsługę tyldy
    #     return False
        
    # def dodaj_gwiazdkę(self):
    #     # TODO zrobić obsługę tyldy
    #     return False
        

class Palec:
    def __init__(self, log, obsługiwane_klawisze):
        self.log = log
        self.wspierane_kombinacje = [obsługiwane_klawisze[0],
                                     obsługiwane_klawisze[1],
                                     obsługiwane_klawisze[0]+obsługiwane_klawisze[1]]
        if len(obsługiwane_klawisze) == 4:
            self.wspierane_kombinacje += [obsługiwane_klawisze[2],
                                          obsługiwane_klawisze[3],
                                          obsługiwane_klawisze[2]+obsługiwane_klawisze[3],
                                          obsługiwane_klawisze[0]+obsługiwane_klawisze[2],
                                          obsługiwane_klawisze[1]+obsługiwane_klawisze[3],
                                          obsługiwane_klawisze[0]+obsługiwane_klawisze[1]+\
                                          obsługiwane_klawisze[2]+obsługiwane_klawisze[3]]
        self.obsługiwane_klawisze = obsługiwane_klawisze
        self.klawisze = {}


    def dodaj_klawisz(self, klawisz, id_kombinacji, długość_kombinacji):
        if klawisz.znak not in self.obsługiwane_klawisze:
            self.log.error(f"{klawisz.znak} nieobsługiwany ({self.obsługiwane_klawisze})")
        elif klawisz.znak not in self.klawisze.keys():
            self.klawisze[klawisz.znak] = klawisz
        else:
            self.klawisze[klawisz.znak].aktualizuj(klawisz, id_kombinacji, długość_kombinacji)

    def pierwszy_lub_ostatni_klawisz(self):
        for klawisz in self.klawisze:
            if klawisz.początkowy or klawisz.końcowy:
                return klawisz.znak
        return None

    def tekst(self):
        ile_klawiszy_użytych = len(self.klawisze)
        tekst = ""
        if ile_klawiszy_użytych == 3:
            # Musimy coś wywalić, pierwszy i ostatni musi zostać
            musi_zostać = self.pierwszy_lub_ostatni_klawisz()
            if not musi_zostać:
                log.error("Żaden klawisz nie jest pierwszy ani ostatni")
                # TODO czy jest taka możliwość?

            for klawisz in self.klawisze:
                if klawisz.znak == musi_zostać:
                    continue
                if musi_zostać+klawisz.znak in self.wspierane_kombinacje:
                    return musi_zostać+klawisz.znak
                elif klawisz.znak+musi_zostać in self.wspierane_kombinacje:
                    return klawisz.znak+musi_zostać
            log.error(f"Nie znalazłem prawidłowej kombinacji dla {self.klawisze.keys()}")
        else:
            for klawisz in self.obsługiwane_klawisze:
                if klawisz in self.klawisze.keys():
                    tekst += klawisz
        return tekst
                


if __name__ == '__main__':
    main()

