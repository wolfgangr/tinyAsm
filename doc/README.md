# The ideas behind tiny Assembler
## Development rationale
### History
### why minimalistic?
## "To Solve" or "Not To Solve"
## Typical Workflow Patterns
# Features provided by tinyAsm
'tinyAsm' provides a couple of own features to close gaps, left by the current (0.21.2) stable FreeCAD features:
## GPinspector - Global Placement Link inspector
`GPinspector` is a FeaturePythonObject (aka FPO) supposed to be attached to Link-Part-Containers.
Upon document recompute, it scans the linked Source-Container (Part) for it's first level sub-Objects.

It maintains a List of Properties, each labelled by a subobject's (internal) Name, containing a List of Placements for all Instances of the Link. These Placement values can easily read by FreeCAD Expressions into spreadsheets or other Features Property fields.

GPInspectors handle the transition from single Links to Link Arrays, both with subelements visible or not. For a consistent interface, for single Links the Placement is delivered as List containing one item.

## GPpart - Part Container maintainig Link inspector for all its instances
`GPpart` is a FPO-Extension of `Std_Part` containers.

It can be filled with subobjects by draw and drop. It is intended to serve as link source for assembly.

Upon recompute, it scans the DAG-Dependency-Tree for all linked instances of itself and keeps GPinspectors attached to them.

This way, FreeCAD-Expressions find a consistent point of reference to refer to the real Global Placement of all contained first-level sub-objects. 

GPpart is inspired by the Assembly4-Part

## GPattach - LCS anchored Attacher

`GPattach` attaches one Part Container or Part Link to another one by matching the placements of first level subobjects
(typically, but not exclusively, Local Coordinate Sytems aka LCS) and optionally some additional placment offset.

`GPattach` comprises an FPO-Link to a Part-Container (aka "Child" - to be attached). It takes a reference to another Part Container (aka "Parent" - may be a Link, too). It scans both for their first level subobjects and maintains enum Properties, where the user can select which subojects's Placement shall be used as attachment anchors.

`GPattach`s own placment is calculated by chaining
* Placement of selected anchor-sub-Object in the Parent
* an offset Placement (defaults to all zeros, i.e. both anchors match)
* inverse Placement of selected anchor-sub-Object in the Child

`GPattach` is inspired by the Attacher in Assembly4 and tries to resemble its functionality.

## pySheet - Spreadsheet extendable functions by users
The idea of user defined function in spreadsheets was the first approach to cope with the assembly quagmire of FreeCAD 0.21.2.
* get real global Placement of linked Objects, which is available in Python, but not in FreeCAD expressions
* perform calculations of anylytic geometry to keep control on constraints, where the Toological Naming Problem (TNP), flipping sketches and other DWIM-artefacts threaten to break models
* open a hands-on development platform for the casual user without deep FreeCAD and Python experience

Writing to spreadsheet cells and interfering with spreadsheet recalcuation from sheet-FPO aka SheetPython turned out to be a quagmire, too. So the customized functions write their result to "ordinary" Property fields of the spreadsheet object, but outside the sheet's cell matrix. This way, they don't interfere with the sheet, but nonetheless can be accessed from Expressions (both from within the sheet as well as from outside) the same way as with sheet cell aliases.

### Security considerations of extendable functions
Security considerations (see #### issue ### Link tbd) placed another constraint on the implementation of python extensions. The current implementation respects the FreeCAD security policy: Separate Code from Data. User defined functions can only reside in the `Macro` directory. Extensions shipped with tinyAsm reside in the `Mod`-tree - precisely in `.../FreeCAD/Mod/tinyAsm/freecad/tinyAsmWB/sheetExt/*`. Of course, any user is free to throw whatever code there he likes, or manipulate the source of `pySheet`. However, the same holds true for any extension of FreeCAD - as it lies at the very heart of FreeCAD architecture.

A "sandbox"-like approach might be desirable and restrict potential damage of malicious code far beyond the way currently practised in FreeCAD. However, such an endeavor is far beyond the "tiny" approach of the current implementation.

The current implementation puts narrow constraints to both functions and arguments supplied to Python evaluation. Though the concept war developped with due caution, neither a hardcore penetration test nor any independent code auditing has yet been performed. __You have been warned!__

### packed extensions with tiny Assembler
A set of prepacked extension fuctions is supplied in [.../tinyAsmWB/sheetExt](../freecad/tinyAsmWB/sheetExt).
The User may mask them for availability or override them with own functions in the `Macro` directory.

#### base extensions
... live in [.../tinyAsmWB/sheetExt/sheetPyMods_base.py](../freecad/tinyAsmWB/sheetExt/sheetPyMods_base.py).
The import statements at the top forward some system fuctions to the availability as extension functions.

Among them is `scipy.optimize.fsolve`, a generic optimizer. For the solution of reverse kinematic problems - arguably the most common case in CAD - a specialized FPO feature was developped - see below.

The others at the moment are mere test and basic "hello world"-level tools.

##### global placement retriever
... beeing the exception.

It allows arbitrary object/Link combinations to be conveyed from "Python-Realm" to "Expression-Realm".
Much of the development of tinyAsm is based on exploration with this code, and benchmarking the results against FreeCAD's builtin `GetGlobalPlacement` macro.

#### triangle solver

In addition to TNP, "flipping sketches" are a nasty side effect of giving too much freedom to "computerized intelligence".
E.g. a triangle may "flip" to it's mirror, when just 3 edge lengths are provided. One possible approach may to supply tow edges and the angle between to the sketcher instead. 

The [triangle solver](../freecad/tinyAsmWB/sheetExt/trianglesolver.py) provides a generic tool to different variations of this problem. Instructions are available in the source code and int the ### example TBD ###

### writing own spreadsheet extension in Python
see example ... ### TBD

## Reverse Kinematic Solver
## Tiny Animator
# Common Functions aliased in Menue and Toolbar
`tinyAsm` does not try to reinvent the wheel. So wherever FreeCAD builtin feature meet the requirements, they are supposed to be preferred. From Experience at the time of development, the following features are aliased in `tinyAsm` to avoid permanent switching of Workbenches. 
