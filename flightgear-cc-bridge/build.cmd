rmdir /Q /S dist
python setup.py py2exe
mkdir dist\ui
xcopy G:\web\flightgear-cc-interface dist\ui /s /h
cp extras\splash.png dist
cp extras\README.txt dist
cp extras\favicon.ico dist\ui
rmdir /Q /S dist\ui\.idea
rmdir /Q /S build
cd dist
"C:\Program Files\7-Zip\7za.exe" a -mx9 -tzip FlightGearCC_v.zip *.* -r