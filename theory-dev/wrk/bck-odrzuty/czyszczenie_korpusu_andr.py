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
Skrypt {skrypt} służy do wstępnej obróbki korpusu
czy to w częściach, czy w całości:
 
 - zmniejszanie liter
 - wszyskie spacje zmienić na \n
 
 - ostatnia czynność:
   - dopuścić tylko określone znaki (tj. polski alfabet)
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
        #korpusname = "ktest"
        korpusname = "data/korpus/wikipedia.txt"
        #slownikname = "slowntest"
    except ValueError:
        print("Sorry, nie rozumim.")
        #better try again... Return to the start of the loop
        continue
    else:
        print("Przetwarzamy ", korpusname)
        #print("Przetwarzamy ", slownikname)
        # and go out the loop
        break


###################################################

def czyszczenie_korpusu(sciezka_do_pliku, limit=None, stats=False):
    ## otwiera plik jako string
    with open(korpusname, 'r') as kn:
        korpus = kn.read()
        korpus = re.sub(r"\s+", "\n", korpus)
        korpus = korpus.lower()
        korpus = korpus.split("\n")

        # Do testów korpus ograniczamy do wysokości limitu
        korpus = korpus[:limit]

        chwilowy_korpus = []
        for ob in korpus:
            if isinstance(ob, str):
                ob = ''.join(filter(str.isalnum,ob))
                chwilowy_korpus.append(ob)

        korpus = list(filter(None, chwilowy_korpus))

        # 2.1. Jeżeli dane słowo w korpusie składa się z choćby jednego znaku,
        # który nie mieści się w zakresie, skasuj to słowo.

        dozwolone_znaki = ['a','ą','b','c','ć','d', 'e','ę','f','g','h',
        'i','j', 'k','l','ł','m','n','ń','o','ó','p', 'q','r','s','ś','t',
        'u','v', 'w','x','y','z','ż','ź']

        print("\n\nDozwolone znaki: \n\n",dozwolone_znaki)

        # Zakładam listę niedozwolonych wyrazów/znaków
        niedozwolone_slowa = []
        # Zakładam listę słów z dozwolonymi znakami
        korpus_przesiany = []


        for slowo in korpus:
            if isinstance(slowo, str):
                if any(z not in dozwolone_znaki for z in slowo):
                    # print(slowo)
                    niedozwolone_slowa.append(slowo)
                else:
                    # print('OK')
                    korpus_przesiany.append(slowo)



        if stats:
            print(f'                           przed    po')
            print(f'Korpus                     {len(korpus)} {len(korpus_przesiany)}')
            print(f'Korpus unikalnych słów:    {len(set(korpus))} {len(set(korpus_przesiany))}')
            print('\n')
            print(f'lista słów niedozwolonych: {len(niedozwolone_slowa)} unikalnych słów: {len(set(niedozwolone_slowa))}')
            print("\nKorpus przed przesiewem: \n",korpus[:27])
            print("\nKorpus po przesianiu:\n",korpus_przesiany[:27])
    return korpus_przesiany, niedozwolone_slowa


korpus_przesiany, niedozwolone_slowa = czyszczenie_korpusu(korpusname, 1000, True)
