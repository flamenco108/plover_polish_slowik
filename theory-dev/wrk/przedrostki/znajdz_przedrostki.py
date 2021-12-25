#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import typing


def find_prefixes(file_in, separator, max_length, verbose=False) -> dict:
    """Znajduje przedrostki w słowach

    Parameters
    ----------
    file_in : typing.TextIO()
        plik ze słowem podzielonym na sylaby w każdej linii;
        linie rozpoczynające się od znaku kratki (#) są pomijane
    separator : str
        ciąg znaków rozdzielający sylaby
    max_length : int
        maksymalna liczba sylab przedrostka
    verbose : bool, optional
        pisanie dodatkowych informacji do konsoli, by default False

    Returns
    -------
    dict
        liczba słów rozpoczynających się od danego przedrostka
    """
    words_in = set([line.strip() for line in file_in])
    if verbose:
        print('Unikalne słowa: ', words_in)

    line_count = len(words_in)  # Zakładam unikalne słowa, tak mi najwygodniej

    valid_prefixes = {}

    file_in.seek(0)  # Przewiń z powrotem na początek pliku
    for line_number, line in enumerate(file_in):
        if line.startswith('#'):
            continue  # Pomiń komentarze

        for length in range(1, max_length + 1):
            syllables = line.strip().split(separator)
            if len(syllables) <= length:
                continue  # Za krótkie słowo

            prefix_candidate = separator.join(syllables[:length])
            rest_of_word = separator.join(syllables[length:])

            if verbose:
                print(
                    f"Przedrostek: '{prefix_candidate}', reszta słowa: '{rest_of_word}'", end=' ')

            if rest_of_word in words_in:
                if prefix_candidate in valid_prefixes:
                    valid_prefixes[prefix_candidate] += 1
                    if verbose:
                        print('zwiększona liczba wystąpień')
                else:
                    valid_prefixes[prefix_candidate] = 1
                    if verbose:
                        print('dopisany do wyników')

            elif verbose:
                print('pominięty, bo reszta nie jest słowem')

        if line_number % 10000 == 0 and line_number != 0:
            print(
                f'Sprawdzono {float(line_number)/float(line_count)*100.0:5.2f}% linii ({line_number}/{line_count})')

    return valid_prefixes


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """Potrzebna żeby skorzystać jednocześnie z wyświetlania domyślnych wartości i ręcznego łamania linii w opisie
    """
    pass


def main():
    """Zamyka w sobie całe działanie skryptu, żeby można było importować pozostałe elementy
    """
    parser = argparse.ArgumentParser(
        formatter_class=CustomFormatter,
        description='Znajduje przedrostki w słowniku podzielonym na sylaby',
        epilog="""Przedrostki spełniają następujące warunki:
  - Składają się z ciągu jednej lub więcej sylab
  - Rozpoczynają dane słowo
  - Pozostała część słowa po usunięciu przedrostka także występuje w słowniku""")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='wypisuj więcej informacji w trakcie działania')
    parser.add_argument('-i', '--input',
                        help='plik słownika do przeszukania', default='slownik-testowy.txt')
    parser.add_argument('-o', '--output',
                        help='wynikowy plik z przedrostkami', default='wyniki/przedrostki.txt')
    parser.add_argument('-L', '--max-length', type=int,
                        help='maksymalna liczba sylab przedrostka', default=2)
    parser.add_argument('--separator',
                        help='znak rozdzielający sylaby', default='=')
    args = parser.parse_args()

    if args.verbose:
        print('Opcje: ', args)

    # Utwórz folder na wyniki jeśli nie istnieje
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    prefixes_found_count = 0
    with open(args.input, 'r') as file_in:
        with open(args.output, 'w') as file_out:
            prefixes = find_prefixes(file_in, args.separator,
                                     args.max_length, args.verbose)

            # Posortuj klucze według wartości dla nich, malejąco
            common_prefixes = sorted(prefixes, key=prefixes.get, reverse=True)
            file_out.write('\n'.join(common_prefixes))

            print(f'Zapisano {len(prefixes)} przedrostków do {args.output}')


# Ten warunek się wykona tylko jeśli to jest właśnie uruchamiany skrypt
if __name__ == '__main__':
    main()
