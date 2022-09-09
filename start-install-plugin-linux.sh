#!/bin/bash


echo "Usuwam słowniki z ~/.config/plover/"
rm -rf ~/.config/plover/slowik* && echo "Słowniki usunięte" && \
~/bin/Plover/plover-4.0.0.dev12-x86_64.AppImage -s plover_plugins install ~/git/plover_polish_slowik/
