"""restricted eval implementation for spreadsheet user defined functions

(c) Wolfgang Rosner 2024 - wolfagngr@github.com
License: LGPL 2+

# https://github.com/wolfgangr/myTinyAsm/blob/master/spEvalidate.py
#
# inspired by evalidate, but finally implemented without
#   see https://github.com/yaroslaff/evalidate


Security considerations:
- implement FreeCAD Policy 'separate Code from Data'
- targets security level as of existing FreeCAD macros
- code for user defined functions is stored as whatever.py modules in the FreeCAD Macro tree
- SheetPython-objects contains configuration and parameter bindings only
  stored in objects Property variables
  ### TBD: documentation
- parameters are sanitized in the caller, allowing only
  - strings, passed in verbatim w/o any 'eval'
  - FreeCAD Expressions, parsed by obj.evalExpression
  - bare Python literals, parsed by ast.literal_eval
- function names are parsed here
  - containing only alphanumericals and _
  - defined in a defined subset of the FreeCAD Macro directory
  - matching a user defined list
- the caller interface 'sPeval' only implements
  function(arg1 , .... argn) syntax
  thus mimicing the limited 'node' of evalidate
  and blocking malicious code injection from Data space (FCStd) to Code space

There is no 'sandbox type' restriction of what the code living in the Macro Directory can do,
as this is open in all over FreeCAD anyway.

"""


import importlib
import re
import sys
from pprint import pformat

# gets packaged function with tiny Assembly WB mod as default:
import freecad.tinyAsmWB.tAcmd.taModSheetFunctions as taModSheetFunctions

def _ppFunclist(fl):
    """ pretty print function list
        key : __module__
    """
    func2mod = [ (key, value.__module__) for key, value in fl.items() ]
    return pformat(func2mod)

class sheetPyCEvalidator:
    """ implement evalidate and associated model for sheetPythonCustom """
    def __init__(self, sheet=None,
            prefix='', modules='', functions='', reimport=''):

        self.sheet = sheet
        self.prefix      = prefix       # getattr(obj, dirs)
        self.modules     = modules      # getattr(obj, files)
        self.functions   = functions    #(obj, functions)
        self.reimport    = reimport     # the property name

        self.ready = False

        self.taFunclist = taModSheetFunctions.getTAfunclist()
        self.modlist  = {}
        self.funclist = {}
        self.accsFlist = {}

    #

    def pp_taFunclist():
        return _ppFunclist(self.taFunclist)

    def pp_funclist():
        return _ppFunclist(self.funclist)

    def pp_accsFlist():
        return _ppFunclist(self.accsFlist)

##
    def sPeval(self, funcnam, *params) :
        """ caller interface to substitute open 'eval' """

        self.make_ready() # ensure that our machinery is up to date

        func_ptr = self.accsFlist.get(funcnam)
        if func_ptr:
            rv = func_ptr(*params)
            return rv
        else:
            return None

  ##
    def _update_modList(self):
        """ parse, sanitize and aggregate user module selection in subset of Macro Path """

        ml = {}

        pref = getattr(self.sheet, self.prefix, '')
        if pref:
            if not re.match(r"^([\w_]+)(\.[\w_]+)*$", pref):
                raise ValueError(f"module prefix <{pref}> does not match foo.bar.pattern")
        else:
            pref= ''

        mods = getattr(self.sheet, self.modules, [])
        for m in mods:
            if not re.match(r"^([\w_]+)(\.[\w_]+)*$", m):
                print(f"module name <{m}> does not match foo.bar.pattern - ignored")
            else:
                ml[m]= (pref + '.' + m) if pref else m

        if (not ml) and pref:  # i.e. no valid modules defined
            ml[pref] = pref

        if ml:
            self.modlist = ml

    def _update_funcList(self):
        """ import user defined modules and get available functions """

        fl = self.taFunclist.copy()  # otherwise dict gets changed
        for key, value in self.modlist.items():

            mod = sys.modules.get(value)

            if mod:                     # already imported
                importlib.reload(mod)

            else:                       #  if still unknown
                try:
                    mod = importlib.import_module(value)
                except:
                    print(f"failed to:  import {value} as {key} ")

            if mod:
                # filter out '__dunders__' to get function candidates
                for fcname, fcval in mod.__dict__.items():
                    if  re.match(r"^__[\w]+__$", fcname):
                        continue

                    if callable(fcval):
                        fl[fcname] = fcval
        if fl:
                self.funclist = fl


    def accessibleFunctions(self):
        """ filter all functions in funclist() by user selection """
        return  { fname: fref
                    for (fname, fref) in self.funclist.items()
                    if fname in self.sheet.cpy_cfg_functions
                }

    ## manage update workflow

    def touched(self):
        self._set_reimport(False)

    def _set_reimport(self, bl = False):
        setattr(self.sheet, self.reimport, bl)

    def _get_reimport(self):
        return bool( getattr(self.sheet, self.reimport, False))

    def update_accesibleFuncs(self):
        self.accsFlist = self.accessibleFunctions()

    def _update(self):
        # if not self.ready:
        self._update_modList()
        self._update_funcList()
        self.update_accesibleFuncs()
        self.ready = True

    def make_ready(self):
        if self.ready:
            return True
        self._update()
        if self.ready:
            return True
        else:
            raise RuntimeError("update failed")













