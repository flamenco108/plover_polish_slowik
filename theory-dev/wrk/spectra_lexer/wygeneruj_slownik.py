#!/usr/bin/env python3
import argparse
import collections
import json
import os
import re
from typing import Any, Dict, TextIO, Tuple

# from cson import CommentRemover

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

    def klawisze_dla_sylaby(self, sylaba: str) -> str:
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

        self._klawisze_dla_sylaby[sylaba] = połącz_klawisze(
            (self.zasady[self.nagłosy[nagłos]].klawisze if nagłos != '' else ''),
            (self.zasady[self.śródgłosy[śródgłos]].klawisze if śródgłos != '' else ''),
            (self.zasady[self.wygłosy[wygłos]].klawisze if wygłos != '' else ''))
        self.log.debug(f"klawisze dla sylaby: {sylaba} zdefiniowane")


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
        # (id_zasady, atrybuty_zasady) = obcięta_linia.split(':')
        (id_zasady, klawisze, litery, alt, flagi, info) = czytaj_znaki_między_cudzysłowem(obcięta_linia)
        # ponownie_obcięta_linia = obcięta_linia.rstrip(', ')
        # log.info(f"Karmie jsona: {{ {ponownie_obcięta_linia} }}")
        # (id_zasady, (klawisze, litery, alt, flagi, info))
        # result = json.loads(f'"{{ {ponownie_obcięta_linia} }}"',
        #                         object_pairs_hook=wykryj_duplikaty_json)
        # log.info(f"json gives: {result}")
        zasada = Zasada(id_zasady, klawisze, litery, alt, flagi, info, numer_linii)
        zasady[id_zasady] = zasada
        
    # with open(args.teoria_szablon) as szablon_cson:
    #     linie_szablonu = szablon_cson.readlines()

    #     if not linie_szablonu[0].startswith('#'):
    #         raise ValueError(
    #             'Pierwsza linia w pliku szablonu musi być komentarzem')
    #         # Inaczej by mi się rozjechały numery linii po dodaniu pierwszej
    #     linie_szablonu[0] = \
    #         f'# UWAGA: Plik wygenerowany automatycznie na podstawie {"rules.cson.in"}\n'

    #     szablon_cson.seek(0)
    #     zasady_json = CommentRemover(szablon_cson)
    #     # for i, linia in enumerate(zasady_json):
    #     #     print(f'{i}\t{linia}', end='')
    #     # zasady_json.seek(0)
    #     try:
    #         zasady = json.load(zasady_json,
    #                            object_pairs_hook=wykryj_duplikaty_json)
    #     except json.JSONDecodeError as e:
    #         wyświetl_błąd_json(zasady_json, e)
    #         raise e

    # print(zasady)

    # Zmień słownik list na słownik obiektów
    # with open(args.log, 'a') as log_generatora:  # Otwórz w trybie a - append, żeby dopisywać
    #     for id in zasady:
    #         # Nazwy zmiennych zgodne z spectra_lexer/doc/rules_format.txt
    #         keys, letters, alt, flags, info = tuple(zasady[id])
    #         sformatowane_klawisze = połącz_klawisze(keys)
    #         if sformatowane_klawisze != keys:
    #             log_generatora.write(
    #                 f'Klawisze szablonu: zmieniono "{keys}" na "{sformatowane_klawisze}"\n')
    #         zasady[id] = Zasada(keys, letters, flags)

    # zasady: Dict[str, Zasada]  # Informacja dla edytora kodu jaki to ma typ

    # Dopisz do zasad z której są linii
    # for i, linia in enumerate(linie_szablonu):
    #     linia = linia.strip()
    #     if linia.startswith('"'):
    #         id = linia.split('"')[1]
    #         # Numery linii w pliku zaczynają się od 1
    #         zasady[id].numer_linii = i + 1

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
                # klawisze_szablonu = zasada.klawisze
                zasada.klawisze = utworzone_klawisze
                # definicja = linie_szablonu[zasada.numer_linii - 1]
                # linie_szablonu[zasada.numer_linii - 1] = \
                #     definicja.replace(
                #         f'["{klawisze_szablonu}"', f'["{utworzone_klawisze}"')
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

    with open(args.teoria, 'w', buffering=512) as zasady_cson:
        zasady_cson.write(f'# UWAGA: Plik auto-generowany na podstawie {args.teoria_szablon}\n')
        zasady_cson.write("{\n")
        for z in zasady.values():
            zasady_cson.write(z.jako_linia_do_pliku())
        zasady_cson.write("}\n")

    słownik = dict()

    for zasada in zasady.values():
        if not zasada.f_słownik:
            continue  # Nie twórz dla niej nowego słowa

        uzupełnij_tekst(zasada, zasady)

        if zasada.klawisze not in słownik:
            słownik[zasada.klawisze] = zasada.tekst
        else:
            log.error(f'Duplikat dla klawiszy `{zasada.klawisze}`: "{zasada.tekst}", już jest "{słownik[zasada.klawisze]}"')

    dyspozytor = DyspozytorKlawiszy(log, zasady)

    frekwencja = dict()
    with open(args.frekwencja, 'r') as dane_frekwencyjne:
        for linia in dane_frekwencyjne:
            linia = linia.strip()
            słowo = linia.split('"')[1]
            liczba = int(linia.split(',')[1])
            if słowo in frekwencja:
                log.error(f'Duplikat "{słowo}" w danych frekwencyjnych, nadpisuję {frekwencja[słowo]} wartością {liczba}')
            frekwencja[słowo] = liczba

    # słownik_ze_słów = dict()

    with open(args.slowa) as podzielone_słowa:
        for numer_linii, linia in enumerate(podzielone_słowa):

            linia = linia.strip()
            if linia.startswith('#'):
                continue

            sylaby = linia.split('=')
            klawisze_słowa = []
            nierozłożona_sylaba = False
            for sylaba in sylaby:
                try:
                    klawisze_sylaby = dyspozytor.klawisze_dla_sylaby(sylaba)
                    klawisze_słowa.append(klawisze_sylaby)
                except ValueError as e:
                    log.error(f'Nie znaleziono rozkładu dla sylaby "{sylaba}" słowa "{linia}": {e.args[0]}')
                    nierozłożona_sylaba = True

            if not nierozłożona_sylaba:
                tekst = ''.join(sylaby)
                klawisze = '/'.join(klawisze_słowa)
                # print(f'Rozłożono {linia} na {klawisze}')
                if (klawisze not in słownik): # and (klawisze not in słownik_ze_słów):
                    słownik[klawisze] = tekst
                # TODO trzeba wymyślić jakiś sposób na eleganckie znajdowanie innych
                # (najlepiej krótszych) kombinacji klawiszy,
                # żeby słowa nie przepadały z powodu duplikacji akordów
                else:
                    stare = słownik[klawisze]
                    nowe = tekst

                    frekw_stare = frekwencja[stare] if stare in frekwencja else -1
                    frekw_nowe = frekwencja[nowe] if nowe in frekwencja else -1

                    if frekw_nowe > frekw_stare:
                        słownik[klawisze] = nowe

                    log.error(f'Duplikat dla klawiszy `{klawisze}`: "{tekst}"{(" (frekwencja " + str(frekw_nowe) + ")") if frekw_nowe != -1 else ""}, już jest "{stare}"{(" (frekwencja " + str(frekw_stare) + ")") if frekw_stare != -1 else ""} {", zamieniam na nowe" if frekw_nowe > frekw_stare else ""}')

            if numer_linii % 10000 == 0 and numer_linii != 0:
                log.info(f'Przetwarzanie linii {numer_linii}: {linia}')

    # Kod wyżej jest tak napisany żeby unikał duplikatów,
    # na wszelki wypadek ważniejsze słowniki są na końcu żeby nadpisać poprzednie
    # słownik_całość = dict()
    # słownik_całość.update(słownik_ze_słów)
    # słownik_całość.update(słownik_z_teorii)

    # Posortuj słowa według kolejności klawiszy
    kolejność = '/#XFZSKTPVLR-JE~*IAUCRLBSGTWOY'
    słownik = collections.OrderedDict(
        sorted(słownik.items(), key=lambda wpis:
               [kolejność.index(k) for k in wpis[0]]))

    linie = [f'"{klawisze}": "{tekst}"'
             for klawisze, tekst in słownik.items()]

    with open(args.slownik, 'w') as slownik:
        slownik.write('{\n' + ',\n'.join(linie) + '\n}')


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

