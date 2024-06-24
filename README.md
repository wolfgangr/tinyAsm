## tinyAsm Workbench for FreeCAD

# Disclaimer - premature work in progress
Do not use for any serious project!  
Current development state per June 2024 is somewhere at late alpha:  
- Code as planned is roughly completed  
- Basic functionality is checked

However, expect errors, data loss and corruption of data and system.\
Of course, bold testers are invited to test and report feedback :-)  


### Documentation
growing here:
[Documentation](./doc/README.md)

Next step:  
test the workbench against some basic [Examples](./examples) and document the results


### Components

#### Own FeaturePython Objects:
* GPinspector: can be attached to some Object to unveil its Effective Global Placement (EGP) to a Property, readable from FreeCAD expressions
* GPpart: a linkable Container which automagically maintains GPinspectors for its subObjects (typically LCS, others may work, too)
* GPattach: an attachment helper, inspired by Assembly4, which allows to assembly one Part to another by joing a specified subobject (typically a LCS) with some optional offset
* tiny Solver: wrapper for numpy solver for the inverse kinematic solution for a chain of features, defined in a FreeCAD document
* tiny Aninmator: simple FeaturePythonObject (FPO) with a property that runs from 0 ... 1 in configurable steps and time. Other Features, Spreadsheets, Expressions can refer to it to build animations of arbitrary complexity
* tiny pySheet: Spreadsheet with the option to add access user defined Python functions without violating the FreeCAD security concept

#### Build upon stable FreeCAD components
The idea of this is not to reinvent the wheel, but leverage the power of existing FreeCAD elements.
Some of the most required ones in typical Assembly workflows are pulled into menue and toolbar to avoid the need for repeated workbench switching
* standard Spreadsheet
* Local coordinate system (without PartDesign overhead )
* Sketch
* Part Extrude
* Part Primitves
* Part Attachment
Std_Part Containers and Std_Link are available independent of selected workbench, so there is no need for extra buttons.

### Inspiration and Rationale
see [doc/tAconcept.md](./doc/tAconcept.md)


## To Be Done
* [90%] the code
* [10%] documentation
* [10%] examples
* [10%] present in Forum




