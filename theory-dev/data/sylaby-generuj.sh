#!/bin/bash

if [[ $# -eq 0 ]] ; then
  echo "Generowanie sylab z pliku słownika, w którym wyrazy zostały"
  echo "już podzielone"
  echo "Usage: $0 sciezka/do/pliku sciezka/do/zmienionego_pliku"
  echo ""
  exit 0
fi

echo $1
if [[ $# -lt 1 ]] ; then
  echo "Podaj plik do przerobki (sciezka/plik)!!!"
  exit 0
else
  INFILE=$1
fi


#plik przetworzony
echo $2
if [[ $# -lt 2 ]] ; then
  echo "Podaj wynikowy plik (sciezka/plik)"
  exit 0
else
  OUTFILE=$2
fi




sed -e 's/^.* //' $INFILE > allsyll1.txt
sed -e 's/=/\n/g' allsyll1.txt > allsyll2.txt
sort allsyll2.txt > allsyll3.txt
uniq allsyll3.txt > allsyll4.txt
uniq -c allsyll3.txt > allsyll4c.txt 
wc -l allsyll4.txt
cat allsyll4.txt > $OUTFILE
rm allsyll*
