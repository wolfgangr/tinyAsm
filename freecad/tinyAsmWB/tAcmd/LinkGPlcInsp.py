"""
# Global Link Inspector
# upon recompute, scan all first level child objects of linked Part container
# and write their real global placment list to a Parameter so it can be read
# from FreeCAD expressions

(c) Wolfgang Rosner 2024 - wolfagngr@github.com
License: LGPL 2+

# boilerplated from
# https://wiki.freecad.org/Create_a_FeaturePython_object_part_I#Complete_code
"""

# ======================================
#   config
parameter_group_name = "GP" # no trailing _ !
tooltip = "retrieved Global Placement of sub-Object - read only"
max_iter = 2 # how deep shall we follow link chains
# ======================================


import FreeCAD as App

try:
    import FreeCADGui
    from pivy import coin
except ImportError:
    print("GPInspector running in GUI-less mode")

import os
import re
import datetime

from freecad.tinyAsmWB import ICON_PATH

##


def traverse_link_chain(lnk):
    """ follow link chain until we find an object with a Group property """

    cnt_iter = max_iter
    frontier = lnk

    while True:
        if hasattr(frontier, 'Group'):
            return frontier
            # --- normal step out here
        #  looks like even link chains supply a "Group" attribute
        #  even if its not displayed in pyzo workspace
        #  so we could have saved the effort here??

        if hasattr(frontier, 'LinkedObject'):
            frontier = frontier.LinkedObject
        else:
            raise ValueError('Link chain does not end in Group object')

        cnt_iter =  cnt_iter -1
        if cnt_iter < 1:
            raise ValueError("Link chain limit exceeded")


def sync_GPParams(obj_svtr, obj_svnd, pgname = parameter_group_name):
    """ param List is kept as property of surveilling object """

    old_PL = obj_svtr.inspectedSubobjectList

    # .. and has to match subobject List of object under surveillance
    eoLinkChain = traverse_link_chain (obj_svnd)
    new_PL =  [ itm.Name + '.'  for itm in eoLinkChain.Group ]   # list(obj_svnd.getSubObjects())
    new_PL.insert(0, '')
    # new_PL.insert(1, '.')
    if hasattr(eoLinkChain, 'Origin'):    # (obj_svnd, 'Origin'):
        new_PL.insert(1, 'Origin.')

    # print ('old_PL', old_PL)
    # print ('new_PL', new_PL)

    prm2prop = {} # keep a dictionary of subobj name -> proeprty name
    # add missing params
    for prm in new_PL:
        pg_prm = pgname + '_' + prm.rstrip('.')
        prm2prop[prm] = pg_prm
        if not (prm in old_PL):
            # print('create param: ' + pg_prm)
            obj_svtr.addProperty("App::PropertyPlacementList", pg_prm, pgname, tooltip)
            obj_svtr.setEditorMode(pg_prm, ['ReadOnly'])

    # remove stale params
    for prm in old_PL:
        pg_prm = pgname + '_' + prm.rstrip('.')
        if not (prm in new_PL):
            # print('delete param: ' + pg_prm)
            obj_svtr.removeProperty(pg_prm)

    obj_svtr.inspectedSubobjectList = new_PL
    return prm2prop


def create_uGPL(obj_name = 'GPLinkInspector', arg_tgt = None):
    """
    Object creation method
    target priority:
    - "arg_tgt" call argument
    - first obj in GUI selection
    - default: None - to be assigned later
    """

    obj = App.ActiveDocument.addObject('App::FeaturePython', obj_name)
    GPLinkInspector(obj)

    if arg_tgt:
        obj.inspectedObject = arg_tgt
    else:
        try:
            target = FreeCADGui.Selection.getSelection()[0]
            obj.inspectedObject = target
            # print(f"attached to surveillance of object: <{target.Name}>")
        except Exception as exc:
            print (exc)
            print('no valid object selected, leave empty')
            pass

    # throws recursive recompute warning
    # App.ActiveDocument.recompute()
    return obj

##

class taGPiViewProvider:
    ''' basic defs to get a custom icon in tree view'''

    def __init__(self, obj):
        obj.Proxy = self
        # self.Object = obj

    def getIcon(self):
        return os.path.join(ICON_PATH , 'GPinsp.svg')

    def attach(self, vobj):
        self.standard = coin.SoGroup()
        vobj.addDisplayMode(self.standard,"Standard");

    def getDisplayModes(self,obj):
        """Return a list of display modes."""
        return ["Standard"]

    def getDefaultDisplayMode(self):
        """Return the name of the default display mode. It must be defined in getDisplayModes."""
        return "Standard"

##

class GPLinkInspector():
    def __init__(self, obj):
        """
        Default constructor
        """
        self.Type = 'GPLinkInspector'
        obj.Proxy = self
        taGPiViewProvider(obj.ViewObject)

        # obj.addProperty('App::PropertyString', 'Description', 'Base', 'Box description')
        obj.addProperty("App::PropertyLink", "inspectedObject", "Base",
            'The object whose subobjects real global placment values shall be retrieved')
        obj.addProperty("App::PropertyStringList", "inspectedSubobjectList", "Base",
            'List of subObjects under surveillance - autogenerated')
        obj.setEditorMode('inspectedSubobjectList', ['ReadOnly'])


    def onDocumentRestored(self, obj):
        """
        to avoid loss of proxy on restoring saved document
        see https://wiki.freecad.org/FeaturePython_methods
        """
        obj.Proxy = self


    def execute(self, obj):
        """
        on object recompute, rebuild surveillance structure
        """
        # print('Recomputing {0:s} ({1:s})'.format(obj.Name, self.Type))
        #
        surveilland = obj.inspectedObject
        if not surveilland:
            print('no object for inspection selected')
            obj.Label=obj.Name
        else:
            if surveilland.ElementCount == 0 :
                # print('  -- singleton Link: ',  surveilland.Name, ' --')
                eff_elems = 1
                idx_elems = ['']
            # elif len(surveilland.ElementList) == 0 :
            #     print('  -- hidden elem Link Array: ',  surveilland.Name, ' --')
            else:
                # print('  -- Link Array: ',  surveilland.Name, ' --')
                eff_elems = surveilland.ElementCount
                idx_elems = [f"{i}." for i in range(eff_elems)]
            obj.Label='GPinsp_' + surveilland.Label
            paramDict = sync_GPParams(obj, surveilland)
            # print ('paramDict:', paramDict)

            for so in paramDict.keys():
                pg_prm = paramDict[so]
                plcList =[]
                for lelem in idx_elems:
                    path = lelem + so
                    plc = surveilland.getSubObject(path, retType = 3)
                    plcList.append(plc)

                # print ("checker: so, idx_elems, plcList:", so, idx_elems, "\n", plcList)
                try:
                    setattr(obj, pg_prm, plcList)
                except:
                    print ( 'failed ot attach placement list')
                    pass


