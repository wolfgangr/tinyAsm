# (c) Wolfgang Rosner 2024 - wolfagngr@github.com
# License: LGPL 2+
#
# boilerplated from
# https://wiki.freecad.org/Create_a_FeaturePython_object_part_I#Complete_code
# https://wiki.freecad.org/Scripted_objects_with_attachment

import FreeCAD as App
# import os
import re
import datetime
import Spreadsheet

# https://docs.python.org/3.8/library/ast.html#ast.literal_eval
# Safely evaluate an expression node or a string containing a Python literal or container display.
from ast import literal_eval

# my own sanitized function eval
import dev.myTinyAsm.spEvalidate as spEvalidate

import xml.sax

CONST_MYBang = "'#!"

CONST_prefix     ="cpy_"
CONST_DEF_prefix ="cpy_def"
CONST_RES_prefix ="cpy_res"
CONST_CFG_prefix ="cpy_cfg"

from dev.myTinyAsm.sheetPyMods_base import *
from dev.myTinyAsm.trianglesolver import solve


# check if propObj is 'cells' and if so, dump XML
# otherwise return False
#
# def debug_cells(obj, prop):
#
#     if prop != 'cells':
#         return False
#
#     propObj = getattr(obj, 'cells')
#     #
#     # if not hasattr(propObj, 'TypeId'):
#     #     return False
#     #
#     # if not (str(propObj.TypeId) == 'Spreadsheet::PropertySheet'):
#     #     return False
#     print (propObj.Content)
#     return True # propObj.Content

# required if we overload execute()
def recompute_cells(obj):
    u_range = obj.getUsedRange()
    range_str = u_range[0] + ':' + u_range[1]
    if range_str != '@0:@0':       # if sheet is not empty
        obj.recomputeCells(range_str)

# evaluate parameters from def-List
def eval_param(obj, param: str):
    # remove leading / trailing  spaces
    ps = param.strip()

    # is it a string?
    match = re.search(r"^\'(.*)\'$", ps )
    if match:
        # forward all with quote encapsulation
        # return ('"' + match.group(1) + '"')
        return str( match.group(1) )

    match = re.search(r"^\"(.*)\"$", ps )
    if match:
        # return ('"' + match.group(1) + '"')
        return str( match.group(1) )

    # '=...' try  FreeCAD Expression;  even matches ...
    #   <<strings>>, cell and object references,  numbers and arithmetic expressions
    match = re.search(r"=(.*)", ps )
    if match:
        try:
            evld = obj.evalExpression( match.group(1) )
            return evld
        except:
            return None

    # try secure ast.literal_eval for python literals
    try:
        return literal_eval(ps)


    except:
        return None

def calc_list_eval(obj, p_list: list[str]):
    if not p_list:
        return None

    funcnam = p_list[0].strip()
    params = [ eval_param(obj, p) for p in p_list[1:] ]
    # print (f"calling {funcnam} with: ", str(params))

    # sanitized evalutaion of funcnam
    rv = obj.Proxy.spEvalidator.sPeval(funcnam, *params)
    # print(rv)
    return rv


## perform calculation
def perform_calculation(obj):
    for prop in obj.PropertiesList:
        match = re.search(f'^{CONST_DEF_prefix}_(.*)', prop)
        if match:
            varname = match.group(1)
            # print (f"matched: {prop} -> {varname}")
            deflist = obj.getPropertyByName(prop)
            prop_res = f"{CONST_RES_prefix}_{varname}"
            result = calc_list_eval(obj, deflist)
            # print (f"to update Property Field {prop_res} with {result} of type {type(result)} ")
            try:
                setattr(obj, prop_res, result)

            except:
                # print (f"cannot set {prop_res} - maybe still initializing...")
                pass # silently ignore, not our business here

            obj.touch()
##


def update_res_fields(obj):
    # cycle over function definitions properties
    for prop in obj.PropertiesList:
        match = re.search(f'^{CONST_DEF_prefix}_(.*)', prop)
        if match:
            varname = match.group(1)
            # print (f"matched: {prop} -> {varname}")
            deflist = obj.getPropertyByName(prop)
            if deflist.__class__ is not list:
                raise TypeError(f"prop must be of Type 'App::PropertyStringList' ")
            # find or create matching result property
            prop_res = f"{CONST_RES_prefix}_{varname}"
            # print (f"result:     -> {prop_res}")
            if prop_res not in obj.PropertiesList:
                obj.addProperty('App::PropertyPythonObject', prop_res, CONST_RES_prefix,
                    f"result property for {prop}")
                # https://wiki.freecad.org/Property_editor#Actions
                # https://freecad.github.io/SourceDoc/d0/da9/classApp_1_1Property.html
                # ['ReadOnly', 'Transient', 'Output', 14, 21]
                obj.setPropertyStatus(prop_res, ['ReadOnly', 'Transient', 'Output', 14, 21])
                obj.touch()  # does this recurse??

            # anyway - may be our result has changed
            perform_calculation (obj)

    # remove stale result fields
    for prop in obj.PropertiesList:
        # cycle over result definitions properties
        match = re.search(f'^{CONST_RES_prefix}_(.*)', prop)
        if match:
            varname = match.group(1)
            prop_def = f"{CONST_DEF_prefix}_{varname}"
            if not prop_def in obj.PropertiesList:
                # print(f"stale result property: {prop} - no matching def: {prop_def} - going to delete")
                obj.removeProperty(prop)



# class sheetSaxHandler(xml.sax.handler.ContentHandler):
#
#     def startElement(self, name, attrs):
#         print(f"BEGIN: <{name}>, {attrs.keys()}")
#         if attrs.__contains__('address') and attrs.__contains__('content'):
#             attr = attrs.getValue('address')
#             val  = attrs.getValue('content')
#             print(f"\t{attr} -> {val}")
#             match = re.search(f"^{CONST_MYBang}(.*)", val)
#             if match:
#                 evld = match.groups()[0]
#                 print(f"\t\tTBD: eval({evld})")
#
#     def endElement(self, name):
#         print(f"END: </{name}>")
#
#     def characters(self, content):
#         if content.strip() != "":
#             print("CONTENT:", repr(content))

# class sheetSaxRecompAllCells(xml.sax.handler.ContentHandler):
#     def startElement(self, name, attrs):
#         print(f"BEGIN: <{name}>, {attrs.keys()}")
#         if name == 'Cell':
#             addr = attrs.getValue('address')
#             print(f'doing obj.recomputeCells({addr})')
#             obj.recomputeCells(addr)


# https://forum.freecad.org/viewtopic.php?p=182016#p182016
class pySheetViewProvider:
    ''' basic defs '''

    def __init__(self, obj):
        # obj.Proxy = self
        self.Object = obj

    # def __getstate__(self):
    #     return None
    #
    # def __setstate__(self, state):
    #     return None

    # maybe this is what we need in 0.21.2 instead?
    # def dumps(self):
    #     return None
    #
    # def loads(self, state):
    #     return None
    #
    # def onBeforeChange(proxy,obj,prop):
    #     print ("VP before change:", prop)
    #
    # def onChanged(proxy,obj,prop):
    #     print ("VP changed:", prop)

class pySheet():
    """
    Simple Custom Box Object
    See Also:
        https://wiki.freecadweb.org/FeaturePython_Objects
    """

    def __init__(self, obj):
        """
        Constructor
        Arguments
        ---------
        - obj: an existing document object or an object created with FreeCAD.Document.addObject('Part::FeaturePython', '{name}').
        """

        self.Type = 'pySheet'

        obj.Proxy = self

        pySheetViewProvider(obj.ViewObject)

        # obj.ViewObject.Proxy = 0  # Mandatory unless ViewProvider is coded

        obj.addProperty('App::PropertyStringList', CONST_DEF_prefix + '_dummy', CONST_DEF_prefix ,
            'template for custom python function definition')

        obj.addProperty('App::PropertyString', CONST_CFG_prefix + '_prefix', CONST_CFG_prefix ,
            'common module path from FreeCAD-Macro-Dir, in foo.bar.format ')

        obj.addProperty('App::PropertyStringList', CONST_CFG_prefix + '_modules', CONST_CFG_prefix ,
            'list of module paths from FreeCAD-Macro-Dir/foo/bar/prefix, in foo.bar.prefix format ')

        obj.addProperty('App::PropertyStringList', CONST_CFG_prefix + '_functions', CONST_CFG_prefix ,
            'names of user defined functions configured to be available')

        obj.addProperty('App::PropertyBool', CONST_CFG_prefix + '_reimport', CONST_CFG_prefix ,
            'set to true to reimport modules after code change')

        # separate instantiation for correct save/restore
        self.spEvalidator = None
        self._spE_init(obj)

    def _spE_init(self, obj):
        self.spEvalidator = spEvalidate.sheetPyCEvalidator( obj,
                CONST_CFG_prefix + '_prefix'    ,
                CONST_CFG_prefix + '_modules'   ,
                CONST_CFG_prefix + '_functions' ,
                CONST_CFG_prefix + '_reimport'    )

    # https://wiki.freecad.org/FeaturePython_methods
    def onDocumentRestored(self, obj):
        obj.Proxy = self

    # https://forum.freecad.org/viewtopic.php?p=346763&sid=d7e3d832b5e934914fcdccc5bdc100d5#p346763
    # does this help against "not json serializable" ?
    # def __getstate__(self):
    #     # return None
    #     return dumps(self)
    # #
    # def __setstate__(self, state):
    #     #     return None
    #     return loads(self, state):
    # #
    # # # maybe this is what we need in 0.21.2 instead?
    def dumps(self):
        return None
    # #
    def loads(self, state):
        # can't spEvalidator right here since we have no access to object
        self.spEvalidator = None
        return None


    def execute(self, obj):
        """
        Called on document recompute
        """
        # earliest hook after reload stored document where we have an obj
        # if not self.spEvalidator:
        if not getattr(self, 'spEvalidator', None):
            print ("in execute: spE_init(self, obj) ")
            self._spE_init(obj)

        # print('what shall I do to execute?')
        ## sync res fields
        recompute_cells(obj)
        # update_res_fields(obj)
        perform_calculation (obj)
        recompute_cells(obj)


    def onBeforeChange(proxy,obj,prop):
        # print ("before change:", prop)
        # debug_cells(obj, prop)
        # if prop == 'cells':
        #     xml.sax.parseString(obj.cells.Content, sheetSaxHandler())
        pass

    def onChanged(proxy,obj,prop):
        # print ("changed:", prop)
        # debug_cells(obj, prop)
        # if prop == 'cells':
        #     xml.sax.parseString(obj.cells.Content, sheetSaxHandler())
        # CONST_DEF_prefix
        spo = obj.Proxy # self of sheet python object is not in local namespace here

        if re.match(f"^{CONST_prefix}.*" , prop): # prefilter since we are called quite often
            match = re.match(f"^{CONST_DEF_prefix}_(.*)" , prop)
            if match:
                print ("changed:", prop)
                recompute_cells(obj)
                update_res_fields(obj)
                recompute_cells(obj)

            # CONST_CFG_prefix
            match = re.match(f"^{CONST_CFG_prefix}_(.*)" , prop)
            if match:
                print ("changed:", prop)
                m_sufx = match.group(1)

                if (m_sufx == 'prefix') or (m_sufx == 'modules'):
                    spo.spEvalidator._update_modList()
                    print ('updated modlist: ', spo.spEvalidator.modlist)

                elif (m_sufx == 'reimport'):
                    if getattr(obj, prop): # i.e. both existing and True
                        ##
                        print('reimporting modules...')
                        spo.spEvalidator._update_funcList()
                        print ('updated list of available functions: ', spo.spEvalidator.funclist)
                        setattr(obj, prop, False)
                        spo.spEvalidator.update_accesibleFuncs()
                        print ('updated list of selected functions: ', spo.spEvalidator.accsFlist)

                    obj.touch()

                elif (m_sufx == 'functions'):
                    spo.spEvalidator.update_accesibleFuncs()
                    print ('updated list of selected functions: ', spo.spEvalidator.accsFlist)

                else:
                    print (f"### TBD: ###: evaluate configuration for {m_sufx}")


def create_pySheet(obj_name='pySheet', document=None):
    """
    Create a pythonized Spreadsheet.
    """
    if not document:
        document = App.ActiveDocument

    obj = document.addObject('Spreadsheet::SheetPython', obj_name)
    pySheet(obj)
    return obj

