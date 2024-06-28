# tinyAsm Workbench for FreeCAD

## Disclaimer - premature work in progress
Do not use for any serious project!  
Current development state per June 2024 is somewhere at late alpha:  
- Code as planned is roughly completed  
- Basic functionality is checked

However, expect errors, data loss and corruption of data and system.\
Of course, bold testers are invited to test and report feedback :-)  

## Why and whereabouts?

This workbench grew out from my personal needs as a FreeCAD and 3D-Design newbie as of version 0.21.2.  
It meets my personal work style developped over some months.  
I'll try to describe this to give readers the opportunity to **check whether this WB may fit their own purpose.**

### Applications
* simple machine construction
* simple parts for milling, 3D-Print as available for DYI
* CAM for 3-prints, laser cutting and milling
* combining imported models for purchased components
* simple Animations to check validity of design

Design workflow in these circumstances is very iterative, skd. of inventive.  

It's the very purpose of the design process to check the validity of any approach.  
Changing features buried deep in early steps, even when complicated models are built upon, is the normal case, not the exception.  
Parametric behaviur is mandatory. Flipping sketches and TNP issues are poison.
I stepped back to openSCAD (which imho is 100% parametric and datum based) at least 3 times for theses reasons.



### Experience on the learning curve
We know: FreeCAD is not a coherent project, but a vivid ecosystem.  
Documentation both in in the "official" area and even more "out in the wild" internet is not coherent to version and recommend conflicting and mutual incompatible workflow, mostly without explicitly noting this fact.

#### The assembly quagmire
As of 0.21.2:
* Assembly 2+ is labeled deprecated
* Assembly3 does not even work for its own first beginners example
* Assembly4 (which best meets my personal work style) is cut of from future development for the moment
* "Version 1.0" is announced for some unspecified future

#### "Poor Man's Assembly"
Following the rationale: "a poor craftsman blames his tools" I developed my own assembly style, based on rigid ground of established FreeCAD components:
* avoiding any of the 0.21.2 assembly workbenches
* relying heavily on computed datum features, kept in spreadsheets
* relying on sketches and Part WB since the "lofty" thinking of independent parts flying into place, guided by my numbers, meets my style of thinking
* avoiding PartDesign WB, since with calculated features, I don't see much advantage that pays off the restriction (single connected solid) and overhead
* relying on links/link groups with calculated placement
* even do some assembly with parametrized parts as in Assembly4 variant parts
* finally avoid "old style" part reuse techniques (Draft Arrays, Draft clones, shape binders, copy...) as far as possible
* organize my design modules in Std_Part containers
* "Animator" macro with mixed experience

#### The Global Placement Problem

The inacessibility of Real Global Placements for linked Parts from the realm of FreeCAD-Expressions (i.e. Properties and Spreadsheets) was the main driving force of tinyAsm. 
This forum thread:
[How can I access real global placement of Linked items in Expressions or spreadsheet?](https://forum.freecad.org/viewtopic.php?t=87609)
copign with the global placement problem grow into development log of this tinyAsm WB.  
Much of tinyAsm is about workaround to this limitation.
It may well be that when "1.0" provides a simple Expression function for this, much of the need for tinyAsm is gone.

**Why** do we need Global Placement in spreadsheets?

Calcualted design I found robust but tedious.
Graphic design is mor intutive, faster in the first way, but prone to TNP, flipping sketches. 
And relations buried deep in some feature's property expressions are hard to maintain, if projects get complicated.
This may eaysily eat up all the time initially saved.

I remember the discussion of "DWIM"-iness in Perl: 
It's nice if computers "automagically" "Do What I Mean".
But it does not always work.

Inspired from that experience, I'd like to use Graphical Design 
* for simple things
* for fancy details attached to a robust core feature
* contained in a usbproject of limited complexity, so that repair for a broken feature is not far away from the first visible occurance

This strategy requires to **switch back from Graphic Design to Calculated Design**.  
Unfortunately, with linked parts, the **real Global Placement is not accessible for the "Expression World"**, i.e Spredsheets and Property fields of geometric features.

Global Placment of a linked Part with respect to the containing Link is **available in Python**, however.
This was the point when the desire for **user defined python fuctions in spreadsheet** became even more pressing.

With linked parts, the very concept of global placement cannot be restricted to the linked part alone, but has to consider the chain of Links which may modify placement.  
There is a great macro "`GetGlobalPlacement`", which, however, works over the `GUI`. Obviously, the `GUI` has solved the challenge, since it is essential for a correct display.  
This macro served as **benchmark and inspiration** for the global placment code in tinyAsm.

#### Features missing from Assembly4
##### Variant Parts
Asm4 provides a variant part feature, that works fine, but only with its own overhead containers.  
I mangaged to resemble the behaviout with Std_Links to quite some extend.  
Tests are not yet finished. I still struggle with broken coherece after applying CopyOnChange: Changes in the source parts other than the variant variables are not forwarded, obviously. This ist still TBD.
May be that some future component may provide some workaround. 

##### Attacher
Asm4 provides an Attachment tool by **matching LCS** of the child to a LCS of the parent. In contrast to the builtin Part-Attacher, the **child** is matched **to some arbitrary target point**, not to its origin.

The behaviour is easily implemented with placment algebra. It could be done in a spreadsheet.  
However, apart from the Golbal Placement issue, chained attachments dependending on a single spreadsheet may complicate recompute dependency. 

Therefore, tinyAsm therefore provides an attachable Part-like FPO which does the Global-Placmenent-lookup, the Placment calculation and fits neatly into the recalc DAG.

##### Animator
Asm4 provides a nice lean animator which simply animates one of its special Variables.

The Animator Macro as obvious replacement turned out to be somwhat clumsy and overloaded. The concept of pushing the animated variable insteat of letting features pull it makes life quite complicated. For simple kinematic checks, some obvious advantage of this approach is not visible.

The tinyAsm-Animator is even simpler than since it runs an **ordinary Property** of itself, where **any expression can refer to**.  
The example show how to extend this by some spreadsheet acrobatic to e.g. oscillations and sequenced animated phases with arbitrary complexity.

#### "To Solve" or "Not to Solve"?
Asm4 labels itself as "solver-free".  
In contrast, Asm3, as it seems, tries to define any problem as a nail, to be driven by some omnipresent solver hammer.  
Let's see what the future brings.

Until then, tinyAsm follows the rationale that **3D-solving** might be **nice**, but has a **price tag** attached to it.  
The 2D-solver in sketches is out of question. To tame it's quirks is a matter of work style.

To meet the rare cases where 3D-solver is really needed (i.e. beyond "nice-to-have"), tinyAsm provides access to the **numpy solver** for the case of the "**Reverse Kinematic Problem**".
First tests for a hexapod-like actuator look good. Animated solving is still TBD.




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




