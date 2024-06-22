"""
freecad/tinyAsmWB/tAcmd/taModSheetFunctions.py

(c) Wolfgang Rosner 2024 - wolfagngr@github.com
License: LGPL 2+

find sheet functions in modules bundled with tiny Animator Workbench
"""


from pprint import pp
import sys
import re

# prepacked mod are evaluated only at load time, not subject to reimport
from freecad.tinyAsmWB.sheetExt import *
MODPATH = 'freecad.tinyAsmWB.sheetExt'


def getTAmodlist(modpath = MODPATH):
    """ list of paths of modules defined in and imported from MODPATH"""
    tAmodlist = ([ key
        for key, value in sys.modules.items()
            if re.match(r"^freecad.tinyAsmWB.sheetExt.", key)  ])

    return tAmodlist



def getTAfunclist(modpath = MODPATH):

    ml = getTAmodlist(modpath)

    fl = {}
    for value in ml:

        mod = sys.modules.get(value)

        if mod:
            # filter out '__dunders__' to get function candidates
            for fcname, fcval in mod.__dict__.items():
                if  re.match(r"^__[\w]+__$", fcname):
                    continue

                if callable(fcval):
                    fl[fcname] = fcval

    return fl


# pp([ (key, value.__module__) for key, value in obj.Proxy.spEvalidator.funclist.items() ])
def debugTAfunclist(modpath = MODPATH):
    fl = getTAfunclist(modpath)
    func2mod = [ (key, value.__module__) for key, value in fl.items() ]
    pp(func2mod)



