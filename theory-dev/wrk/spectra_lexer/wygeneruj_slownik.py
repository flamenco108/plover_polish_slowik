#!/usr/bin/env python3
import random
import argparse
import collections
import os
import re
from typing import Any, Dict, TextIO, Tuple


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


class DyspozytorKlawiszy:
    def __init__(self, log, zasady):
        self.log = log
        log.info("Zbuduj słowniki do szukania zasad dla fragmentów sylaby")
        self.zasady = zasady
        self.nagłosy = dict()
        self.śródgłosy = dict()
        self.wygłosy = dict()
        self._klawisze_dla_sylaby = dict()
        self._samogłoski = re.compile(r'[aąeęioóuy]+')

        for zasada in zasady.values():
            if zasada.f_nagłos or zasada.f_śródgłos or zasada.f_wygłos:
                uzupełnij_tekst(zasada, zasady)
            else:
                continue

            if zasada.f_nagłos:
                self.nagłosy[zasada.tekst] = zasada.id
            elif zasada.f_śródgłos:
                self.śródgłosy[zasada.tekst] = zasada.id
            elif zasada.f_wygłos:
                self.wygłosy[zasada.tekst] = zasada.id

    def klawisze_dla_sylaby(self, sylaba: str):
        if not sylaba in self._klawisze_dla_sylaby.keys():
            self.rozłóż_sylabę(sylaba)
        return self._klawisze_dla_sylaby[sylaba]
    
    def rozłóż_sylabę(self, sylaba: str):
        self.log.debug(f"Definiuję klawisze dla sylaby: {sylaba}")
        m = self._samogłoski.search(sylaba)
        if not m:
            błąd = f"sylaba {sylaba} bez samogłosek"
            self.log.error(błąd)
            raise ValueError(błąd)
        nagłos = re.split(self._samogłoski, sylaba)[0]
        śródgłos = m.group(0)
        wygłos = re.split(self._samogłoski, sylaba)[1]

        # Wykryj "i" które tylko zmiękcza, przesuń je do nagłosu
        if len(śródgłos) > 1 and śródgłos.startswith('i'):
            nagłos = nagłos + śródgłos[0]
            śródgłos = śródgłos[1:]

        if nagłos != '' and (nagłos not in self.nagłosy):
            raise ValueError(f'brak definicji ONSET dla "{nagłos}"')
        if śródgłos != '' and (śródgłos not in self.śródgłosy):
            raise ValueError(f'brak definicji NUCLEUS dla "{śródgłos}"')
        if wygłos != '' and (wygłos not in self.wygłosy):
            raise ValueError(f'brak definicji CODA dla "{wygłos}"')

        self._klawisze_dla_sylaby[sylaba] = ((self.zasady[self.nagłosy[nagłos]].klawisze if nagłos != '' else ''),
            (self.zasady[self.śródgłosy[śródgłos]].klawisze if śródgłos != '' else ''),
            (self.zasady[self.wygłosy[wygłos]].klawisze if wygłos != '' else ''))
        self.log.debug(f"klawisze dla sylaby: {sylaba} zdefiniowane")


class PalcoKombinator():
    def __init__(self, log, zasady):
        self.palce = dict()
        # X: ch
        self.palce["LMały"] = ("XZFS", "XF", "ZS", "XZ", "FS", "X", "F", "Z", "S")
        self.palce["LSerdeczny"] = ("KT", "K", "T")
        self.palce["LŚrodkowy"] = ("PV", "P", "V")
        self.palce["LWskazujący"] = ("LR", "L~", "R*", "L", "R", "~", "*", "~*", "LR~*")
        self.palce["LKciuk"] = ("JE", "EI", "J", "E", "I")
        self.palce["PKciuk"] = ("IA", "AU", "I", "A", "U")
        # CR: j
        self.palce["PWskazujący"] = ("CR", "~C", "*R", "~", "*", "C", "R", "~*", "CR~*")
        # LB: ł
        self.palce["PŚrodkowy"] = ("LB", "L", "B")
        self.palce["PSerdeczny"] = ("SG", "S", "G")
        # TW: ą,ć; W: f; TO: a; TOWY: e; OY: ę; WY: i
        self.palce["PMały"] = ("TOWY", "OY", "TO", "WY", "TW", "T", "W", "O", "Y")
        self.nazwy_palców = ["LMały", "LSerdeczny", "LŚrodkowy", "LWskazujący", "LKciuk", "PKciuk", "PWskazukący", "PŚrodkowy", "PSerdeczny", "PMały"]

    def wykombinuj(self, zważone_sylaby, limit_prób):
        kombinacje = []
        ilość_sylab = len(zważone_sylaby)
        while limit_prób > 0:
            limit_prób -= 1
            zważone_klawisze = self._zważ_klawisze(zważone_sylaby[0])
            pożądane_klawisze = zważone_klawisze.clone()
            palce = ["LWskazujący", "LŚrodkowy", "LSerdeczny", "LMały", "LKciuk", "PKciuk", "PWskazukący", "PŚrodkowy", "PSerdeczny", "PMały"]
            (kombinacja, niedopasowanie) = self._dodaj_klawisze_wg_palców(palce, pożądane_klawisze)
            if ilość_sylab == 1:
                kombinacje.append((kombinacja, niedopasowanie))
                continue
            zważone_klawisze = self._zważ_klawisze(zważone_sylaby[-1])
            pożądane_klawisze = zważone_klawisze.clone()
            palce = ["PWskazujący", "PŚrodkowy", "PSerdeczny", "PMały", "PKciuk", "LKciuk", "LWskazukący", "LŚrodkowy", "LSerdeczny", "LMały"]
            (kombinacja, niedopasowanie) = self._dodaj_klawisze_wg_palców(palce, pożądane_klawisze)
            if ilość_sylab == 2:
                # TODO: trzeba dopisać do nowe klawisze do istniejącej rozpoczętej kombinacji
                kombinacje.append((kombinacja, niedopasowanie))
                continue
            zważone_klawisze = self._zważ_klawisze(zważone_sylaby[1:-1])
            pożądane_klawisze = zważone_klawisze.clone()
            palce = self.nazwy_palców.clone()
            random.shuffle(palce)
            (kombinacja, niedopasowanie) = self._dodaj_klawisze_wg_palców(palce, pożądane_klawisze)
            kombinacje.append((kombinacja, niedopasowanie))
            if "R" in kombinacja and ("L" in kombinacja or "C" in kombinacja):
                kombinacje.append((kombinacja+"~*", niedopasowanie + 2))
            elif "R" in kombinacja and "C" not in kombinacja):
                kombinacje.append((kombinacja+"*", niedopasowanie + 1))
            elif "R" not in kombinacja and (("L" in kombinacja and "B" not in kombinacja) or "C" in kombinacja):
                kombinacje.append((kombinacja+"~", niedopasowanie + 1))
        return kombinacje

    def _zważ_klawisze(self, zważone_sylaby):
        zważone_klawisze = collections.defaultdict(lambda: 0)
        kombinacje = []
        for (sylaba, ((nagłos, n_waga),
                      (śródgłos, ś_waga),
                      (wygłos, w_waga))) in zważone_sylaby:
            for klawisz in nagłos:
                zważone_klawisze[klawisz] += n_waga
            for klawisz in śródgłos:
                zważone_klawisze[klawisz] += ś_waga
            for klawisz in wygłos:
                zważone_klawisze[klawisz] += w_waga
        return zważone_klawisze

    def _dodaj_klawisze_wg_palców(self, palce, zważone_klawisze, priorytetowe_klawisze=""):
        kombinacja = ""
        pożądane_klawisze = priorytetowe_klawisze.clone()
        for palec in palce:
            for kombo in self.palce[palec]
                wszystkie_użyte = True
                for klawisz in kombo:
                    if klawisz not in pożądane_klawisze:
                        wszystkie_użyte = False
                        break
                if wszystkie_użyte:
                    kombinacja += kombo
                    for klawisz in kombo:
                        pożądane_klawisze.pop(klawisz)
                    break
            if len(pożądane_klawisze.keys()) == 0:
                break
        niedopasowanie = 0
        for ile_brakuje in pożądane_klawisze.values()
            niedopasowanie += ile_brakuje
        return (kombinacja, niedopasowanie)


def Ważniak():
    def __init__(self):
        self.wagi_pierwszej_sylaby = (2, 1, 1)
        self.wagi_ostatniej_sylaby = (1, 1, 2)
        self.wagi_środkowej_sylaby = (1, 0, 1)
        self.extra_wagi_akcentowanej_sylaby = (1, 1, 0)
    def zważ_sylaby(self, sylaby):
        zważone_sylaby = []
        ilość_sylab = len(sylaby)
        (sylaba, (nagłos, śródgłos, wygłos))) = sylaby[0]
        zważona = (sylaba, ((nagłos, self.wagi_pierwszej_sylaby[0]),
                  (śródgłos, self.wagi_pierwszej_sylaby[1]),
                   (wygłos, self.wagi_pierwszej_sylaby[2])))
        zważone_sylaby.append(zważona)
        zważona = None
        if ilość_sylab == 1:
            return zważone_sylaby
        if ilość_sylab == 2:
            (sylaba, (nagłos, śródgłos, wygłos))) = sylaby[-1]
             zważona = (sylaba, ((nagłos, self.wagi_ostatniej_sylaby[0]),
                    (śródgłos, self.wagi_ostatniej_sylaby[1]),
                    (wygłos, self.wagi_ostatniej_sylaby[2])))
             zważone_sylaby.append(zważona)
             return zważone_sylaby
        for (sylaba, (nagłos, śródgłos, wygłos))) in sylaby[1:-1]:
            zważona = (sylaba, ((nagłos, self.wagi_środkowej_sylaby[0]),
                                (śródgłos, self.wagi_środkowej_sylaby[1]),
                                (wygłos, self.wagi_środkowej_sylaby[2])))
            zważone_sylaby.append(zważona)
        (sylaba, ((nagłos, n_waga), (śródgłos, ś_waga), (wygłos, w_waga)))) = sylaby[-2]
         doważona = (sylaba, ((nagłos, n_waga + self.wagi_akcentowanej_sylaby[0]),
                        (śródgłos, ś_waga + self.wagi_akcentowanej_sylaby[1]),
                        (wygłos, w_waga + self.wagi_akcentowanej_sylaby[2])))
         zważone_sylaby[-2] = doważona
         return zważone_sylaby

            
class Generator():
    def __init__(self, log, słownik_ostateczny):
        self.log = log
        self.palco_komb = PalcoKombinator()
        self.ważniak = Ważniak()
        # {tekst: {"Kombinacja": niedopasowanie}}
        self.słownik = słownik_ostateczny
        self.kombinacje = dict()
        self._zainicjalizuj_kombinacje()
        self.loguj_postęp_co = 100 # Będzie log po tylu wygenerowanych słowach
        self.postęp = 0
        self.minimum_kombinacji_per_słowo = 4

    def _zainicjalizuj_kombinacje(self):
        self.log("Inicjalizuję bazę generatora")
        for (tekst, kombinacje) in self.słownik:
            for kombinacja in kombinacje.keys():
                self.kombinacje[kombinacja] = tekst
        self.log("Baza zainicjalizowana w pamięci")

    def _dopasuj_kombinacje(tekst, kombinacje):
        for (kombinacja, niedopasowanie) in kombinacje:
            obecny_właściciel = None
            if kombinacja in self.kombinacje.keys():
                obecny_właściciel = self.kombinacje[kombinacja]
                if obecny_właściciel == tekst:
                    continue
                kombinacje_właściciela = self.słownik(obecny_właściciel)
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
                        self.słownik(obecny_właściciel) = kombinacje_właściciela
                        self.słownik(tekst)[kombinacja] = niedopasowanie
                        self.kombinacje[kombinacja] = tekst
                
    def wygeneruj_kombinacje((tekst, sylaby), limit_prób=100):
        self.postęp += 1
        zważone_sylaby = self.ważniak.zważ_sylaby(sylaby)
        kombinacje = self.palco_komb.wykombinuj(zważone_sylaby, limit_prób)
        self._dopasuj_kombinacje(tekst, kombinacje)
            
        if self.postęp % self.loguj_postęp_co == 0:
            log.info(f"{self.postęp}: {tekst} - wygenerowano")

    # Ponieważ sortowanie może trochę zająć, warto zapisać co już mamy
    # w razie gdyby skończył się zapas RAMu
    def generuj_do_pliku():
        for (tekst, kombinacje) in self.słownik:
            for (kombinacja, niedopasowanie) in kombinacje:
                yield f'"{kombinacja}": "{tekst}"\n'


def main():
    parser = argparse.ArgumentParser(
        description='Generuj konkretne zasady teorii i słownik'
        'na podstawie szablonu teorii i słów podzielonych na sylaby',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--teoria-szablon', default='assets/rules.cson.in',
                        help='szablon zasad teorii')
    parser.add_argument('--teoria', default='wyniki/rules.cson',
                        help='gotowe zasady teorii')
    parser.add_argument('--log', default='wyniki/generuj_slownik.log',
                        help='log przebiegu generacji słownika')
    parser.add_argument('--frekwencja', default='../../data/frekwencja_Kazojc.csv',
                        help='dane frekwencyjne (w formacie linii csv: "słowo",częstość)')
    parser.add_argument('--slowa', default='../../data/slownik',
                        help='słowa do utworzenia słownika podzielone na sy=la=by')
    parser.add_argument('--slownik', default='wyniki/spektralny-slowik.json',
                        help='wynikowy plik JSON do załadowania do Plovera')
    args = parser.parse_args()

    # Upewnij się że foldery istnieją
    for plik_wyjściowy in [args.teoria, args.log, args.slownik]:
        folder = os.path.dirname(plik_wyjściowy)
        if folder != '':
            os.makedirs(folder, exist_ok=True)

    # Spróbuj otworzyć plik logu
    log = Logger(args.log)
    log.info(f'Argumenty: {str(args)[10:-1]}')

    zasady = dict()
    def czytaj_linie_pliku(plik):
        for linia in open(plik, "r"):
            yield linia

    numer_linii = 0
    for linia in czytaj_linie_pliku(args.teoria_szablon):
        numer_linii += 1
        obcięta_linia = linia.strip()

        # Jeśli to pusta linia, przejdź dalej
        if not obcięta_linia:
            continue

        #Opuszczamy linie komentarza i nawiasy
        if obcięta_linia.startswith('#') or\
            obcięta_linia.startswith('{') or\
            obcięta_linia.startswith('}'):
            continue
        log.info(f"Parsuję linię {numer_linii}: {obcięta_linia}")
        (id_zasady, klawisze, litery, alt, flagi, info) = czytaj_znaki_między_cudzysłowem(obcięta_linia)
        zasada = Zasada(id_zasady, klawisze, litery, alt, flagi, info, numer_linii)
        zasady[id_zasady] = zasada
        
    # Inna zasada w tekście: ciąg dowolnych znaków wewnątrz nawiasów
    inna_zasada = re.compile(r'\(([^()]+)\)')

    log.info("Złóż wszystkie zasady bez klawiszy z innych zasad")
    # Możliwe że będzie konieczne kilka iteracji jeśli jest kilka poziomów definicji
    while True:
        zmieniono_zasadę = False  # Wykryj iteracje bez szans na ukończenie zadania

        for zasada in zasady.values():
            if not zasada.bez_klawiszy():
                continue

            użyte_id = set()
            tekst = zasada.litery
            log.info(f"Uzupełniam {zasada}")
            while True:
                # Szczegóły znalezionej innej zasady
                m = inna_zasada.search(tekst)
                if not m:
                    # log.error(f"{zasada} - nie wiem jak uzupełnić klawisze")
                    break
                inne_id = m.group(1).split('|')[1] \
                    if '|' in m.group(1) else m.group(1)
                użyte_id.add(inne_id)
                log.info("Obsługa składni: (litery|id), wstaw id w nawiasach")
                podmiana = ('(' + inne_id + ')') \
                    if '|' in m.group(1) else zasady[m.group(1)].litery
                tekst = tekst[:m.start()] + podmiana + tekst[m.end():]

            użyte_id_do_uzupełnienia = {
                id for id in użyte_id if zasady[id].bez_klawiszy()}

            if len(użyte_id_do_uzupełnienia) == 0:
                log.info("Mamy wszystkie składowe, można utworzyć ten wpis")
                utworzone_klawisze = połącz_klawisze(
                    *[zasady[id].klawisze for id in użyte_id])
                zasada.klawisze = utworzone_klawisze
                zmieniono_zasadę = True
                log.info(f'{zasada} wygenerowana')

        if not jest_pusta_zasada(zasady):
            log.info("Wszystkie zasady uzupełnione.")
            break
        if not zmieniono_zasadę:
            pozostałe = [id for id, zasada in zasady.items()
                         if zasada.bez_klawiszy()]
            błąd = f'Nie udało się znaleźć klawiszy dla zasad: {", ".join(pozostałe)}'
            log.error(błąd)
            raise ValueError(błąd)

    with open(args.teoria, 'w', buffering=10240) as zasady_cson:
        zasady_cson.write(f'# UWAGA: Plik auto-generowany na podstawie {args.teoria_szablon}\n')
        zasady_cson.write("{\n")
        for z in zasady.values():
            zasady_cson.write(z.jako_linia_do_pliku())
        zasady_cson.write("}\n")

    # Słownik wyjściowy, dane w formie:
    # {tekst: set{("Kombinacja", niedopasowanie)}}
    # ten format będzie potrzebny, jeśli magia ma zadziałać
    słownik = defaultdict(lambda: dict{})
    for zasada in zasady.values():
        if not zasada.f_słownik:
            continue  # Nie twórz dla niej nowego słowa
        uzupełnij_tekst(zasada, zasady)
        słownik[zasada.tekst][zasada.klawisze] = 0

    dyspozytor = DyspozytorKlawiszy(log, zasady)
    
    # jeśli magia ma zapracować na chleb, musi skorzystać z pośredniaka
    # dane w formie: {"słowo": [(sylaba, (nagłos, śródgłos, wygłos)))]}
    # czyli dla każdego słowa mamy listę tupli, każdy element listy opisuje sylabę
    # długość listy to ilość sylab w słowie
    pośredniak = dict()
    numer_linii = 0
    for linia in czytaj_linie_pliku(args.slowa):
        numer_linii += 1
        linia = linia.strip()
        if linia.startswith('#'):
            continue

        sylaby = linia.split('=')
        klawisze_słowa = []
        nierozłożona_sylaba = False
        for sylaba in sylaby:
            try:
                klawisze_sylaby = dyspozytor.klawisze_dla_sylaby(sylaba)
                klawisze_słowa.append((sylaba, klawisze_sylaby))
            except ValueError as e:
                log.error(f'Nie znaleziono rozkładu dla sylaby "{sylaba}" słowa "{linia}": {e.args[0]}')
                nierozłożona_sylaba = True

        if not nierozłożona_sylaba:
            tekst = ''.join(sylaby)
            pośredniak[tekst] = klawisze_słowa
            # klawisze = '/'.join(klawisze_słowa)
            # print(f'Rozłożono {linia} na {klawisze}')
            # if (klawisze not in słownik): # and (klawisze not in słownik_ze_słów):
            #     słownik[klawisze] = tekst
            # TODO trzeba wymyślić jakiś sposób na eleganckie znajdowanie innych
            # (najlepiej krótszych) kombinacji klawiszy,
            # żeby słowa nie przepadały z powodu duplikacji akordów
            # else:
            #     stare = słownik[klawisze]
            #     nowe = tekst

            #     frekw_stare = frekwencja[stare] if stare in frekwencja else -1
            #     frekw_nowe = frekwencja[nowe] if nowe in frekwencja else -1

            #     if frekw_nowe > frekw_stare:
            #         słownik[klawisze] = nowe

            #     log.error(f'Duplikat dla klawiszy `{klawisze}`: "{tekst}"{(" (frekwencja " + str(frekw_nowe) + ")") if frekw_nowe != -1 else ""}, już jest "{stare}"{(" (frekwencja " + str(frekw_stare) + ")") if frekw_stare != -1 else ""} {", zamieniam na nowe" if frekw_nowe > frekw_stare else ""}')

        if numer_linii % 10000 == 0 and numer_linii != 0:
            log.info(f'Przetwarzanie linii {numer_linii}: {linia}')

    log.info("Wczytałem sylaby, generuję klawisze...")
    generator = Generator(log, słownik)
    for linia in czytaj_linie_pliku(args.frekwencja):
        linia = linia.strip()
        słowo = linia.split('"')[1]
        frekwencja = int(linia.split(',')[1])
        generator.wygeneruj_kombinacje(pośredniak[słowo])

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
        plik_wynikowy.write('{\n')
    log.info("Fajrant")


class Zasada:
    def __init__(self, zid: str, klawisze: str, litery: str, alt: str, flagi: str, info: str, numer_linii: int) -> None:
        self.id = zid
        self.klawisze = klawisze
        self.litery = litery
        self.alt = alt
        self.info = info
        self.numer_linii = numer_linii

        # Wygeneruj wpis do słownika na tej podstawie
        self.f_słownik = 'DICT' in flagi
        # Zasada tylko do używania w innych zasadach, powinna mieć ~ w id
        self.f_referencyjna = 'REFERENCE' in flagi
        # Flaga UPPERCASE jest potrzebna żeby pogodzić generację słownika z lekserem dla literowania wielkich liter
        self.f_duże_litery = 'UPPERCASE' in flagi

        # Fazy sylaby na potrzeby generowania klawiszy
        self.f_nagłos = 'ONSET' in flagi
        self.f_śródgłos = 'NUCLEUS' in flagi
        self.f_wygłos = 'CODA' in flagi

        # Uzupełniony tekst do słownika (self.litery może odwoływać się do innych zasad)
        self.tekst = ''
        if not self.bez_klawiszy():
            self.tekst = self.litery

    def jako_linia_do_pliku(self) -> str:
        flagi = ""
        if self.f_słownik:
            flagi += "DICT "
        if self.f_referencyjna:
            flagi += "REFERENCE "
        if self.f_duże_litery:
            flagi += "UPPERCASE "
        if self.f_nagłos:
            flagi += "ONSET "
        if self.f_śródgłos:
            flagi += "NUCLEUS "
        if self.f_wygłos:
            flagi += "CODA "
        return f'  "{self.id}": \t["{self.klawisze}", "{self.litery}", "", "{flagi}", "{self.info}"],\n'

    def __str__(self) -> str:
        return f'{self.numer_linii}: "{self.klawisze}" -> "{self.litery} ({self.info})"'

    def bez_klawiszy(self) -> bool:
        return self.klawisze == ''


def uzupełnij_tekst(zasada: Zasada, zasady: Dict[str, Zasada]) -> None:
    """Podmień odwołania do innych zasad na tekst
    """
    tekst = zasada.litery
    inna_zasada = re.compile(r'\(([^()]+)\)')
    while True:  # Nie używam operatora := bo jest na razie zbyt świeży
        # Szczegóły znalezionej innej zasady
        m = inna_zasada.search(tekst)
        if not m:
            break
        # Obsługa składni: (litery|id), wstaw litery
        podmiana = (m.group(1).split('|')[0] if '|' in m.group(1)
                    else zasady[m.group(1)].litery)
        tekst = tekst[:m.start()] + podmiana + tekst[m.end():]

    if zasada.f_duże_litery:
        tekst = tekst.upper()

    zasada.tekst = tekst


def jest_pusta_zasada(zasady: Dict[Any, Zasada]) -> bool:
    for zasada in zasady.values():
        if zasada.bez_klawiszy():
            return True
    return False


def połącz_klawisze(*args: str) -> str:
    """Łączy klawisze dwóch akordów. Jeśli klawisz pojawia się
    przynajmniej w jednym z argumentów, to będzie w wyniku.

    Dla danego zbioru klawiszy zawsze wygeneruje taki sam tekst.

    Returns
    -------
    str
        Klawisze steno w kolejności, rozdzielone '-' tylko jeśli to niezbędne

    Raises
    ------
    ValueError
        Jeżeli któryś z argumentów zawierał nierozpoznane znaki
    """
    zestawy = list(args)
    kolejność = '#XFZSKTPVLR-JE~*IAUcrlbsgtwoy'

    indeksy = []
    for zestaw in zestawy:
        # Zamień prawą część na małe litery żeby szukać w indeksach
        strony = re.split(r'[\-JE~*IAU]+', zestaw)
        if len(strony) > 1:
            prawa: str = strony[-1]
            if len(prawa) > 0:
                zestaw = zestaw[:-len(prawa)] + prawa.lower()
        try:
            indeksy.extend([kolejność.index(k) for k in zestaw])
        except ValueError as e:
            print('Łączenie klawiszy', zestawy)
            raise e

    indeksy = sorted(list(set(indeksy)))  # Posortowane bez powtórzeń
    wynik = ''.join([kolejność[i] for i in indeksy])
    if re.search(r'[JE~*IAU]', wynik):  # Por. system.py IMPLICIT_HYPHEN_KEYS
        wynik = wynik.replace('-', '')
    elif wynik.endswith('-'):
        wynik = wynik.replace('-', '')  # Myślnik na końcu jest zbędny

    return wynik.upper()


# def wyświetl_błąd_json(zasady_json: TextIO, błąd: json.JSONDecodeError):
#     """Oznacza graficznie miejsce wystąpienia błędu JSON
#     """
#     zasady_json.seek(0)
#     linie_json = zasady_json.readlines()
#     indeks_linii = błąd.lineno - 1  # lineno to linia w pliku więc zaczyna się od 1

#     print('------------')
#     if indeks_linii >= 2:
#         print(linie_json[indeks_linii - 2], end='')
#     if indeks_linii >= 1:
#         print(linie_json[indeks_linii - 1], end='')
#     print(linie_json[indeks_linii], end='')
#     print(' '*(błąd.colno - 2), '^---', błąd.msg)
#     if indeks_linii < len(linie_json) - 1:
#         print(linie_json[indeks_linii + 1], end='')
#     if indeks_linii < len(linie_json) - 2:
#         print(linie_json[indeks_linii + 2], end='')
#     print('------------')


def wykryj_duplikaty_json(klucz_wartość: list) -> dict:
    d = {}
    for k, w in klucz_wartość:
        if k in d:
            raise ValueError(
                f'Duplikat klucza JSON `{k}`: '
                f'"{w}", już jest "{d[k]}"')
        else:
            d[k] = w
    return d


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
            
if __name__ == '__main__':
    main()

