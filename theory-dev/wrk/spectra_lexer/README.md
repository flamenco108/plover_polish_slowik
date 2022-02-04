# Teoria Słowik dla Spectra Lexer

Żeby móc iterować teorię, chcemy ją zapisać w sposób zrozumiały dla skryptów i potem automagicznie wygenerować większość słownika. Zamiast opracowywać nowy format, tu będą dane kompatybilne z wtyczką [Spectra Lexer](https://github.com/fourshade/spectra_lexer). Format reguł ma [formalny opis](https://github.com/fourshade/spectra_lexer/blob/master/doc/rules_format.txt).

Na potrzeby tego zastosowania, jest wprowadzone kilka zmian od oryginalnego formatu. Reguły mogą mieć puste pole `keys`, co oznacza że mają mieć wszystkie klawisze reguł które są wymienione w polu `letters`.

Wpisy w słowniku są generowane przez przetwarzanie listy słów zgodnie ze zdefiniowanymi zasadami. Jeśli jakiś wpis ma być włączony bezpośrednio do słownika musi mieć flagę `DICT`. Zasady służące do przypisywania klawiszy sylabom mają mieć jedną z flag opisujących ich położenie w sylabie: `ONSET`, `NUCLEUS`, `CODA`.

Pisząc szablon, dbaj o to aby poszczególne pola we wpisach z pewnej grupy zasad, były w tych samych kolumnach tekstu. To znacznie upraszcza ręczną edycję wielu wpisów jednocześnie.

## Uruchamianie

Żeby używać Spectra Lexer w normalnym oknie Plover z tymi zasadami trzeba wygenerować polski indeks i ręcznie go załadować do wtyczki. Na razie szybciej jest uruchamiać ją samodzielnie (opcje z `http` są dlatego że zdarzają się problemy z Qt w tym trybie).

```
python3 generuj_slownik.py && \
spectra_lexer index --keymap=assets/key_layout.cson --rules=wyniki/rules.cson --board-defs=assets/board_defs.cson --translations=wyniki/spektralny-slowik.json --index=wyniki/index.json && \
spectra_lexer http --http-port=8888 --keymap=assets/key_layout.cson --rules=wyniki/rules.cson --board-defs=assets/board_defs.cson --translations=wyniki/spektralny-slowik.json --index=wyniki/index.json
```
