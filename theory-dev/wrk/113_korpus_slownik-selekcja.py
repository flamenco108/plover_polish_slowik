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
na sylaby taką oto metodą:

 - sprawdza, czy słowo z korpusu występuje w słowniku
 słów podzielonych na sylaby
 - jeżeli występuje, słowo podzielone zastępuje słowo niepodzielone
 - jeżeli nie występuje, słowo zostaje skierowane do dalszej obróbki

Dalsza obróbka:
 - słowo niepodzielone zapisane do pliku korpus_niepodzielone (sort, uniq)
 - załadować korpus_niepodzielone
 - słowa podzielić przez pyHyphen i zapisać do pliku korpus_niepodz_podzielone

Dalsza obróbka poza plikiem {skrypt}
 - obróbka ręczna korpus_niepodz_podzielone
 - doklejenie pliku do korpusu

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
        # korpusname = "../data/korpus-test"
        # slownikname = "../data/slownik-test"
        korpusname = "../data/do_korpus/nazwy_geogr"
        slownikname = "../data/slownik"
    except ValueError:
        print("Sorry, nie rozumim.")
        #better try again... Return to the start of the loop
        continue
    else:
        print("Przetwarzamy ", korpusname)
        print("Przetwarzamy ", slownikname)
        print("")
        # and go out the loop
        break


###################################################

def otworz_pliki(sciezka_do_korpusu, sciezka_do_slownika):
    with open(slownikname, 'r') as sn:
        slownik = sn.readlines()
        slownik = [x.strip() for x in slownik]
        slownik_dict = {} # słownik z powyższych {'słowo':['sło','wo']}
        slowa_d = []
        sylaby_d = []
        # slownik_dict_klucze = ['slowo','sylaby']
        for linia in slownik:
            linia = linia.strip()
            slowa = linia.replace('=','')
            slowa_d.append(slowa)
            #print(slowa)
            sylaby_slowa = linia.split('=')
            sylaby_d.append(sylaby_slowa)
            #print(sylaby_slowa)

        slownik_dict = {key: value for key, value in zip(slowa_d,sylaby_d)}

    # otwieram korpus i do listy
    with open(korpusname, 'r') as kn:
        korpus = kn.readlines()
        korpus = [x.strip() for x in korpus]
        # sklejam slowa_d z korpus, żeby w korpus wystąpiło każde słowo ze słownika przynajmniej raz!
        korpus = korpus + slowa_d

    return slownik_dict, korpus

# 1. Pobrać słownik i korpus słów podzielonych na sylaby - do listy
slownik_dict, korpus = otworz_pliki(korpusname, slownikname)
print("\nSłownik oraz korpus pobrane.")

# print("\nSłownik_dict: ")
# print(slownik_dict)
# print("\nKorpus: ")
# print(korpus)

# 2. Porównać listę i dict w pętli

print("\n=== Porównanie korpusu i słownika ===\n")

# 2.1. Które słowa z korpusu nie występują w słowniku - do osobnej listy
korpus_uniq = set(korpus)
korpus_niepodzielone = []
korpus_podzielone = []
for s in korpus_uniq:
    #for k in slownik_dict.keys():
        if s not in slownik_dict.keys():
            korpus_niepodzielone.append(s)
        else:
            sld = '='.join(slownik_dict[s])
            korpus_podzielone.append(sld)


print('Sortowanie list')
korpus_niepodzielone.sort()
korpus_podzielone.sort()

# print("\nSłowa niepodzielone: ")
# print(korpus_niepodzielone)




# # 2.2. Policzyć wystąpienia słów z korpusu
# # DOPIERO W OSTATNIM PRZEBIEGU, KIEDY ZOSTANIE POPRAWIONY!!! DOCELOWO!!!!
# # dict zawierający słowo: liczba_wystąpień
# def licz_wystapienia(lista, slowo):
    # try:
        # lista[slowo] = lista[slowo] + 1
    # except KeyError as e:
        # lista[slowo] = 1
    # return

# korpus_licz = {}
# for slowa in korpus:
    # licz_wystapienia(korpus_licz, slowa)
# #for k, v in korpus_licz.items():
# #    #print("Key ", k, " has occurred ", str(v), " times")
# #    print(k, str(v))
# print("\nSłowa:liczba wystąpień w korpusie: ")
# print(korpus_licz)
# ###########

# # 2.3. Połączyć słownik z listą wystąpień oraz słownik z wyrazami podzielonymi

# slownik_licz = {slowo: [slownik_dict[slowo], korpus_licz[slowo]] for slowo in slownik_dict}
# print("\nSłownik z liczbą wystąpień: ")
# print(slownik_licz)




# 3. Zrzut do plików

korp_plik =  korpusname + '_niepodzielone'
korp_slownik = korpusname + '_podzielone'

with open(korp_plik, 'w') as kw:
    kw.write('\n'.join(korpus_niepodzielone))
print("\nSylaby podzielone zapisane do pliku", korp_plik)
# print("\nSylaby podzielone zapisane do pliku:\n",'\n'.join(korpus_niepodzielone))

with open(korp_slownik, 'w') as kw:
    kw.write('\n'.join(korpus_podzielone))
print("\nSylaby podzielone zapisane do pliku", korp_slownik)
# print("\nSylaby podzielone zapisane do pliku:\n",'\n'.join(korpus_niepodzielone))


print("\n\nKONIEC!!!\n\n")
