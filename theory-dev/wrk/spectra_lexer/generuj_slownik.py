#!/usr/bin/env python3
import argparse
import collections
import json
import os
import re
from typing import Any, Dict, TextIO, Tuple

from cson import CommentRemover


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
    with open(args.log, 'w') as log_generatora:
        log_generatora.write(f'Argumenty: {str(args)[10:-1]}\n')

    zasady = dict()
    linie_szablonu = []
    with open(args.teoria_szablon) as szablon_cson:
        linie_szablonu = szablon_cson.readlines()

        if not linie_szablonu[0].startswith('#'):
            raise ValueError(
                'Pierwsza linia w pliku szablonu musi być komentarzem')
            # Inaczej by mi się rozjechały numery linii po dodaniu pierwszej
        linie_szablonu[0] = \
            f'# UWAGA: Plik wygenerowany automatycznie na podstawie {"rules.cson.in"}\n'

        szablon_cson.seek(0)
        zasady_json = CommentRemover(szablon_cson)
        # for i, linia in enumerate(zasady_json):
        #     print(f'{i}\t{linia}', end='')
        # zasady_json.seek(0)
        try:
            zasady = json.load(zasady_json)
        except json.JSONDecodeError as e:
            wyświetl_błąd_json(zasady_json, e)
            raise e

    # print(zasady)

    # Zmień słownik list na słownik obiektów
    with open(args.log, 'a') as log_generatora:  # Otwórz w trybie a - append, żeby dopisywać
        for id in zasady:
            # Nazwy zmiennych zgodne z spectra_lexer/doc/rules_format.txt
            keys, letters, alt, flags, info = tuple(zasady[id])
            sformatowane_klawisze = połącz_klawisze(keys)
            if sformatowane_klawisze != keys:
                log_generatora.write(
                    f'Klawisze szablonu: zmieniono "{keys}" na "{sformatowane_klawisze}"\n')
            zasady[id] = Zasada(keys, letters, flags)

    zasady: Dict[str, Zasada]  # Informacja dla edytora kodu jaki to ma typ

    # Dopisz do zasad z której są linii
    for i, linia in enumerate(linie_szablonu):
        linia = linia.strip()
        if linia.startswith('"'):
            id = linia.split('"')[1]
            # Numery linii w pliku zaczynają się od 1
            zasady[id].numer_linii = i + 1

    # Inna zasada w tekście: ciąg dowolnych znaków wewnątrz nawiasów
    inna_zasada = re.compile(r'\(([^()]+)\)')

    # Złóż wszystkie zasady bez klawiszy z innych zasad
    # Możliwe że będzie konieczne kilka iteracji jeśli jest kilka poziomów definicji
    while True:
        zmieniono_zasadę = False  # Wykryj iteracje bez szans na ukończenie zadania

        for edytowane_id, zasada in zasady.items():
            if not zasada.do_uzupełnienia():
                continue

            użyte_id = set()
            tekst = zasada.litery
            while True:
                # Szczegóły znalezionej innej zasady
                m = inna_zasada.search(tekst)
                if not m:
                    break
                inne_id = m.group(1).split('|')[1] \
                    if '|' in m.group(1) else m.group(1)
                użyte_id.add(inne_id)
                # Obsługa składni: (litery|id), wstaw id w nawiasach
                podmiana = ('(' + inne_id + ')') \
                    if '|' in m.group(1) else zasady[m.group(1)].litery
                tekst = tekst[:m.start()] + podmiana + tekst[m.end():]

            użyte_id_do_uzupełnienia = {
                id for id in użyte_id if zasady[id].do_uzupełnienia()}

            if len(użyte_id_do_uzupełnienia) == 0:
                # Mamy wszystkie składowe, można utworzyć ten wpis
                utworzone_klawisze = połącz_klawisze(
                    *[zasady[id].klawisze for id in użyte_id])
                klawisze_szablonu = zasada.klawisze
                zasady[edytowane_id].klawisze = utworzone_klawisze
                definicja = linie_szablonu[zasada.numer_linii - 1]
                linie_szablonu[zasada.numer_linii - 1] = \
                    definicja.replace(
                        f'["{klawisze_szablonu}"', f'["{utworzone_klawisze}"')
                zmieniono_zasadę = True
                # print(f'Wygenerowano {zasady[edytowane_id]}')

        if not jest_pusta_zasada(zasady):
            break
        if not zmieniono_zasadę:
            pozostałe = [id for id, zasada in zasady.items()
                         if zasada.do_uzupełnienia()]
            raise ValueError(
                f'Nie udało się znaleźć klawiszy dla zasad: {", ".join(pozostałe)}')

    with open(args.teoria, 'w') as zasady_cson:
        zasady_cson.writelines(linie_szablonu)

    słownik_z_teorii = dict()

    with open(args.log, 'a') as log_generatora:

        for id, zasada in zasady.items():
            if not zasada.f_słownik:
                continue  # Nie twórz dla niej nowego słowa

            uzupełnij_tekst(zasady, id)

            if zasada.klawisze not in słownik_z_teorii:
                słownik_z_teorii[zasada.klawisze] = zasada.tekst
            else:
                log_generatora.write(
                    f'Duplikat dla klawiszy `{zasada.klawisze}`: '
                    f'"{zasada.tekst}", już jest "{słownik_z_teorii[zasada.klawisze]}"\n')

    # Zbuduj słowniki do szukania zasad dla fragmentów sylaby
    nagłosy = dict()
    śródgłosy = dict()
    wygłosy = dict()

    for id, zasada in zasady.items():
        if zasada.f_nagłos or zasada.f_śródgłos or zasada.f_wygłos:
            uzupełnij_tekst(zasady, id)
        else:
            continue

        if zasada.f_nagłos:
            nagłosy[zasada.tekst] = id
        elif zasada.f_śródgłos:
            śródgłosy[zasada.tekst] = id
        elif zasada.f_wygłos:
            wygłosy[zasada.tekst] = id

    frekwencja = dict()
    with open(args.frekwencja, 'r') as dane_frekwencyjne:
        for linia in dane_frekwencyjne:
            linia = linia.strip()
            słowo = linia.split('"')[1]
            liczba = int(linia.split(',')[1])
            if słowo in frekwencja:
                raise ValueError(
                    f'Duplikat "{słowo}" w danych frekwencyjnych, z liczbami {liczba} i {frekwencja[słowo]}')
            else:
                frekwencja[słowo] = liczba

    słownik_ze_słów = dict()

    with open(args.log, 'a') as log_generatora:
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
                        klawisze_sylaby = rozłóż_sylabę(
                            zasady, nagłosy, śródgłosy, wygłosy, sylaba)
                        klawisze_słowa.append(klawisze_sylaby)
                    except ValueError as e:
                        log_generatora.write(
                            f'Nie znaleziono rozkładu dla sylaby "{sylaba}" słowa "{linia}": {e.args[0]}\n')
                        nierozłożona_sylaba = True

                if not nierozłożona_sylaba:
                    tekst = ''.join(sylaby)
                    klawisze = '/'.join(klawisze_słowa)
                    # print(f'Rozłożono {linia} na {klawisze}')
                    if (klawisze not in słownik_z_teorii) and (klawisze not in słownik_ze_słów):
                        słownik_ze_słów[klawisze] = tekst
                    elif klawisze in słownik_z_teorii:
                        log_generatora.write(
                            f'Duplikat dla klawiszy `{klawisze}`: '
                            f'"{tekst}", już jest "{słownik_z_teorii[klawisze]}" zdefiniowane w teorii\n')
                    else:
                        stare = słownik_ze_słów[klawisze]
                        nowe = tekst

                        frekw_stare = frekwencja[stare] if stare in frekwencja else -1
                        frekw_nowe = frekwencja[nowe] if nowe in frekwencja else -1

                        if frekw_nowe > frekw_stare:
                            słownik_ze_słów[klawisze] = nowe

                        log_generatora.write(
                            f'Duplikat dla klawiszy `{klawisze}`: '
                            f'"{tekst}"{(" (frekwencja " + str(frekw_nowe) + ")") if frekw_nowe != -1 else ""}, '
                            f'już jest "{stare}"{(" (frekwencja " + str(frekw_stare) + ")") if frekw_stare != -1 else ""}'
                            f'{", zamieniam na nowe" if frekw_nowe > frekw_stare else ""}\n')

                if numer_linii % 10000 == 0 and numer_linii != 0:
                    print(f'Przetwarzanie linii {numer_linii}: {linia}')

    # Kod wyżej jest tak napisany żeby unikał duplikatów,
    # na wszelki wypadek ważniejsze słowniki są na końcu żeby nadpisać poprzednie
    słownik_całość = dict()
    słownik_całość.update(słownik_ze_słów)
    słownik_całość.update(słownik_z_teorii)

    # Posortuj słowa według kolejności klawiszy
    kolejność = '/#XFZSKTPVLR-JE~*IAUCRLBSGTWOY'
    słownik_całość = collections.OrderedDict(
        sorted(słownik_całość.items(), key=lambda wpis:
               [kolejność.index(k) for k in wpis[0]]))

    linie = [f'"{klawisze}": "{tekst}"'
             for klawisze, tekst in słownik_całość.items()]

    with open(args.slownik, 'w') as slownik:
        slownik.write('{\n' + ',\n'.join(linie) + '\n}')


class Zasada:
    def __init__(self, klawisze: str, litery: str, flagi: str, numer_linii: int = 0) -> None:
        self.klawisze = klawisze
        self.litery = litery
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
        if not self.do_uzupełnienia():
            self.tekst = self.litery

    def __str__(self) -> str:
        return f'Zasada: "{self.klawisze}" -> "{self.litery}"'

    def do_uzupełnienia(self) -> bool:
        return self.klawisze == ''


def uzupełnij_tekst(zasady: Dict[str, Zasada], id: str) -> None:
    """Podmień odwołania do innych zasad na tekst
    """
    zasada = zasady[id]
    tekst = zasada.litery
    inna_zasada = re.compile(r'\(([^()]+)\)')
    while True:  # Nie używam operatora := bo jest na razie zbyt świeży
        # Szczegóły znalezionej innej zasady
        m = inna_zasada.search(tekst)
        if not m:
            break
        # Obsługa składni: (litery|id), wstaw litery
        podmiana = m.group(1).split('|')[0] \
            if '|' in m.group(1) else zasady[m.group(1)].litery
        tekst = tekst[:m.start()] + podmiana + tekst[m.end():]

    if zasada.f_duże_litery:
        tekst = tekst.upper()

    zasady[id].tekst = tekst


def jest_pusta_zasada(zasady: Dict[Any, Zasada]) -> bool:
    for zasada in zasady.values():
        if zasada.do_uzupełnienia():
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


def rozłóż_sylabę(zasady: Dict[str, Zasada], nagłosy: Dict[str, str],
                  śródgłosy: Dict[str, str], wygłosy: Dict[str, str], sylaba) -> str:
    samogłoski = re.compile(r'[aąeęioóuy]+')
    m = samogłoski.search(sylaba)
    if not m:
        raise ValueError('sylaba bez samogłosek')
    nagłos = re.split(samogłoski, sylaba)[0]
    śródgłos = m.group(0)
    wygłos = re.split(samogłoski, sylaba)[1]

    # Wykryj "i" które tylko zmiękcza, przesuń je do nagłosu
    if len(śródgłos) > 1 and śródgłos.startswith('i'):
        nagłos = nagłos + śródgłos[0]
        śródgłos = śródgłos[1:]

    if nagłos != '' and (nagłos not in nagłosy):
        raise ValueError(f'brak definicji ONSET dla "{nagłos}"')
    if śródgłos != '' and (śródgłos not in śródgłosy):
        raise ValueError(f'brak definicji NUCLEUS dla "{śródgłos}"')
    if wygłos != '' and (wygłos not in wygłosy):
        raise ValueError(f'brak definicji CODA dla "{wygłos}"')

    return połącz_klawisze(
        (zasady[nagłosy[nagłos]].klawisze if nagłos != '' else ''),
        (zasady[śródgłosy[śródgłos]].klawisze if śródgłos != '' else ''),
        (zasady[wygłosy[wygłos]].klawisze if wygłos != '' else '')
    )


def wyświetl_błąd_json(zasady_json: TextIO, błąd: json.JSONDecodeError):
    """Oznacza graficznie miejsce wystąpienia błędu JSON
    """
    zasady_json.seek(0)
    linie_json = zasady_json.readlines()
    indeks_linii = błąd.lineno - 1  # lineno to linia w pliku więc zaczyna się od 1

    print('------------')
    if indeks_linii >= 2:
        print(linie_json[indeks_linii - 2], end='')
    if indeks_linii >= 1:
        print(linie_json[indeks_linii - 1], end='')
    print(linie_json[indeks_linii], end='')
    print(' '*(błąd.colno - 2), '^---', błąd.msg)
    if indeks_linii < len(linie_json) - 1:
        print(linie_json[indeks_linii + 1], end='')
    if indeks_linii < len(linie_json) - 2:
        print(linie_json[indeks_linii + 2], end='')
    print('------------')


if __name__ == '__main__':
    main()
