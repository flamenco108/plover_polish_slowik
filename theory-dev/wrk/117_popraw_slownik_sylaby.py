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
Skrypt {skrypt} służy do: 
 - poprawienia pliku podzielonego na sylaby przy pomocy regex
 
Wciąga z pliku tekstowego do listy. Plik tekstowy ułożony tak:
sło=wo
dru=gie

 
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
        korpusname = "../data/do_korpus/sjpng_up"
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


# def wydziel_sylaby(lista):
    # sylaby = []
    # for s in lista:
        # syl = s.split('=')
        # # print(syl)
        # for x in syl:
            # sylaby.append(x)
    # sylaby = set(sylaby)
    # return sylaby
skroty = 'skroty.txt'
def usun_skroty(lista,skroty):
# plik słów wcześniej pobrany do listy
# pobiera z pliku do drugiej listy skróty
# usuwa te skróty z listy
    with open(skroty, 'r') as kn:
        skroty = kn.readlines()
        skroty = [x.strip() for x in skroty] # usuwam '\n' itp
        skroty = list(filter(None, skroty)) # usuwam puste linie

    for l in lista:
        if l in skroty:
            lista.remove(l)
            #print(l)
    return lista


# def czyszczenie(lista, patterny):
    # wynikmatch = []
    # wyniksub = []
    # for k in patterny:
        # print(k)
        # for s in lista:
            # if re.match(k,s):
                # # print(s)
                # zm = re.sub(r"{}".format(k), r"{}".format(patterny[k]), s)
                # zm = zm.split('=')
                # #print('s: ',s,'ZM: ',zm)
                # for z in zm:
                    # wynikmatch.append(z)
            # else:
                # # print(k,'->',patterny[k])
                
                # wyniksub.append(s)
    # wynikmatch = list(set(wynikmatch))
    # wyniksub = list(set(wyniksub))
    # return wynikmatch, wyniksub

def czyszczenie(lista, patterny):
    wynik = []
    for s in lista:
        for k in patterny:
            zm = re.sub(r"{}".format(k), r"{}".format(patterny[k]), s)
            wynik.append(zm)
    return wynik



##############



patterny = { 
# słowa zaczynające się na ą i ę
'^[ąę].*$' : '',
# słowa nie zawierające samogłosek
'^[^aeiouóyąę=]+$' : '',
# jednosylabowe kończące się na niedozwolone ó
'^[^aeiouóyąę=]+ó$' : '',
#'^([^aeiouyąęó]*[aeouąęó])([^aeiouyąęó]+[aeouąęó][^aeiouyąęó]*)$' : '\\1=\\2',
#'^u$' : ''
#'^$' : ''
#'^$' : ''
# pojedyncze i specjalne przypadki
'^ba=aar=dzo$' : 'bar=dzo'
#'^.*[ąęółńćśżź]+.*(a{2,9}|e{2,9}|i{3,9}|o{2,9}|u{2,9}|ó{2,9}|y{2,9}|ą{2,9}|ę{2,9}).*$' : ''
#'^$' : ''
#'^$' : ''
#'^$' : ''
#'^$' : ''
}





plik = otworz_plik_lista(korpusname)
print('PLik otwarty')

plik1 = usun_skroty(plik, skroty)
plik1 = set(plik1)
plik1 = list(plik1)
plik1.sort()
print('skroty usuniete')

listap = czyszczenie(plik1, patterny)
listap = set(listap)
listap = list(listap)
listap.sort()
print('czyszczenie zrobione')



# print('Czyszczenie sylab: \n')
# wynikmatch, wyniksub = czyszczenie_sylab(sylaby, patterny)

print('\nLiczba plik: ', len(plik))
print(plik[:200])

print('\nLiczba plik1: ', len(plik1))
print(plik1[:200])

print('\nLiczba listap: ', len(listap))
print(listap[:200])


#print('\nLiczba match: ', len(wynikmatch))
#print(sylaby)
#print(len(sylaby))
#slowo_wystepuje, slowo_niewystepuje = sprawdz_w_slowniku(plik,jezyki)
##############

# Zapisywanie do pliku

# slowa_wyst = korpusname + '_slowa_wystepujace'
# slowa_niewyst = korpusname + '_slowa_niewystepujace'


# with open(slowa_wyst, 'w') as kw:
        # kw.write('\n'.join(set(slowo_wystepuje)))
# print("\nSłowa występujące zapisane do pliku: ",slowa_wyst)

# # niedozwolone_slowa_file = korpusname + '_niedozwolone'

# with open(slowa_niewyst, 'w') as kw:
    # kw.write('\n'.join(slowo_niewystepuje))
# print("\nSłowa niewystępujące zapisane do pliku: ", slowa_niewyst)


print("\n\nKONIEC!!!\n\n")

###################################################

#sprawdzaj_w_slownikach(korpusname)
