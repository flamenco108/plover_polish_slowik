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
Skrypt {skrypt} służy do obliczania średniej i mediany liczby sylab
słów zawartych we wskazanym pliku

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



#filename = open('liczby_sylab.txt', 'r')
with open(filename, 'r') as file:
	# tworzę listę z obiektami int i usuwam znaki "\n"
	# lines = map(int,file.read().splitlines())
	lines=[int(l) for l in file.read().splitlines()]
	# suma wartości obiektów listy
	total = sum(lines)
	# liczba obiektów listy
	leng = len(lines)
	print ("Suma sylab: %d" % (total))
	print ("Liczba sylab: %d" % (leng))
	average = total / leng
	print ("Średnia liczba sylab we wszystkich słowach w korpusie: %d" % (average))
	# liczę medianę
	median = statistics.median(lines)
	print("Mediana liczby sylab we wszystkich słowach w korpusie: %d" % (median))
