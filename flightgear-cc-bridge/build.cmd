rmdir /Q /S dist
python setup.py py2exe
mkdir dist\ui
xcopy G:\web\flightgear-cc-interface dist\ui /s /h
cp splash.png dist
cp README.txt dist
rmdir /Q /S dist\ui\.idea
rmdir /Q /S build
