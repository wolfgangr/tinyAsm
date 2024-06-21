
# boilerplated from beam WB and Manipulator WB
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
            # "tiny_GPattach",
            # "tiny_Solver",
            # "tiny_Animator",
            # "tiny_pySheet"
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
        #     "tiny_Solver",
        #     "tiny_Animator",
        #     "tiny_pySheet"
##

# class Beam(BaseCommand):
#
#     def Activated(self):
#         interaction.make_beam(self.view)
#
#     def GetResources(self):
#         return {'Pixmap': os.path.join(ICON_PATH, 'beam.svg'), 'MenuText': 'Beam', 'ToolTip': 'Create a beam'}
#
#
# class CutMiter(BaseCommand):
#
#     def Activated(self):
#         interaction.make_miter_cut(self.view)
#
#     def GetResources(self):
#         return {'Pixmap': os.path.join(ICON_PATH, 'beam_miter_cut.svg'), 'MenuText': 'Miter Cut', 'ToolTip': 'Perform miter cut of 2 beams'}
#
#
# class CutPlane(BaseCommand):
#
#     def Activated(self):
#         interaction.make_plane_cut(self.view)
#
#     def GetResources(self):
#         return {'Pixmap': os.path.join(ICON_PATH, 'beam_plane_cut.svg'), 'MenuText': 'Plane Cut', 'ToolTip': 'Cut a beam by a face of another beam'}
#
#
# class CutShape(BaseCommand):
#
#     def Activated(self):
#         interaction.make_shape_cut(self.view)
#
#     def GetResources(self):
#         return {'Pixmap': os.path.join(ICON_PATH, 'beam_shape_cut.svg'), 'MenuText': 'Shape Cut', 'ToolTip': 'Cut a beam by outer surface of another beam'}
#
#
# class LinkedFace(BaseCommand):
#
#     def Activated(self):
#         boxtools.create_linked_face()
#
#     def GetResources(self):
#         return {'Pixmap': os.path.join(ICON_PATH, 'linked_face.svg'), 'MenuText': 'Linked Face', 'ToolTip': 'linked_face'}
#
#
# class ExtrudedFace(BaseCommand):
#
#     def Activated(self):
#         boxtools.create_extruded_face()
#
#     def GetResources(self):
#         return {'Pixmap': os.path.join(ICON_PATH, 'extruded_face.svg'), 'MenuText': 'Extruded Face', 'ToolTip': 'extruded_face'}
#
#
# class FlatFace(BaseCommand):
#
#     def Activated(self):
#         boxtools.create_flat_face()
#
#     def GetResources(self):
#         return {'Pixmap': os.path.join(ICON_PATH, 'linked_face.svg'), 'MenuText': 'Flat Face', 'ToolTip': 'flat_face'}
#
# class ScrewMaker(BaseCommand):
#
#     def Activated(self):
#         a = App.ActiveDocument.addObject("Part::FeaturePython", "screw")
#         screw_maker.Screw(a)
#         screw_maker.ViewproviderScrew(a.ViewObject)
#
#     def GetResources(self):
#         return {'Pixmap': os.path.join(ICON_PATH, 'screw.svg'), 'MenuText': 'create Screw', 'ToolTip': 'create Screw'}
#
#
#
# class NurbsConnection(BaseCommand):
#
#     def Activated(self):
#         bspline_tools.make_nurbs_connection()
#
#     def GetResources(self):
#         return {'Pixmap': os.path.join(ICON_PATH, 'nurbs_connect.svg'), 'MenuText': 'NURBS Connect', 'ToolTip': 'nurbs_connect'}
#
#
# class FemSolver(BaseCommand):
#
#     def Activated(self):
#         sel = Gui.Selection.getSelection()
#         fem2d.make_GenericSolver(sel[0], sel[1])
#         App.ActiveDocument.recompute()
#
#     def GetResources(self):
#         return {'Pixmap': os.path.join(ICON_PATH, "generic_solver.svg"), 'MenuText': 'FEM Solver', 'ToolTip': 'fem_solver'}
#
#
# class Reload():
#     NOT_RELOAD = ["freecad.frametools.init_gui"]
#     RELOAD = ["freecad.frametools"]
#     def GetResources(self):
#         return {'Pixmap': os.path.join(ICON_PATH, 'reload.svg'), 'MenuText': 'Refresh', 'ToolTip': 'Refresh'}
#
#     def IsActive(self):
#         return True
#
#     def Activated(self):
#         try:
#             from importlib import reload
#         except ImportError:
#             pass # this is python2
#         import sys
#         for name, mod in sys.modules.copy().items():
#             for rld in self.RELOAD:
#                 if rld in name:
#                     if mod and name not in self.NOT_RELOAD:
#                         print('reload {}'.format(name))
#                         reload(mod)
#         from pivy import coin
