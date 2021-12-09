#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys
import statistics

###################################################
### ZAJAWKA i pobranie nazwy pliku do przetworzenia
# nazwa tego skryptu
from pathlib import Path
#Path(__file__).name    # ScriptName.py
#Path(__file__).stem    # ScriptName

zajawka = """
Skrypt {skrypt} służy do 
podzielenia pliku tekstowego 
zawierającego korpus językowy
na sylaby.

""".format(skrypt = Path(__file__).name)

print(zajawka)
###

### Pobierz nazwę pliku do przetworzenia
while True:
	try:
		filename = input("Podaj nazwę pliku: ")
	except ValueError:
		print("Sorry, nie rozumim.")
		#better try again... Return to the start of the loop
		continue
	else:
		print("Przetwarzamy ", filename)
		# and go out the loop
		break


###################################################

# 1. Pobrać korpus
# 2. Pobrać słownik z wyrazami podzielonymi na sylaby
# 3. Wyciągnąć z korpusu do osobnego pliku wyrazy, których nie ma w słowniku
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






#filename = open('liczby_sylab.txt', 'r')
with open(filename, 'r') as file:
