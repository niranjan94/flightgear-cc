rmdir /Q /S dist
rmdir /Q /S build
python setup.py py2exe
mkdir dist\ui
xcopy G:\web\flightgear-cc-interface dist\ui /s /h
cp README.txt dist
rmdir /Q /S dist\ui\.idea
rmdir /Q /S build
