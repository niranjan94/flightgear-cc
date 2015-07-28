from distutils.core import setup
import py2exe
setup(
    options = {'py2exe': {'bundle_files': 1}},
    zipfile = None,
    console = [{
            "script":"interface.py",
            "icon_resources": [(1, "FlightGearCC.ico")],
            "dest_base":"FlightGearCC"
            }],
)