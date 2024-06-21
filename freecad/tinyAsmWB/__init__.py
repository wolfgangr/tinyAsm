"""FreeCAD init script of tinyAsm module"""
# template: https://wiki.freecad.org/Workbench_creation
#
# ***************************************************************************
# *   Copyright (c) 2024 Wolfgang Rosner wolfgangr@github.com               *
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

# FreeCAD.addImportType("My own format (*.own)", "importOwn")
# FreeCAD.addExportType("My own format (*.own)", "exportOwn")


import os
from .version import __version__
DIR = os.path.dirname(__file__)
ICON_PATH = os.path.join(DIR, "icons")


print("... loading tinyAsmWB... Dummy")
import freecad.tinyAsmWB as tinyAsmWB

import freecad.tinyAsmWB.tAcmd
from freecad.tinyAsmWB.tAcmd import *
import freecad.tinyAsmWB.sheetExt
from freecad.tinyAsmWB.sheetExt import *



