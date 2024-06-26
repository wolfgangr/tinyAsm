"""FreeCADGui init script of tinyAsm module"""
# ***************************************************************************
# *    Copyright (c) 2024 Wolfgang Rosner wolfgangr@github.com              *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENSE text file.                                 *
# *                                                                         *
# *   FreeCAD is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Lesser General Public License for more details.                   *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with FreeCAD; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************/

try:
    import FreeCADGui
    # Gui = FreeCADGui
    import FreeCAD
except ImportError:
    print("module not loaded with freecad")

# import FreeCAD
# import FreeCADGui
import sys
import os

# source of extern commands to be used in buttons and menue
import PartGui
import SpreadsheetGui
import SketcherGui

# our own WB ecosystem
from freecad.tinyAsmWB import commands
import freecad.tinyAsmWB as tinyAsmWB
from   freecad.tinyAsmWB import ICON_PATH

class tinyAsm (FreeCADGui.Workbench):

    MenuText = "tiny Asm"
    ToolTip = "minimalistic datum based Assembly toolbox"
    Icon = os.path.join(ICON_PATH , 'tinyAsmWB.svg')

    def Initialize(self):
        """This function is executed when the workbench is first activated.
        It is executed once in a FreeCAD session followed by the Activated function.
        """



        mycommands = commands.mycommands

        collectedtoolbarcommands = commands.cmdList

        parttoolbarcommands = [
            # "Part_CheckGeometry",
            'Part_EditAttachment',
            "Part_Primitives",
            # "Part_Builder",
            # "Part_Cut",
            # "Part_Fuse",
            # "Part_Common",
            "Part_Extrude",
            # "Part_Revolve",
        ]
        collectedtoolbarcommands.extend(parttoolbarcommands)

        othercmds = [
            # "Spreadsheet_CreateSheet",
            'Sketcher_NewSketch',
            'Sketcher_ReorientSketch',
            "Spreadsheet_CreateSheet",
        ]
        collectedtoolbarcommands.extend(othercmds)


        self.appendToolbar("tinyAssembly", mycommands)
        self.appendToolbar("common Commands", collectedtoolbarcommands)
        # self.appendToolbar("common Commands", parttoolbarcommands)

        # self.appendMenu("My New Menu", self.list) # creates a new menu
        self.appendMenu("tinyAssembly", mycommands)
        self.appendMenu("commonCmds", collectedtoolbarcommands)
        # self.appendMenu("commonCmds", parttoolbarcommands)

        # self.appendMenu(["An existing Menu", "My submenu"], self.list) # appends a submenu to an existing menu

    def Activated(self):
        """This function is executed whenever the workbench is activated"""
        return

    def Deactivated(self):
        """This function is executed whenever the workbench is deactivated"""
        return

    def ContextMenu(self, recipient):
        """This function is executed whenever the user right-clicks on screen"""
        # "recipient" will be either "view" or "tree"
        self.appendContextMenu("My commands", self.list) # add commands to the context menu

    def GetClassName(self):
        # This function is mandatory if this is a full Python workbench
        # This is not a template, the returned string should be exactly "Gui::PythonWorkbench"
        return "Gui::PythonWorkbench"

# try:    # for development: readd WB in running FC
#     FreeCADGui.removeWorkbench('tinyAsm')
# except:
#     print("DEBUG ### cannot remove Workbench 'tinyAsm' ")

FreeCADGui.addWorkbench(tinyAsm)
print("tinyAsmWB initialized GUI")
