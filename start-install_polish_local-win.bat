echo
echo
echo
echo
echo Usuwam slowniki z C:\Users\flamenco\AppData\Local\plover\plover
echo
echo
echo
echo

del "C:\Users\flamenco\AppData\Local\plover\plover\slowik*" /s /f /q

echo
echo
echo
echo
echo S³owniki usuniete!
echo
echo
@echo off
echo. 
echo.
echo £adujê plugin D:\Flamenco\Git\plover_polish_slowik
echo.
echo.
echo.
echo.
"C:\Program Files\Open Steno Project\Plover 4.0.0.dev12\plover_console.exe" -s plover_plugins install "D:\Flamenco\Git\plover_polish_slowik"
echo.
echo.
echo.
echo.
echo Plugin zaladowany!
echo.
echo.
echo.
echo.