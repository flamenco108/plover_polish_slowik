#!/usr/bin/env python3
import argparse
from itertools import combinations
import json
import re
from typing import Tuple

from cson import CommentRemover


Klw = Tuple[str, str, str]
"""Klawisze podzielone na lewą, środek i prawą, w poprawnej kolejności
"""


def main():
    domyślne_pliki = {
        'teoria': 'wyniki/rules.cson',
        'slownik': 'wyniki/spektralny-slowik.json'
    }

    parser = argparse.ArgumentParser(
        description='''Znajdź nieużywane kombinacje klawiszy na podstawie \
pliku definicji teorii (domyślnie) lub gotowego słownika

Wskazówki:
  - w razie problemów z argumentami (np. zaczynając klawisze od myślnika),
    możesz rozdzielić argumenty opcjonalne i pozycyjne pisząc `--`, np:
        wolne_klawisze.py --slownik -- -crlb
  - jeśli jest dużo wyników, może być wygodniej zapisać je w pliku, np:
        wolne_klawisze.py xfzs > wyniki/wolne_klawisze.txt''',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('klawisze', metavar='KLAWISZE', type=str,
                        help='klawisze do sprawdzenia')
    źródło = parser.add_mutually_exclusive_group()
    źródło.add_argument('--teoria', default=domyślne_pliki['teoria'],
                        help=f'plik z definicją teorii (domyślnie: {domyślne_pliki["teoria"]})')
    źródło.add_argument('--slownik', nargs='?', const=domyślne_pliki['slownik'],
                        help='przeszukaj słownik zamiast definicji teorii, opcjonalnie podaj '
                        f'plik słownika Plover (domyślnie: {domyślne_pliki["slownik"]})')
    parser.epilog = '''\
Klawisze do sprawdzenia, oraz w przeszukiwanych plikach muszą należeć do następującego zbioru:
    #XFZSKTPVLR -JE~*IAU CRLBGTSGTWOY
Wielkość liter nie ma znaczenia. W przypadku klawiszy które występują po obu stronach klawiatury
zakłada się że są po lewej, chyba że znajdują się po którymś ze znaków z centralnej części.
Wpisy do słownika składające się z kilku uderzeń ograniczonych / są dzielone i rozpatrywane osobno.'''
    args = parser.parse_args()
    klawisze: Klw = None
    try:
        klawisze = podziel_klawisze(args.klawisze)
    except ValueError as e:
        parser.error(e.args[0])
    plik_źródłowy = args.teoria if args.slownik is None else args.slownik
    print('Szukanie niewykorzystanych kombinacji klawiszy '
          f'`{zapis_plover(klawisze)}` w {plik_źródłowy}')

    wykorzystane = set()
    if args.slownik is None:
        with open(args.teoria) as teoria_cson:
            teoria = json.load(CommentRemover(teoria_cson))
            for definicja in teoria.values():
                assert definicja[0] != '', 'Plik teorii musi mieć wygenerowane klawisze'
                wykorzystane.add(zapis_unikalny(
                    podziel_klawisze(definicja[0])))
    else:
        with open(args.slownik) as slownik_json:
            slownik = json.load(slownik_json)
            for wpis in slownik.keys():
                for uderzenie in wpis.split('/'):
                    wykorzystane.add(zapis_unikalny(
                        podziel_klawisze(uderzenie)))

    wolne_jako_element = []
    wolne_jako_całość = []
    nie_zawierają_wykorzystanej = []
    for indeksy in kombinacje(sum([len(s) for s in klawisze])):
        wybrane = wybierz_klawisze(klawisze, indeksy)
        wybrane_u = zapis_unikalny(wybrane)
        if wybrane_u not in wykorzystane:
            nie_są_elementem = True
            for zastosowanie in wykorzystane:
                if all(k in zastosowanie for k in wybrane_u):
                    nie_są_elementem = False
                    break
            if nie_są_elementem:
                wolne_jako_element.append(zapis_plover(wybrane))
            else:
                zastosowanie_się_mieści = False
                for zastosowanie in wykorzystane:
                    if all(k in wybrane_u for k in zastosowanie):
                        zastosowanie_się_mieści = True
                        break
                if not zastosowanie_się_mieści:
                    nie_zawierają_wykorzystanej.append(zapis_plover(wybrane))
                else:
                    wolne_jako_całość.append(zapis_plover(wybrane))

    print(
        f'-------- {len(nie_zawierają_wykorzystanej)} kombinacji nie jest użytych samodzielnie, '
        'nie jest częścią złożenia, ani nie mieści się w nich żadne złożenie')
    print('\n'.join(nie_zawierają_wykorzystanej))
    print(
        f'-------- {len(wolne_jako_całość)} kombinacji nie jest użytych samodzielnie, '
        'ale występuje jako część złożenia')
    print('\n'.join(wolne_jako_całość))
    print(
        f'-------- {len(wolne_jako_element)} kombinacji nie jest użytych samodzielnie, '
        'ale mieści się w nich jakieś użyte złożenie')
    print('\n'.join(wolne_jako_element))
    # Pozostały przypadek: nie ma elementów wspólnych z żadnym wpisem, ale to niemożliwe każdego klawisza gdzieś użyliśmy


def kombinacje(n: int):
    """Wybierz kombinacje ze zbioru n elementów, zaczynając od najkrótszych.

    Parameters
    ----------
    n : int
        liczba elementów zbioru do wyboru

    Yields
    -------
    Tuple[int, ...]
        indeksy wybranych elementów pomiędzy 0 a n-1 włącznie
    """
    for k in range(1, n+1):
        for comb in combinations(range(n), k):
            yield comb


def wybierz_klawisze(klawisze: Klw, indeksy: Tuple[int, ...]) -> Klw:
    """Zwraca klawisze dla listy indeksów.

    Parameters
    ----------
    klawisze : Klw
        zbiór klawiszy do wyboru podzielony na części klawiatury
    indeksy : Tuple[int, ...]
        indeksy klawiszy do wyboru gdyby były niepodzielonym tekstem

    Returns
    -------
    Klw
        wybrane klawisze
    """
    dł_l, dł_ś, dł_p = [len(s)for s in klawisze]
    lewe = [klawisze[0][i]
            for i in indeksy if i < dł_l]
    środkowe = [klawisze[1][i - dł_l]
                for i in indeksy if dł_l <= i < (dł_l + dł_ś)]
    prawe = [klawisze[2][i - dł_l - dł_ś]
             for i in indeksy if i >= (dł_l + dł_ś)]
    return tuple([''.join(s) for s in [lewe, środkowe, prawe]])


def zapis_plover(klawisze: Klw) -> str:
    """Zapisz klawisze podzielone na strony w tej formie co w słowniku

    Parameters
    ----------
    klawisze : Klw
        zbiór klawiszy podzielony na części klawiatury

    Returns
    -------
    str
        klawisze zapisane ciągiem, rozdzielone myślnikiem tylko jeśli to konieczne
    """
    return klawisze[0] + ('-' if klawisze[1] == '' and len(klawisze[2]) > 0 else klawisze[1]) + klawisze[2]


def zapis_unikalny(klawisze: Klw) -> str:
    """Zapisz klawisze tak żeby każdy był unikalnym znakiem

    Parameters
    ----------
    klawisze : Klw
        zbiór klawiszy podzielony na części klawiatury

    Returns
    -------
    str
        klawisze zapisane ciągiem, prawa strona małymi literami, bez myślnika
    """
    return klawisze[0] + klawisze[1] + klawisze[2].lower()


def podziel_klawisze(klawisze_plover: str) -> Klw:
    """Waliduje, dzieli i sortuje klawisze

    Parameters
    ----------
    klawisze_plover : str
        klawisze podane przez użytkownika

    Returns
    -------
    Klw
        zbiór klawiszy podzielony na części klawiatury

    Raises
    ------
    ValueError
        Klawisze środkowej części podane jako dwa ciągi
    ValueError
        Podano klawisze których nie ma na rozpoznanej stronie klawiatury
    """
    klawisze_użytkownika = re.sub(r'\s', '', klawisze_plover.upper())

    klawiatura_lewa = '#XFZSKTPVLR'
    klawiatura_środek = '-JE~*IAU'
    klawiatura_prawa = 'crlbgtsgtwoy'

    klawisze = None
    środkowe_klawisze = re.compile(r'[\-JE~*IAU]+')
    środek = re.search(środkowe_klawisze, klawisze_użytkownika)
    if środek:
        strony = re.split(środkowe_klawisze, klawisze_użytkownika)
        if len(strony) > 2:
            raise ValueError(
                f'Środkowe klawisze ({klawiatura_środek}) podane dwukrotnie')
        else:
            klawisze = (strony[0], środek.group(0), strony[1])
    else:
        klawisze = (klawisze_użytkownika, '', '')

    błędne_klawisze = []
    brakuje_podziału = False
    for i, k in enumerate(klawisze_użytkownika):
        if i < len(klawisze[0]):
            if k not in klawiatura_lewa:
                błędne_klawisze.append(i)
                if k.lower() in klawiatura_prawa:
                    brakuje_podziału = True
        elif i < (len(klawisze[0]) + len(klawisze[1])):
            if k not in klawiatura_środek:
                błędne_klawisze.append(i)
                if k.lower() in klawiatura_prawa:
                    brakuje_podziału = True
        else:
            if k.lower() not in klawiatura_prawa:
                błędne_klawisze.append(i)

    if len(błędne_klawisze) > 0:
        wskaźnik = ''.join([('^' if i in błędne_klawisze else ' ')
                            for i in range(len(klawisze_użytkownika))])
        raise ValueError(f'Podano niepoprawne klawisze{", może brakuje myślnika" if brakuje_podziału else ""}'
                         f':\n\n{klawisze_użytkownika}\n{wskaźnik}')

    # Myślnik jest niepotrzebny jak są przechowywane w częściach
    klawisze = (klawisze[0], klawisze[1].replace('-', ''), klawisze[2])

    # Usuwa duplikaty i sortuje
    kolejność = klawiatura_lewa + klawiatura_środek + klawiatura_prawa.upper()
    klawisze = tuple([
        ''.join([kolejność[i]
                for i in sorted(list(set(kolejność.index(k)
                                         for k in strona)))])
        for strona in klawisze])
    return klawisze


if __name__ == '__main__':
    main()
