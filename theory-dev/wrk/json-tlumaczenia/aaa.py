#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys, re
# import statistics
import json

###################################################
### ZAJAWKA i pobranie nazwy pliku do przetworzenia
# nazwa tego skryptu
from pathlib import Path
#Path(__file__).name    # ScriptName.py
#Path(__file__).stem    # ScriptName

zajawka1 = """
Skrypt {skrypt} służy do:
 - wydzielenia sylab z wcześniej podzielonych na sylaby wyrazów,
 - podzielenia sylab na nagłos-głos-wygłos,
 - zapisanie tego wszystkiego do plików

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

        naglosy_json = "naglosy-left.json"
        wyglosy_json = "wyglosy-right.json"
        glosy_json = "glosy-middle.json"
        sylaby = "sylaby.txt"
    except ValueError:
        print("Sorry, nie rozumim.")
        #better try again... Return to the start of the loop
        continue
    else:
        print("Przetwarzamy ", naglosy_json)
        print("Przetwarzamy ", wyglosy_json)
        print("Przetwarzamy ", glosy_json)
        print("Przetwarzamy ", sylaby)
        print("")
        # and go out the loop
        break


###################################################
### FUNKCJE
###################################################

def otworz_plik_lista(plik):
#otwiera plik z listą stringów rozdzielonych \n i zwraca listę
    with open(plik, 'r') as kn:
        plik = kn.readlines()
        plik = [x.strip() for x in plik] # usuwam '\n' itp
        plik = list(filter(None, plik)) # usuwam puste linie
    return plik


def wydziel_sylaby(lista):
#z pliku z wyrazami podzielonymi na sylaby wydziela pojedyncze sylaby
    sylaby = []
    for s in lista:
        syl = s.split('=')
        # print(syl)
        for x in syl:
            sylaby.append(x)
    sylaby = set(sylaby)
    return sylaby

def otworz_json_dict(plik):
# otwiera plik JSON i wczytuje do slownika
    with open(plik) as json_file:
        dict = json.load(json_file)
    return dict


#def potnij_sylabe(sylaba,naglosy_lista,wyglosy_lista,glosy_lista):
#
#    sylaba_pocieta = []
#    # odcinam nagłos, reszta idzie dalej
#    # jeżeli nie znajdzie nagłosu, podaje dalej sylabę
#    def wybierz_naglos(naglosy_lista, sylaba):
#        for naglos in naglosy_lista:
#            if sylaba.startswith(naglos):
#                reszta = sylaba[len(naglos):]
#                naglos = naglos
#                break
#            else:
#                naglos = False
#                reszta = sylaba
#        return naglos, reszta
#
#    # pobieram resztę i odcinam wygłos
#    # to, co pozostało, powinno być głosem (śródgłosem) sylaby
#    # jeżeli nie znajdzie, podaje dalej resztę
#    def wybierz_wyglos(wyglosy_lista, glosy_lista, reszta):
#        for wyglos in wyglosy_lista:
#            for glos in glosy_lista:
#                if reszta.endswith(str(wyglos)) and reszta.startswith(glos):
#                    glos = glos
#                    wyglos = wyglos
#                    break
#                elif reszta.startswith(glos):
#                     #glos = reszta[len(glos):]
#                     glos = glos
#                     wyglos = False
#                     break
#                else:
#                    glos = False
#                    wyglos = False
#        return wyglos, glos
#
#    # teraz trzeba sprawdzić, czy zebrane części (nagłos, głos, wygłos)
#    # złożone do kupy dają nam daną sylabę
#    def porownanie_sylab(sylaba,naglos,glos,wyglos):
#        sylaba_pocieta = [naglos, glos, wyglos]
#        # skleja listę, zamienia False na string a potem na ''
#        sylspr = [str(sp) for sp in sylaba_pocieta]
#        sylaba_sprawdzana = ''.join(spr.replace('False','',1) for spr in sylspr)
#        print("sylaba sprawdzana: ",sylaba_sprawdzana)
#        if sylaba_sprawdzana == sylaba:
#            return naglos, glos, wyglos
#        return False, sylaba
#
#    nag, rest = wybierz_naglos(naglosy_lista,sylaba)
#    print("NAGŁOS+RESZTA: ",nag,rest)
#    wyg, glo = wybierz_wyglos(wyglosy_lista,glosy_lista,rest)
#    print("GŁOS+WYGŁOS: ",glo,wyg)
#
#    if porownanie_sylab(sylaba,nag,glo,wyg):
#        sylaba_pocieta = [nag,glo,wyg]
#        # print("sylaba pocieta: ",sylaba_pocieta)
#        return sylaba_pocieta
#    print("Nie udało się!")


def wybierz_naglos(naglosy_lista, sylaba):
  naglos = False
  reszta = sylaba
  for n in naglosy_lista:
    if sylaba.startswith(n):
      reszta = sylaba[len(n):]
      naglos = n
      break
  return naglos, reszta

def wybierz_wyglos(wyglosy_lista, sylaba):
  wyglos = False
  reszta = sylaba
  for w in wyglosy_lista:
    if sylaba.endswith(w):
      reszta = sylaba[:-len(w)]
      wyglos = w
      break
  return wyglos, reszta

def wybierz_glos(glosy_lista, sylaba):
  glos = False
  for g in glosy_lista:
    if sylaba == g:
      glos = g
      break
  return glos





#################### WYKONANIE ####################

## naglosy
nagg = otworz_json_dict(naglosy_json)
# zamien key i value
#nagg = {v: k for k, v in nagg.items()}
# sortuj wg key length
nag_dict = {}
for k in sorted(nagg,key=len,reverse=True):
    nag_dict[k] = nagg[k]
    nag_list = list(nag_dict.keys())
nag_list = sorted(nag_list,key=len,reverse=True)
print("Nagłosy, list:\n",nag_list,"\n")

## wyglosy
wygg = otworz_json_dict(wyglosy_json)
# zamien key i value
#wygg = {v: k for k, v in wygg.items()}
# sortuj wg key length
wyg_dict = {}
for k in sorted(wygg,key=len,reverse=True):
    wyg_dict[k] = wygg[k]
    wyg_list = list(wyg_dict.keys())
wyg_list = sorted(wyg_list,key=len,reverse=True)
print("Wygłosy, list:\n",wyg_list,"\n")

## glosy
gglo = otworz_json_dict(glosy_json)
# zamien key i value
#gglo = {v: k for k, v in gglo.items()}
# sortuj wg key length
glo_dict = {}
for k in sorted(gglo,key=len,reverse=True):
    glo_dict[k] = gglo[k]
    glo_list = list(glo_dict.keys())
glo_list = sorted(glo_list,key=len,reverse=True)
print("Głosy, list:\n",glo_list,"\n")

## sylaby
syl = otworz_plik_lista(sylaby)
print("Sylaby, list:\n",syl,"\n")


#syl = 'wgnieźdź'
#pocieta = potnij_sylabe(syl,nag_list,wyg_list,glo_list)
#print("POCIETA SYLABA: ",pocieta)

## odhaszuj to
#syl_dict = {}
#for s in syl:
#    print("+++++++++++++\nSYLABA: ",s)
#    pocieta = potnij_sylabe(s,nag_list,wyg_list,glo_list)
#    syl_dict[s] = list(pocieta)
#    print(syl_dict[s])
#    #print("POCIETA SYLABA: ",pocieta)
#print("++++++++++++\n")
#print(syl_dict)

syl_dict = {}

for sylaba in syl:
    print("SYLABA: ",sylaba)
    naglos, r1 = wybierz_naglos(nag_list, sylaba)
    wyglos, r2 = wybierz_wyglos(wyg_list, r1)
    glos = wybierz_glos(glo_list, r2)

    slowo_ponownie_zlozone = ''

    #if not naglos:
    #    print("", "nie znaleziono na liście pasującego NAGŁOSU")
    #else:
    #    slowo_ponownie_zlozone += naglos

    #if not glos:
    #    glos = r2
    #    print("", f"nie znaleziono na liście GŁOSU: {r2}")
    #    slowo_ponownie_zlozone += glos

    #if not wyglos:
    #    print("", "nie znaleziono na liście pasującego WYGŁOSU")
    #else:
    #    slowo_ponownie_zlozone += wyglos

    #print(f"WYNIK: {slowo_ponownie_zlozone}")
    syl_dict[sylaba] = [naglos,glos,wyglos]
    print(syl_dict[sylaba])

print(syl_dict)

















###################################################
print("\n\nKONIEC!!!\n\n")
###################################################
