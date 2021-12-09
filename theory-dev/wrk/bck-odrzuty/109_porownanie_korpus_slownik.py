#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys, re
import statistics

###################################################
### ZAJAWKA i pobranie nazwy pliku do przetworzenia
# nazwa tego skryptu
from pathlib import Path
#Path(__file__).name    # ScriptName.py
#Path(__file__).stem    # ScriptName

zajawka1 = """
Skrypt {skrypt} służy do 
podzielenia pliku tekstowego 
zawierającego korpus językowy
na sylaby.
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
        korpusname = "kst"
        slownikname = "slsl"
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

# 1. Pobrać korpus

with open(korpusname) as kn:
    korpus = kn.readlines()
# usuwam `\n` z końca linii
korpus = [x.strip() for x in korpus] 

print(korpus[108:123])

# 2. Pobrać słownik z wyrazami podzielonymi na sylaby

with open(slownikname) as sn:
    slownik = sn.readlines()
# usuwam `\n` z końca linii
slownik_syl = [x.strip() for x in slownik] # lista słów podzielonych na sylaby
print("slownik_syl zrobiony")
slownik = [re.sub('=','',x) for x in slownik_syl] # lista słów nie podzielonych na sylaby
print("slownik zrobiony")
slownik_dict = {} # słownik z powyższych list {'słowo':'sło=wo'}
print("slownik_dict zadeklarowany")

for i in slownik:
    for x in slownik_syl:
        slownik_dict[i] = x
        
for linia in slownik:
	linia = linia.strip()
	slownik_dict[linia.replace('=', '')] = linia.split('=')


print(slownik_dict[108:128])


# 3. Wyciągnąć z korpusu do osobnego pliku wyrazy, których nie ma w słowniku

for k in range(len(korpus)):
    for s in range(len(slownik)):
        #slowo = re.sub('=','',slownik[s])
        if slowo == korpus[k]:
            print(slownik[s],' ',korpus[k])
        else:
            print(korpus[k],' ',slownik[s])
            # slownik[s] += korpus[k]
        #if korpus[k] not in slownik:


# 3.1. Słowa, które nie są słowami (np. cyfry) wydzielić do osobnego pliku.
# 3.1.1. Usunąć z korpusu słowa, które nie są słowami.
# 3.2. Ręcznie poprawić plik ze słowami, których nie znaleziono w słowniku (ok. 500K wg diff)
# 3.2.1. Słowa nie podzielone na sylaby podzielić przy pomocy pyHyphen (do ponownej ręcznej obróbki)
# 3.3. Podzielone słowa dołączyć do nowego słownika.
# 4. Podzielić korpus na sylaby wg nowego słownika
# 5. STATY
# 5.1.Wygenerować słownik częstości sylab z korpusu
# 5.1.1. Wygenerować słownik częstości nagłosów z korpusu
# 5.1.1.1. Słownik porównawczy częstości nagłosów korpus-słownik
# 5.1.2. Wygenerować słownik częstości wygłosów z korpusu
# 5.1.2.1. Słownik porównawczy częstości wygłosów korpus-słownik
# 5.2. Wygenerować słownik unikalnych sylab z korpusu
# 5.2.1. Wygenerować słownik unikalnych nagłosów
# 5.2.2. Wygenerować słownik unikalnych wygłosów


# jak masz listę wszystkich słów, to możesz wykorzystując komendę set(lista) wyciągnąć unikalne wpisy
# list.count(value)  podaje ci liczbę wystąpień
# tworzysz sobie {słowo: {count: liczba wystąpień, syl: [sylaba 1, sylaba 2, ...]}
# następnie tworzysz kolejny słownik {sylaba: count, ....}
# for key in słownik_słów:
   # for syl in słownik_słow[key][syl]:
      # if syl not in słownik_sylab:
         # słownik_sylab[syl] = słownik_słów[key][count]
      # else:
          # słownik_sylab[syl] += słownik_słów[key][count]


# A owo słowo ma pochodzić ze słownika słów unikalnych, czy z set(korpus)?

# Andrzej Smirnow
# Może pochodzić z set(korpus)
# Podczas tworzenia jeśli nie ma podanego podziału na sylaby możesz podzielić je w inny sposób
# Możesz też jednocześnie zrzucać do oddzielnej listy 'ku pamięci'
# D = collections.Counter(korpus) stworzy ci słownik {slowo:liczba wystąpień,...}
# korpus = list() # korpus w postaci listy
# slownik_sylab = dict() # słownik {slowo: [podział na sylaby',...}
# d = collections.Counter(korpus)
# dd = dict()
# for key in d:
    # dd[key]={'liczba': d[key],'sylaby':slownik_sylab.get(key, podzial_na_sylaby(key)}
# w ostatniej linii podzial_na_sylaby() to funkcja która dzieli na sylaby słowo dla którego nie mamy znanego podziału. Na początek, póki jej nie mamy może zwracać [] - czyli pustą listę.
# są jeszcze funkcje typu map(), ale nie użyałem, więc nie wiem jak działają






# filename = open('liczby_sylab.txt', 'r')
# with open(filename, 'r') as file:
