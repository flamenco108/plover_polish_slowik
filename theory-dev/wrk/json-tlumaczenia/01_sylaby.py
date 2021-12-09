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
 - podzielenia sylab na nagłos+głos+wygłos (lewa, środkowa i prawa strona klawiry)
 - przetłumaczenia tych ww. części na kod STENO (na podst słowników JSON)
 - zapisania wyniku do pliku JSON

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

        naglosy_json = "naglosy-trillo-test.json"
        #naglosy_json = "naglosy-left-test.json"
        wyglosy_json = "wyglosy-trillo-test.json"
        #wyglosy_json = "wyglosy-right-test.json"
        # tu mamy opcje
        glosy_json = "glosy-trillo-test.json"
        #glosy_json = "glosy-middle-test.json"
        # sylaby-plik - pełne sylaby lub plik testowy
        sylaby = "sylaby-plik"
        #sylaby = "sylaby-test.txt"
        # plik do zapisu
        plik_json = "plover_polish_trillo.json"
        #plik_json = "plover_polish_slowik.json"
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

def wybierz_naglos(naglosy_lista, sylaba):
# wybiera nagłos z sylaby na podstawie listy nagłosów
    naglos = False
    reszta = sylaba
    for n in naglosy_lista:
        if sylaba.startswith(n):
            reszta = sylaba[len(n):]
            naglos = n
            break
    return naglos, reszta

def wybierz_wyglos(wyglosy_lista, sylaba):
# wybiera wygłos z sylaby (ost. spółgł.) na podst. listy wygłosów
    wyglos = False
    reszta = sylaba
    #print("wybi_wyg przed for:\t| wyglos: ",wyglos,"\t| reszta: ",reszta,"\t| naglos: ",naglos)
    for w in wyglosy_lista:
        if sylaba.endswith(w):
            #reszta = sylaba[:-len(w)]
            reszta = re.sub(r"(.*){}".format(w),r"\1",sylaba)
            wyglos = w
            #print("wybi_wyg po if:\t| wyglos: ",wyglos,"\t| reszta: ",reszta,"\t| naglos: ",naglos)
            break
    return wyglos, reszta

def wybierz_glos(glosy_lista, sylaba):
    # rozpoznaje, czy głos jest poprawny na podst. listy głosów
    glos = False
    #print("wybierz_glos przed for:\t| glos: ",glos,"\t| wyglos: ",wyglos,"\t| sylaba: ",sylaba,"\t| naglos: ",naglos)
    for g in glosy_lista:
        if sylaba == g:
            glos = g
            #print("wybierz_glos po if:\t| glos-g: ",glos,"\t| wyglos: ",wyglos,"\t| sylaba: ",sylaba,"\t| naglos: ",naglos)
            break
    return glos

def podmien_xlos(ngw_dict, ngwglos):
# podmienia naglos, glos, wyglos na odpowiedniki w kodzie steno
# wzięte z odpowiednich plików JSON pociągniętych do słowników
    for g in ngw_dict:
        if ngwglos == g:
            ngwglos = ngw_dict[g]
            break
    return ngwglos



print("###################################################")
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
#print("Nagłosy, list:\n",nag_list,"\n")
#print("Nagłosy, dict:\n",nag_dict,"\n")

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
#print("Wygłosy, list:\n",wyg_list,"\n")
#print("Wygłosy, dict:\n",wyg_dict,"\n")

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
#print("Głosy, list:\n",glo_list,"\n")
#print("Głosy, dict:\n",glo_dict,"\n")

## sylaby
syl = otworz_plik_lista(sylaby)
#print("Sylaby, list:\n",syl,"\n")



print("###################################################")
### robimy sylaby
syl_dict = {}

for sylaba in syl:
    #print("----\nSYLABA: ",sylaba)
    naglos, r1 = wybierz_naglos(nag_list, sylaba)
    #print("WYBIERZ_NAGLOS wyn: \tnaglos, r1: ",naglos,r1)
    wyglos, r2 = wybierz_wyglos(wyg_list, r1)
    #print("WYBIERZ_WYGLOS wyn: \twyglos, r2: ",wyglos,r2)
    glos = wybierz_glos(glo_list, r2)
    #print("WYBIERZ_GLOS wyn: \tglos: ",glos)

    #slowo_ponownie_zlozone = ''

    #if not naglos:
    #    print("", "nie znaleziono na liście pasującego NAGŁOSU")
    #else:
    #    slowo_ponownie_zlozone += naglos
    #if not glos:
    #    glos = r2
    #    print("", f"nie znaleziono na liście GŁOSU: {r2}")
    #else:
    #    slowo_ponownie_zlozone += glos
    #if not wyglos:
    #    print("", "nie znaleziono na liście pasującego WYGŁOSU")
    #else:
    #    slowo_ponownie_zlozone += wyglos
    #print(f"WYNIK: {slowo_ponownie_zlozone}")

    syl_dict[sylaba] = [naglos,glos,wyglos]
    #print(syl_dict[sylaba])

print("###################################################")
#print(syl_dict)

print("###################################################")

steno_dict = {}

for s in syl_dict:
    #print("--------")
    #print("SYLABA: ",s)
    #print("PODZIAŁ: ",syl_dict[s])
    ngw = syl_dict[s]
    naglos = ngw[0]
    glos = ngw[1]
    wyglos = ngw[2]
    naglos = podmien_xlos(nag_dict,naglos)
    glos = podmien_xlos(glo_dict,glos)
    wyglos = podmien_xlos(wyg_dict,wyglos)
    #print("wynik: ",naglos,glos,wyglos)
    naglos = naglos if naglos else ''
    glos = glos if glos else ''
    wyglos = wyglos if wyglos else ''
    syl_steno = naglos+glos+wyglos
    #print("steno: ",syl_steno)
    steno_dict[s] = syl_steno

# steno_dict = słownik {'sylaba':'STENOSYLABA'}

# sortuj wg kluczy alfabetycznie
sd = steno_dict
steno_dict = {}
for k in sorted(sd):
    steno_dict[k] = sd[k]
# zamien key i value
steno_dict = {v: k for k, v in steno_dict.items()}

# steno_dict = słownik {'STENOSYLABA':'sylaba'}

#print("STENO_DICT: ",steno_dict)

json_dict = json.dumps(steno_dict,ensure_ascii=False,indent=2)

#print(json_dict)

print("Zapis do pliku: ",plik_json)
f = open(plik_json,"w")
f.write(json_dict)
f.close()


print("\n###################################################")
###################################################
print("\nKONIEC!!!\n\n")
###################################################
