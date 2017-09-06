rmdir /Q /S dist
python setup.py py2exe
mkdir dist\ui
xcopy C:\flightgear-cc\flightgear-cc-interface dist\ui /s /h
xcopy extras\splash.png dist
xcopy extras\README.txt dist
xcopy extras\favicon.ico dist\ui
rem rmdir /Q /S dist\ui\.idea
rmdir /Q /S build
cd dist
"C:\Program Files\7-Zip\7z.exe" a -mx9 -tzip FlightGearCC_v.zip *.* -r