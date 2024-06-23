# The ideas behind tiny Assembler
## Development rationale
## "To Solve" or "Not To Solve"
## Typical Workflow Patterns
# Features provided by tinyAsm
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
GPattach is a FPO-Link to a Part-Container (aka "Child" - to be attached). It takes a reference to another Part Container (aka "Parent" - may be a Link, too). It scans both for their first level subobjects and maintains a enum Properties, where the user can select which subojects's Placement shall be used as attachment anchors.

GPattach own placment is calculated as the sequence of
* Placement of selected anchor-sub-Object in the Parent
* an offset Placement (defaults to all zeros, i.e. both anchors match)
* inverse of selected anchor-sub-Object in the Child

`GPattach` is inspired by the Attacher in Assembly4 and tries to resemble its functionality.

## Spreadsheet extendable functions by users
### packed extensions with tiny Assembler
#### global placement retriever
#### triangle solver
### writing own spreadsheet extension in Python
## Reverse Kinematic Solver
## Tiny Animator
# Common Functions aliased in Menue and Toolbar
