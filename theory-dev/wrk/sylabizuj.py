#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        description='''Przenieś podział na sylaby z jednego pliku do drugiego

Wskazówki:
  - jako plik wejściowy możesz podać "-" żeby brał dane z konsoli (stdin),
    wtedy można pisać słowa na żywo w trakcie działania programu, np:
        sylabizuj.py -f -
    lub przekierować inne procesy, np:
        echo "abak" | sylabizuj.py -
  - tak samo można zrobić dla pliku wyjściowego żeby wyniki trafiały do konsoli''',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    domyślny_output = 'wyniki/sylabizowane'
    parser.add_argument('-o', '--output',
                        type=argparse.FileType('w', encoding='UTF-8'),
                        help=f'wynikowy plik podzielony na sylaby (domyślnie: jeśli input to stdin: stdout, jeśli input to plik: {domyślny_output})')
    parser.add_argument('-f', '--force', action='store_true',
                        help='kontynuuj działanie w przypadku wystąpienia błędu (domyślnie: nie)')
    domyślne_sylaby = '../data/slownik'
    parser.add_argument('--sylaby', default=domyślne_sylaby,
                        type=argparse.FileType('r', encoding='UTF-8'),
                        help=f'plik wzorcowy ze słowami podzielonymi na sylaby (domyślnie {domyślne_sylaby})')
    parser.add_argument('--separator', default='=', metavar='SEP',
                        help='znak rozdzielający sylaby (domyślnie "=")')
    poziom = parser.add_mutually_exclusive_group()
    poziom.add_argument('-v', '--verbose', action='count', default=0,
                        help='wypisuj więcej informacji w trakcie działania')
    poziom.add_argument('-q', '--quiet', action='count', default=0,
                        help='wypisuj mniej informacji w trakcie działania')
    parser.add_argument('input',
                        type=argparse.FileType('r', encoding='UTF-8'),
                        help='plik ze słowami do podziału na sylaby')
    args = parser.parse_args()
    args.verbosity = args.verbose - args.quiet
    if args.output is None:
        if args.input.name == '<stdin>':
            args.output = sys.stdout
        else:
            os.makedirs(os.path.dirname(domyślny_output), exist_ok=True)
            args.output = open(domyślny_output, 'w')

    if args.verbosity > 0:
        print('Argumenty:', str(args)[10:-1])

    sylaby = dict()
    for numer_linii, linia in enumerate(args.sylaby):
        linia = linia.strip()
        sklejone = ''.join(linia.split(args.separator))
        if sklejone not in sylaby:
            sylaby[sklejone] = [linia]
        else:
            if linia in sylaby[sklejone]:
                if args.verbosity > 0:
                    print(f'Duplikat sylabizacji: "{linia}"')
            else:
                sylaby[sklejone].append(linia)

        if args.verbosity >= 0:
            if numer_linii % 10000 == 0 and numer_linii != 0:
                print(f'Wczytywanie sylab z linii {numer_linii}: {linia}')

    for numer_linii, linia in enumerate(args.input):
        słowo = linia.strip()

        if słowo in sylaby:
            for sylabizacja in sylaby[słowo]:
                args.output.write(sylabizacja + '\n')
        else:
            info = f'Nie znaleziono sylabizacji dla słowa "{słowo}"'
            if not args.force:
                raise ValueError(
                    info + ', bez argumentu --force przerywam działanie')
            if args.force and args.verbosity >= 0:
                print(info)

        if args.verbosity >= 0:
            if numer_linii % 10000 == 0 and numer_linii != 0:
                print(f'Przetwarzanie słowa {numer_linii}: {słowo}')


if __name__ == '__main__':
    main()
