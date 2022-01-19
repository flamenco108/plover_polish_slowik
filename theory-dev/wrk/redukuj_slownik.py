#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import typing


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Usuwa ze słownika słowa które można utworzyć używając przedrostka',
        epilog='Żeby słowo zostało usunięte, część pozostała po usunięciu '
               'danego przedrostka też musi być w słowniku. '
               'Jeśli jest kilka wariantów, wybiera najdłuższy przedrostek')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='wypisuj więcej informacji w trakcie działania')
    parser.add_argument('--slownik',
                        help='plik słownika do uproszczenia', default='../data/slownik')
    # TODO: Otwieranie jednej kolumny z pliku ods jako plik tekstowy z liniami
    # To są zipowane pliki xml, można to zrobić bez dodatkowych bibliotek,
    # ale trzeba by zrobić składnię do wybierania o który arkusz i kolumnę chodzi
    parser.add_argument('--przedrostki',
                        help='plik z przedrostkami', default='../data/przedrostki.txt')
    parser.add_argument('-o', '--output',
                        help='wynikowy plik ze zmniejszonym słownikiem',
                        default='wyniki/slownik-rozłożony.txt')
    group_sylaby = parser.add_mutually_exclusive_group()
    group_sylaby.add_argument('-S', '--sylaby', action='store_true',
                              help='dziel słowa tylko całymi sylabami')
    group_sylaby.add_argument('-s', '--nie-sylaby', action='store_false', dest='sylaby',
                              help='dziel słowa dowolnie')
    parser.add_argument('--separator',
                        help='znak rozdzielający sylaby w słowniku', default='=')
    args = parser.parse_args()

    if args.verbose:
        print('Opcje: ', args)

    if args.sylaby:
        raise NotImplementedError(
            'Na razie nie ma trybu sylabami, bo przedrostki nie są podzielone')

    # Utwórz folder na wyniki jeśli nie istnieje
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    with open(args.slownik) as słownik:
        with open(args.przedrostki) as przedrostki:
            with open(args.output, 'w') as output:
                redukuj_przedrostki(słownik, przedrostki,
                                    output, args.separator, args.verbose)


def redukuj_przedrostki(słownik: typing.TextIO, przedrostki: typing.TextIO, output: typing.TextIO,
                        separator: str, verbose=False):
    # Zbiory przedrostków o danych długościach
    przedrostki_wg_dł = zbiory_wg_długości(przedrostki)
    # Zbiór słów niepodzielonych na sylaby
    słowa = set([''.join(linia.strip().split(separator))
                for linia in słownik
                if not linia.startswith('#')])

    # Zakładając unikalne słowa w pliku, tak mi wygodniej
    liczba_linii = len(słowa)
    liczba_rozłożonych = 0

    słownik.seek(0)  # Przewiń z powrotem na początek pliku
    for numer_linii, linia in enumerate(słownik):
        if linia.startswith('#'):
            continue  # Pomiń komentarze
        słowo = ''.join(linia.strip().split(separator))

        # Jakie długości przedrostka rozważyć, krótsze niż słowo
        maks_dł_przedrostka = min(len(przedrostki_wg_dł), len(słowo) - 1)

        rozłożone = False

        # Preferowane dłuższe przedrostki, iteracja od maks_dł do 1 włącznie
        for dł_przedrostka in reversed(range(1, maks_dł_przedrostka + 1)):
            początek = słowo[:dł_przedrostka]
            reszta = słowo[dł_przedrostka:]

            # Przedrostki o długości 1 są na pozycji 0 w liście
            if początek in przedrostki_wg_dł[dł_przedrostka - 1] and reszta in słowa:
                if verbose:
                    print(f'Rozkładanie {początek}-{reszta}')
                rozłożone = True
                liczba_rozłożonych += 1
                break

        if not rozłożone:
            output.write(linia)

        if numer_linii % 10000 == 0 and numer_linii != 0:
            print(
                f'Sprawdzono {float(numer_linii)/float(liczba_linii)*100.0:5.2f}% '
                f'linii ({numer_linii}/{liczba_linii}), rozłożono {liczba_rozłożonych} słów')


def zbiory_wg_długości(plik: typing.TextIO) -> typing.List[set]:
    """Tworzy listę linii pogrupowanych w zbiory według długości.
    Możliwe że niektóre zbiory będą puste. Znaki odstępu i nowej linii
    (whitespace) na początku i końcu wiersza są ignorowane.

    Parameters
    ----------
    plik : typing.TextIO
        plik podzielony na linie

    Returns
    -------
    list
        lista N elementów, gdzie pierwszy element to zbiór wszystkich linii
        o długości 1, a ostatni to zbiór linii o największej długości;
    """
    wynik = []

    for linia in plik:
        linia = linia.strip()

        if len(linia) == 0:
            continue

        while len(wynik) < len(linia):
            wynik.append(set())

        # Zbiór linii o długości 1 jest na pozycji 0 w liście
        wynik[len(linia) - 1].add(linia)

    return wynik


if __name__ == '__main__':
    main()
