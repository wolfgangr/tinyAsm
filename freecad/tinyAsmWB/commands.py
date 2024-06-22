"""
freecad/tinyAsmWB/commands.py

(c) Wolfgang Rosner 2024 - wolfagngr@github.com
License: LGPL 2+

boilerplated from beam WB and Manipulator WB

"""

import os

import FreeCADGui #  as Gui
import FreeCAD    #  as App

# Part....
import AttachmentEditor

import freecad.tinyAsmWB
from freecad.tinyAsmWB import ICON_PATH
from freecad.tinyAsmWB.tAcmd import *
from freecad.tinyAsmWB.sheetExt import *

# from . import interaction, boxtools, bspline_tools
# from . import fem2d
# from . import screw_maker
#
#
# __all__ = [
#     "Beam",
#     "CutMiter",
#     "CutPlane",
#     "CutShape"]

cmdList = [
        'bareLCS',
        # 'CreateCommonSheet',
        # "taPart_EditAttachment",
            # # "Part_CheckGeometry",
            # # "Part_Builder",
            # # "Part_Cut",
            # # "Part_Fuse",
            # # "Part_Common",
            # "Sketcher_NewSketch",
            # "Part_Extrude",
            # "Part_Primitives",
            # # "Part_Revolve",
            # "Part_EditAttachment",


    ]

mycommands = [
            "taGPInspector",
            "taGPpart",
            "taGPattach",
            "taPySheet",
            "taAnimator",
            # "tiny_pySheet"
            # "tiny_Solver",
            # "tiny_Animator",

        ]

class BaseCommand(object):

    def __init__(self):
        pass

    def GetResources(self):
        return {'Pixmap': '.svg', 'MenuText': 'Text', 'ToolTip': 'Text'}

    def IsActive(self):
        if FreeCAD.ActiveDocument is None:
            return False
        else:
            return True

    def Activated(self):
        pass

    @property
    def view(self):
        return FreeCADGui.ActiveDocument.ActiveView

##
class DatumLCS(BaseCommand):

    def GetResources(self):
        return {'Pixmap'  : os.path.join(ICON_PATH , 'DatumLCS.svg') ,
                     'MenuText': "Datum LCS" ,
                     'ToolTip' : "Datum LCS\nw/o PD overhead\nas in Manipulator workbench"}

    def Activated(self):
        FreeCAD.ActiveDocument.addObject('PartDesign::CoordinateSystem','LCS')

FreeCADGui.addCommand('bareLCS',DatumLCS())

##
#     "tiny_GPInspector",


gpi = freecad.tinyAsmWB.tAcmd.LinkGPlcInsp

class taGPins(BaseCommand):

    def GetResources(self):
        return {'Pixmap'  : os.path.join(ICON_PATH , 'GPinsp.svg') ,
                'MenuText': "GPLink inspector" ,
                'ToolTip' : "retrieve GlobalPlacement\nof subelements\nof a linked Part"}

    # grey out unless a single link instance is selected
    # from Part/AttachmentEditor/Commands.py
    def IsActive(self):
        sel = FreeCADGui.Selection.getSelectionEx()

        if len(sel) == 1:
            if hasattr(sel[0].Object,"Placement"):
                if hasattr(sel[0].Object, "ElementCount"):
                    self.selection = sel[0].Object
                    return True

        self.selection = None
        return False

    def Activated(self):
        # FreeCAD.ActiveDocument.addObject('PartDesign::CoordinateSystem','LCS')
        gpi.create_uGPL(obj_name = 'taGPinsp', arg_tgt = self.selection)
        # ### TBD: check for selected Part?
        pass

FreeCADGui.addCommand("taGPInspector", taGPins() )

##
#     "tiny_GPpart",

gpp = freecad.tinyAsmWB.tAcmd.Part_maintGP

class taGPpart(BaseCommand):

    def GetResources(self):
        return {'Pixmap'  : os.path.join(ICON_PATH , 'GPpart.svg') ,
                'MenuText': "GPpart " ,
                'ToolTip' : "Part container to be linked\nmaintains dependend GPinspectors"}

    def Activated(self):
        gpp.create_GPpart()
        # pass

FreeCADGui.addCommand("taGPpart", taGPpart() )


##
#     "tiny_GPattach",

gpa = freecad.tinyAsmWB.tAcmd.attachByGP

class taGPattach(BaseCommand):

    def GetResources(self):
        return {'Pixmap'  : os.path.join(ICON_PATH , 'GPattach.svg') ,
                'MenuText': "GPattach" ,
                'ToolTip' : "attach one Container to another\nby matching placement of sub-objects\nfirst selection: Child\nsecond selection: Parent"}

    # grey out unless a single link instance is selected
    # from Part/AttachmentEditor/Commands.py
    def IsActive(self):
        sel = FreeCADGui.Selection.getSelectionEx()

        if len(sel) == 2:
            # if hasattr(sel[0].Object,"Placement"):
                # if hasattr(sel[0].Object, "ElementCount"):
                    # self.selection = sel[0].Object
            return True

        # self.selection = None
        return False

    def Activated(self):
        # FreeCAD.ActiveDocument.addObject('PartDesign::CoordinateSystem','LCS')
        # gpi.create_uGPL(obj_name = 'taGPinsp', arg_tgt = self.selection)
        gpa.create_GPatt(obj_name='taGPattach')
        # ### TBD: check for selected Part?
        pass

FreeCADGui.addCommand("taGPattach", taGPattach() )

##
#     "tiny_pySheet"


gps = freecad.tinyAsmWB.tAcmd.sheetPythonCustomFunc

class taPySheet(BaseCommand):

    def GetResources(self):
        return {'Pixmap'  : os.path.join(ICON_PATH , 'PySheet.svg') ,
                'MenuText': "Extensible Spreadsheet" ,
                'ToolTip' : "Spreadsheet with user\nextensible Python fuctions"}

    def Activated(self):
        gps.create_pySheet()
        # pass

FreeCADGui.addCommand( "taPySheet", taPySheet() )

##
#     "tiny_Animator",

gpAnim = freecad.tinyAsmWB.tAcmd.tinyAnimator

class taAnimator(BaseCommand):

    def GetResources(self):
        return {'Pixmap'  : os.path.join(ICON_PATH , 'taAnimator.svg') ,
                'MenuText': "simple Animator" ,
                'ToolTip' : "FeaturePythonObject with runnable Property"}

    def Activated(self):
        gpAnim.create_tinyAnimator(obj_name = 'taAnimator')
        # pass

FreeCADGui.addCommand( "taAnimator", taAnimator() )





##
#     "tiny_Solver",
