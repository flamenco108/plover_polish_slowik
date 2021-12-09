#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys, re
# import statistics

###################################################
### ZAJAWKA i pobranie nazwy pliku do przetworzenia
# nazwa tego skryptu
from pathlib import Path
#Path(__file__).name    # ScriptName.py
#Path(__file__).stem    # ScriptName

zajawka1 = """
Skrypt {skrypt} służy do podzielenia podanego korpusu
na sylaby.
Chodzi o plik, który zawiera słowa wcześniej niepodzielone na sylaby:
 - Musi on zostać poddany najsampierw ręcznej obróbce.
 - Potem zassany i podzielony na sylaby.
 - Potem znowu zapisany i poddany ręcznej obróbce.
 - Wreszcie gotowy produkt może zostać dołączony do słownika,
który będzie użyty przy powtórnym przelocie przez korpus.

""".format(skrypt = Path(__file__).name)
print(zajawka1)
###
zajawka2 = """
Ścieżka do skryptu dla orientacji:
{path}

""".format(path = Path(__file__))
print(zajawka2)


### Pobierz nazwę pliku do przetworzenia
while True:
    try:
        # odblokować po zakończeniu pisania kodu
        # korpusname = input("Podaj nazwę korpusu: ")
        # slownikname = input("Podaj nazwę słownika: ")
        # na razie ćwiczymy na plikach testowych
        # korpusname = "../data/korpus/korpus_sylaby_podz_uniq"
        korpusname = "../data/do_korpus/sjp_ngu"
        #slownikname = "../data/slownik-test"
    except ValueError:
        print("Sorry, nie rozumim.")
        #better try again... Return to the start of the loop
        continue
    else:
        print("Przetwarzamy ", korpusname)
        #print("Przetwarzamy ", slownikname)
        print("")
        # and go out the loop
        break


###################################################

def dziel_na_sylaby(plik):
    with open(plik, 'r') as kn:
        plik = kn.readlines()
        plik = [x.strip() for x in plik]

    sylaby_podzielone = []
    from hyphen import Hyphenator
    h = Hyphenator('pl_PL') # ustawiam język polski
    for s in plik:
        sylaby = h.syllables(s)
        if not sylaby:
            sylaby_podzielone.append(s)
        else:
            sylaby_podzielone.append(sylaby)
    slownik_podzielone = {key: value for key, value in zip(plik,sylaby_podzielone)}

    # print("\nLista z pliku niepodzielonego: ")
    # print(plik)
    # print("\nSylaby podzielone: ")
    # print(sylaby_podzielone)
    # print("\nSłownik podzielone: ")
    # print(slownik_podzielone)

    slownik_wynik = korpusname + '_slownik_podzielone'
    sylaby_wynik = korpusname + '_sylaby_podzielone'
    sylaby_uniq =  korpusname + '_sylaby_podz_uniq'

    slp = {}
    for key, val in slownik_podzielone.items():
        #print(key,' ',val)
        if isinstance(val,list):
            slp[key] = '='.join(val)
            # print('==',slp[key])
        else:
            slp[key] = val
            # print('--',slp[key])
    #print(slp)

    with open(slownik_wynik, 'w') as kw:
        print("\nSłownik słowo+sylaby zapisywane do pliku:\n")
        for key, val in slp.items():
            kw.write('%s %s\n' % (key,val))
            # print('%s %s' % (key,val))
        print("\nSłownik słowo+sylaby zapisane do pliku: ",slownik_wynik)

    # niedozwolone_slowa_file = korpusname + '_niedozwolone'

# same sylaby
    slb = []
    for e in sylaby_podzielone:
        if isinstance(e,list):
            e = '='.join(e)
            slb.append(e)
    #        print(e)
        else:
            e = e
            slb.append(e)
    #        print(e)

    with open(sylaby_wynik, 'w') as kw:
        kw.write('\n'.join(slb))
    print("\nSylaby podzielone zapisane do pliku: ", sylaby_wynik)

    slb = set(slb)
    slb = list(slb)
    slb.sort()
    with open(sylaby_uniq, 'w') as kw:
        kw.write('\n'.join(slb))
    print("\nSylaby podzielone unikalne i posortowane zapisane do pliku: ", sylaby_uniq)

    # print("\n\nKONIEC!!!\n\n")

###################################################

dziel_na_sylaby(korpusname)
