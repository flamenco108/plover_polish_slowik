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
Skrypt {skrypt} służy do 
pozostawienia w pliku korpusu językowego
wyłącznie liter z polskiego alfabetu.
Ma wyłączyć inne znaki oraz cyfry.
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
        korpusname = "korptest"
        slownikname = "slowntest"
    except ValueError:
        print("Sorry, nie rozumim.")
        #better try again... Return to the start of the loop
        continue
    else:
        print("Przetwarzamy ", korpusname)
        print("Przetwarzamy ", slownikname)
        # and go out the loop
        break


###################################################

# 1. Pobrać korpus i jego słowa do listy

with open(korpusname) as kn:
    korpus = kn.readlines()
# usuwam `\n` z końca linii
korpus = [x.strip() for x in korpus] 

print("Wycinek korpusu (przed przesiewem): ",korpus[108:216])



# 2. Jeżeli dane słowo w korpusie składa się z choćby jednego znaku,
# który nie mieści się w zakresie, skasuj to słowo.

dozwolone_znaki = ['a','ą','b','c','ć','d',
'e','ę','f','g','h','i','j',
'k','l','ł','m','n','ń','o','ó','p',
'q','r','s','ś','t','u','v',
'w','x','y','z','ż','ź']

print(dozwolone_znaki)

# test_lista = ['zażółć','gęślą','jaźń','„czesky','marek','’puskta']
# print("Test lista przed przesiewem:\n",test_lista)

for test_string in korpus:
    if any(z not in dozwolone_znaki for z in test_string):
        # print(test_string)
        korpus.remove(test_string)
    # else:
        # print('OK')

print("Korpus po przesianiu:\n",korpus[108:216])

print("\n\nKONIEC\n\n")