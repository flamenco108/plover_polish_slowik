#!/bin/bash

if [ $# -eq 0 ]; then
	echo ""
	echo "Skrypt $0 służy do:"
	echo "wygenerowania listy sylab ze wskazanego słownika"
	echo "wygenerowania nagłosów i wygłosów ze wskazanego słownika"
    echo ""
	echo "Wywolanie: $0 nazwa pliku do przetworzenia"
	echo "---------------------------------------------------------------------"
	echo ""
	exit 1
fi

plik=$1
nazwa=${plik%.*}
naglosy=$nazwa-naglosy.txt
wyglosy=$nazwa-wyglosy.txt


echo "Biorę $plik" 


echo "Sortuję $plik"
sort $plik > $nazwa-01.tmp
echo "Unikuję $plik"
uniq $nazwa-01.tmp > $nazwa-02.tmp && rm $nazwa-01.tmp
echo "Robię sylaby z $plik"

sed -e 's/=/\n/g' $nazwa-02.tmp  > $nazwa-sylaby && rm $nazwa-02.tmp

echo "Robię plik unikalnych sylab"
cat $nazwa-sylaby | uniq > $nazwa-syl-unik


echo "Robię nagłosy i wygłosy z $plik"
cat $nazwa-sylaby | \

awk 'BEGIN {FS="[aeiouóyąę]"}{print $1}' > nag01.tmp

cat $nazwa-sylaby | \
#awk 'BEGIN {FS="[aeiouóyąę]"}{print $2}' > nag02.tmp
#gawk -i inplace 'BEGIN {FS="[aeiouóyąę]"}{print $2}'  > nag02.tmp
gawk 'BEGIN {FS="[aeiouóyąę]"}{print $2}'  > nag02.tmp

cat nag01.tmp | sort | uniq > $naglosy && rm nag01.tmp
cat nag02.tmp | sort | uniq > $wyglosy && rm nag02.tmp

echo "Liczba nagłosów: " && wc -l $naglosy
echo "Liczba wygłosów: " && wc -l $wyglosy
echo 'KONIEC'
