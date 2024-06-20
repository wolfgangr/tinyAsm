## tinyAsm Workbench for FreeCAD

# Disclaimer - !!DO NOT USE!! - premature work in progress

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

*cope with FreeCAD startes frustration from toponaming, quagmire of support and assembly development
*it's a poor craftsman who blames his tools
*https://wiki.freecad.org/Topological_naming_problem
Use of supporting datum objects like planes and local coordinate systems is strongly recommended to produce models that aren't easily subject to such topological errors.

#### Topological Naming Problem - Avoid it or Attack it?

Primordial reptile behavioral patterns obviously applies to the attitude towards the topolocigal naming problem (aka TNP):

Very motivated developers and experienced users feel comfortable with the idea to attack TNP.
As of writing (Summer 2024), TNP is major development target.
Assembly3 - trying to conquer TNP - is in the focus, but obviously not yet mature in 0.21.2.
Assembly4 - trying to avoid TNP and leaving control to the user instead of handing it over to some opaque solving machine - is cut off from mainstream development from the moment.
Assembly2+ is labeled as deprecated.

The unexperienced or casual user is left behind.
The Workbench at hand grew from such an experience:

* get lured into nice looking features
* loosing work by collapsing models due to TNP, flipping sketches and compatibility issues
* documentation quagmire
* learn to accept that FreeCAD is not a toughly maintained business project, but a vivid ecosystem
* it's FOSS, after all
* learn to use what is there and make the best out of it
* learn to control featues, dimensions and placement by datum objects and calculation
* grahical attachment is nice, fast, intuitive but risky, so use it wisely
* Links are a great tool for reusable parts
* ... but they spoil the access of their real global placement from the realm of FreeCAD Expression engine
* effective global placement of linked objects is readily available from Python scripting, however

It were desirable to combine the lofty easiness of graphical attachment with the srict control of calculated datum items.
Its always easy to switch from calculated datums to graphical attachment e.g. for "decorative" details.
However, as soon as links are involved, the Global Placement restriction does not allow to go back from a graphical designed chain back to calculated Expressions.

#### Simplicity
The need for this WB may dramatically dissolve as soon as there is access to Effective Global Placement from Expressions in the FreeCAD core.
So the design follows the K.I.S.S rationale: "keep it simple and stupid"

##### Placement inspection is limited to first level subObjects of linked Part Containers
There is neither support for deep level inspection not Draft Arrays or whatever other option in the "nice to have" area.
You always can put any other object into a Part container and add a LCS to whereever you want

##### Variants are left to the users Imagination
As the example for the animator shows, with the help of Spreadsheets and combined expression in Features Properties, arbitrary complexity can be produced under user control.
Development, Testing and the extra button is restricted to LCS - the instance of datum objects which fully contrains the 6 DoF of a placment.
Other datum objects (plane, line, dot) are easily derived from a LCS by simply ignoring some DoF of a LCSs placment.

## To Be Done
* the code
* documemtation
* examples
* present in Forum




