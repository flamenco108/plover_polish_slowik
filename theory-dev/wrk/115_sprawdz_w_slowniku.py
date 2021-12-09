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
Skrypt {skrypt} służy do sprawdzenia, czy dane słowo
to rzeczywiście słowo w jakimkolwiek języku.
Sprawdzanie odbędzie się w językach:
pl_PL, de_DE, en_US, en_GB, fr, pt_PT, pt_BR, cs, cs_CZ,
hr_HR, hu_HU, es_ES

 
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
        korpusname = "../data/korpus/korpusn_uniq"
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

def otworz_plik_lista(plik):
#otwiera plik z listą stringów rozdzielonych \n i zwraca listę
    with open(plik, 'r') as kn:
        plik = kn.readlines()
        plik = [x.strip() for x in plik] # usuwam '\n' itp
        plik = list(filter(None, plik)) # usuwam puste linie
    return plik

def sprawdz_w_jezyku(slowo,jezyk):
    import enchant # w razie potrzeby trzeba zaktualizować listę języków przez instalację odpowiednich pakietów myspell
    d = enchant.Dict(jezyk)
    if d.check(slowo) or d.check(slowo.capitalize()) or d.check(slowo.title()):
        sd = True
    else:
        sd = False
    return sd


def sprawdz_w_slowniku(slownik,jezyki):
# jako parametr przyjmuje listę słów oraz listę języków
    slowo_wystepuje = [] # lista słów, które występują w którymkolwiek słowniku
    slowo_niewystepuje = [] # lista słów, które nie występują w żadnym słowniku
    import enchant # w razie potrzeby trzeba zaktualizować listę języków przez instalację odpowiednich pakietów myspell
    for j in jezyki:
        d = enchant.Dict(j)
        print('\n+++++++++++++ ',j,' +++++++++++++\n')
        for s in slownik:
            if sprawdz_w_jezyku(s,j):
                slowo_wystepuje.append(s)
                slownik.remove(s)
                # print('TAK=                ')
            # print('----------- ',s,' -----------')
    slowo_wystepuje = set(slowo_wystepuje)
    slowo_niewystepuje = set(slownik)
    return slowo_wystepuje, slowo_niewystepuje


jezyki = ['pl_PL', 'de_DE', 'fr_FR', 'en_US', 'en_GB', 'es_ES', 'cs_CZ', 'pt_BR', 'pt_PT', 'hu_HU' ]

##############
plik = otworz_plik_lista(korpusname)
slowo_wystepuje, slowo_niewystepuje = sprawdz_w_slowniku(plik,jezyki)
##############

# Zapisywanie do pliku

slowa_wyst = korpusname + '_slowa_wystepujace'
slowa_niewyst = korpusname + '_slowa_niewystepujace'


with open(slowa_wyst, 'w') as kw:
        kw.write('\n'.join(set(slowo_wystepuje)))
print("\nSłowa występujące zapisane do pliku: ",slowa_wyst)

# niedozwolone_slowa_file = korpusname + '_niedozwolone'

with open(slowa_niewyst, 'w') as kw:
    kw.write('\n'.join(slowo_niewystepuje))
print("\nSłowa niewystępujące zapisane do pliku: ", slowa_niewyst)


print("\n\nKONIEC!!!\n\n")

###################################################

#sprawdzaj_w_slownikach(korpusname)
