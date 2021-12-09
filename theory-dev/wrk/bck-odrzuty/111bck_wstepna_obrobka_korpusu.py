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
        korpusname = "data/korpus/wiki.test"
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

# 1. Pobrać korpus i jego słowa do listy


## otwiera plik do listy
# with open(korpusname) as kn:
#     korpus = kn.readlines()
#     for x in korpus:
#         korpus.extend()
# usuwam `\n` z końca linii
# korpus = [x.strip() for x in korpus] 
# print("Wycinek korpusu (przed przesiewem): ",korpus[:27])

znaki_specjalne = ' !@#$%^&*\(\)_+-=,./;\'<>?:\"[]\\{}|'

## otwiera plik jako string
with open(korpusname, 'r') as kn:
    # spacje na \n
    #korpus = kn.read().replace(' ','\n')
    korpus = kn.read()
    #korpus = "\n".join(re.sub(r"\s+", "\n", korpus))
    korpus = re.sub(r"\s+", "\n", korpus)
    # WIELKIE litery na małe
    korpus = korpus.lower()
    # Aby nie usunęło zbyt wiele tekstu, jednakowoż usuwam pewne znaki zawczasu
    #korpus = [korpus.replace(z,"\n") for z in znaki_specjalne]
    #for z in znaki_specjalne:
     #   korpus.replace(z,"\n")
    korpus.translate ({ord(c): "\n" for c in "!@#$%^&*()[]{};:,./<>?\|`~-'\"=_+"})
    #korpus = str(korpus)
    #korpus = korpus[1:]
    korpus = korpus.split("\n")
    korpus = [x.strip() for x in korpus]
print("\n\nWycinek korpusu (przed przesiewem): \n\n",korpus[:27])


# 2.0. Jeszcze raz zamieniam spacje w \n - metodą jak w pętli poniżej

# spacja = ' '
# brejk = '\n'

# for test_string in korpus:
    # test_string = list(test_string.replace(spacja,brejk))
    # korpus.extend(test_string)




# 2.1. Jeżeli dane słowo w korpusie składa się z choćby jednego znaku,
# który nie mieści się w zakresie, skasuj to słowo.

dozwolone_znaki = ['a','ą','b','c','ć','d',
'e','ę','f','g','h','i','j',
'k','l','ł','m','n','ń','o','ó','p',
'q','r','s','ś','t','u','v',
'w','x','y','z','ż','ź']

print("\n\nDozwolone znaki: \n\n",dozwolone_znaki)

# Zakładam listę niedozwolonych wyrazów/znaków
niedozwolone_slowa = []

# test_lista = ['zażółć','gęślą','jaźń','„czesky','marek','’puskta']
# print("Test lista przed przesiewem:\n",test_lista)

for test_string in reversed(korpus):
    if any(z not in dozwolone_znaki for z in test_string):
        # print(test_string)
        korpus.remove(test_string)
        niedozwolone_slowa.append(test_string)
    #else:
        # print('OK')
     #   niedozwolone_slowa.append(test_string)

print("\n\nKorpus po przesianiu:\n\n",korpus[:27])


# 3. Zapisz poprawioną listę do pliku

korpuswynik = korpusname + '_dozwolone_znaki'


with open(korpuswynik, 'w') as kw:
    kw.write('\n'.join(korpus))

print("Dozwolone zapisane do pliku ",korpuswynik)

niedozwolone_slowa_file = korpusname + '_niedozwolone'

with open(niedozwolone_slowa_file, 'w') as kw:
    kw.write('\n'.join(niedozwolone_slowa))

print("\n\nNiedozwolone zapisane do pliku: ",niedozwolone_slowa_file)

print("\n\nKONIEC!!!\n\n")