#!/usr/bin/env python3
import argparse
import collections
import os
import re


# {"Fonem": ("Lewa ręka", "Prawa ręka")}
fonemy_spółgłoskowe = {"b": ("P~", "B"),
                       "c": ("ZT", "C"),
                       "ch": ("X", "CB"),
                       "cz": ("PV", "CL"),
                       "ć": ("TJ", "TW"),
                       "d": ("T~", "BT"),
                       "dź": ("ZTJ~", "LST"),
                       "dż": ("PV~", "CLW"),
                       "f": ("F", "W"),
                       "g": ("K~", "G"),
                       "h": ("XK~", "CBW"),
                       "j": ("J", "CR"),
                       "k": ("K", "GW"),
                       "l": ("L", "L"),
                       "ł": ("LJ", "LB"),
                       "m": ("KP", "CS"),
                       "n": ("TV", "CL"),
                       "ń": ("TVJ", "CLW"),
                       "p": ("P", "PW"),
                       "q": ("KV", "GWY"),
                       "r": ("R", "R"),
                       "rz": ("RJ", "RBW"),
                       "s": ("S", "S"),
                       "sz": ("TP", "RB"),
                       "ś": ("SJ", "SW"),
                       "t": ("T", "T"),
                       "v": ("V", "W"),
                       "w": ("V", "W"),
                       "x": ("SK", "BSG"),
                       "z": ("Z", "BS"),
                       "ź": ("ZJ", "BSW"),
                       "ż": ("TP~", "RBW")}


# {"Fonem": ("Środek", "Prawa ręka")}
fonemy_samogłoskowe = {"a": ("A", "TO"),
                       "ą": ("~O", "TW"),
                       "e": ("E", "TWOY"),
                       "ę": ("E~", "OY"),
                       "i": ("I", "WY"),
                       "o": ("AU", "O"),
                       "ó": ("U", ""),
                       "u": ("U", ""),
                       "y": ("IAU", "Y")}


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
        self.rozbite_sylaby = SłownikDomyślny(lambda x: self.rozłóż_sylabę(x))
        self.kombinacje = dict()
        self._zainicjalizuj_kombinacje()
        self.loguj_postęp_co = 10000 # Będzie log po tylu wygenerowanych słowach
        self.postęp = 0
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
            self.log.error(błąd)
            return (sylaba, "", "")
        nagłos = fonemy(re.split(self._samogłoski, sylaba)[0])
        śródgłos = fonemy(m.group(0))
        wygłos = fonemy(re.split(self._samogłoski, sylaba)[1])
        self.log.debug(f"Rozłożyłem {sylaba} na {nagłos} {śródgłos} {wygłos}")
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
            (nagłos, śródgłos, wygłos) = self.rozłóż_sylabę(sylaby[0])
            kombinacja = ""
            for litera in nagłos:
                kombinacja += fonemy_spółgłoskowe[litera][0]
                self.log.debug(f"1>N:{kombinacja}")
            for litera in śródgłos:
                kombinacja += fonemy_samogłoskowe[litera][0]
                self.log.debug(f"1>Ś:{kombinacja}")
            for litera in wygłos:
                kombinacja += fonemy_spółgłoskowe[litera][1]
                self.log.debug(f"1>W:{kombinacja}")
            kombinacja = dedup(kombinacja)  # TODO to powinno być rozwiązane w trakcie kombinowania
            kombinacje.append((kombinacja, 0))
            self.log.info(f"{słowo}: {kombinacja}")
        elif ilość_sylab == 2:
            # Może zabraknąć U (i Ó) na końcU
            # Nagłos pierwszej - lewa, jej śródgłos - kciuk(i), wygłos i druga sylaba - prawa
            kombinacja_lewa = ""
            kombinacja_środkowa = ""
            kombinacja_prawa = ""
            self.log.debug(f"rozbijam {sylaby[0]}")
            (nagłos, śródgłos, wygłos) = self.rozłóż_sylabę(sylaby[0])
            for litera in nagłos:
                self.log.debug(f"N: {litera}")
                kombinacja_lewa += fonemy_spółgłoskowe[litera][0]
                self.log.debug(f"2>1N:{kombinacja_lewa}")
            for litera in śródgłos:
                self.log.debug(f"Ś: {litera}")
                kombinacja_środkowa += fonemy_samogłoskowe[litera][0]
                self.log.debug(f"2>1Ś:{kombinacja_środkowa}")
            for litera in wygłos:
                self.log.debug(f"W: {litera}")
                kombinacja_prawa += fonemy_spółgłoskowe[litera][1]
                self.log.debug(f"2>1W:{kombinacja_prawa}")

            (nagłos, śródgłos, wygłos) = self.rozłóż_sylabę(sylaby[1])
            for litera in nagłos:
                kombinacja_prawa += fonemy_spółgłoskowe[litera][1]
                self.log.debug(f"2>2N:{kombinacja_prawa}")
            for litera in śródgłos:
                kombinacja_prawa += fonemy_samogłoskowe[litera][1]
                self.log.debug(f"2>2Ś:{kombinacja_prawa}")
            for litera in wygłos:
                kombinacja_prawa += fonemy_spółgłoskowe[litera][1]
                self.log.debug(f"2>2W:{kombinacja_prawa}")

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


def fonemy(string):
    fonemy_dwuznakowe = {"c": ["h", "z"],
                         "d": ["ź", "ż"],
                         "r": ["z"],
                         "s": ["z"]}
    znaki = split(string)
    wynik = []
    i = 0
    while i < len(znaki):
        znak = znaki[i]
        if znak in fonemy_dwuznakowe.keys():
            if (i+1 < len(znaki)) and znaki[i+1] in fonemy_dwuznakowe[znak]:
                następny_znak = znaki[i+1]
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


if __name__ == '__main__':
    main()

