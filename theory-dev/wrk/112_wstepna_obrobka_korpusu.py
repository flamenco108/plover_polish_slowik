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

 - ostatnia czyniedozwolone_slowaość:
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
        korpusname = "../data/korpus/nieobr/sjp_odm.txt"
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
        # usuwa wszelkie przejawy spacji i zamienia na \n
        korpus = re.sub("\s+", "\n", korpus)
        # zamienia myślnik na \n w celach ochrony dwuczłonowych wyrazów
        korpus = re.sub("-", "\n", korpus)
        # usuwa rzymskie liczby
        #korpus = re.sub(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", "\n", korpus)
        # wszystko do małych literek
        korpus = korpus.lower()

        # zamienia string w listę
        korpus = korpus.split("\n")


        # Do testów korpus ograniczamy do wysokości limitu
        korpus = korpus[:limit]

        # stats - zbieram dane statystyczne przed przesiewem
        lista = len(korpus)
        lista_uniq = len(set(korpus))
        korpus_przed = korpus[:limit]

        # usuwa wszystko, co nie jest literką Unicode
        chwilowy_korpus = []
        for slowo in korpus:
            if isinstance(slowo, str):
                #ob = re.sub(r"\s+", "\n", ob)
                # usuwa numeryki i inne znaki przestankowe
                slowo = ''.join(filter(str.isalnum,slowo))
                # usuwa samotne litery, które nie są partykułami
                slowo = re.sub(r"^[bcćdefghjklłmnńprsśtżźy]$", "\n", slowo)
                # usuwa rzymskie numerale czyli liczby
                #slowo = re.sub(r"^m{1,3}(cm|cd|d?c{1,3})(xc|xl|l?x{1,3})(ix|iv|v?i{2,3})$", "\n", slowo)
                chwilowy_korpus.append(slowo)

        # przy okazji usuwamy puste elementy listy
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
        #korpus_przesiany = []


        for slowo in korpus[:]:
            if isinstance(slowo, str):
                if any(z not in dozwolone_znaki for z in slowo):
                    # print(slowo)
                    niedozwolone_slowa.append(slowo)
                    korpus.remove(slowo)
                #else:
                #    # print('OK')
                #    korpus.remove(slowo)


        # stats - dane statystyczne po przesianiu
        lista_przesiana = len(korpus)
        lista_przesiana_uniq = len(set(korpus))
        lista_niedozwolona = len(niedozwolone_slowa)
        lista_niedozwolona_uniq = len(set(niedozwolone_slowa))


        if stats:
            print('\n    === STATYSTYKA ===    ')
            print('                           przed    po')
            print(f'Korpus                     {lista}   {lista_przesiana}')
            print(f'Korpus unikalnych słów:    {lista_uniq}   {lista_przesiana_uniq}')
            print('\n')
            print(f'lista słów niedozwolonych: {lista_niedozwolona}   unikalnych słów: {lista_niedozwolona_uniq}')
            print("\nKorpus przed przesiewem: \n",korpus_przed[:27])
            print("\nKorpus po przesianiu:\n",korpus[:27])
            print('\n    === STATYSTYKA ===    \n')

    return korpus, niedozwolone_slowa


korpus_przesiany, niedozwolone_slowa = czyszczenie_korpusu(korpusname, None, True)
#korpus_przesiany, niedozwolone_slowa = czyszczenie_korpusu(korpusname, 2000, True)


# 3. Zapisz poprawioną listę do pliku

korpuswynik = korpusname + '_dozwolone_znaki'


with open(korpuswynik, 'w') as kw:
    kw.write('\n'.join(korpus_przesiany))

print("\nDozwolone zapisane do pliku ",korpuswynik)

niedozwolone_slowa_file = korpusname + '_niedozwolone'

print("\nNiedozwolone słowa unikujemy i usuwamy cyfry przed zapisem do pliku.")
niedo_slo = [x for x in niedozwolone_slowa if not (x.isdigit() or x[0] == '-' and x[1:].isdigit())]
niedozwolone_slowa = set(niedo_slo)
niedozwolone_slowa = set(niedozwolone_slowa)

with open(niedozwolone_slowa_file, 'w') as kw:
    kw.write('\n'.join(niedozwolone_slowa))

print("\nNiedozwolone zapisane do pliku: ",niedozwolone_slowa_file)

print("\n\nKONIEC!!!\n\n")
