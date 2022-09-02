echo Usuwam słowniki z C:\Users\flamenco\AppData\Local\plover\plover
del "C:\Users\flamenco\AppData\Local\plover\plover\slowik*" /s /f /q
echo Słowniki usunięte!
echo Ładuję plugin D:\Flamenco\Git\plover_polish_slowik
"C:\Program Files\Open Steno Project\Plover 4.0.0.dev12\plover_console.exe" -s plover_plugins install "D:\Flamenco\Git\plover_polish_slowik"
echo Plugin załadowany!