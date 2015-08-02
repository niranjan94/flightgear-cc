from distutils.core import setup
import py2exe

setup(
    options={
        'py2exe': {
            'bundle_files': 1,
            'compressed': True,
            'optimize': 2,
            'dll_excludes': ['w9xpopen.exe', 'msvcr71.dll'],
            'excludes': ['_ssl', 'doctest', 'pdb', 'unittest', 'difflib', 'inspect', 'calendar', 'tarfile', 'zipfile', 'optparse', 'xmllib', 'ftplib'],
        }},
    zipfile=None,
    console=[{
        "script": "interface.py",
        "icon_resources": [(1, "FlightGearCC.ico")],
        "dest_base": "FlightGearCC",
        'uac_info': "requireAdministrator",
    }],
)