"""
attachByGP.py
- inspired by Assembly4-Attacher -
attaches one Part Container or Part Link to another one
by matching the placements of first level subobjects
(preferrably LCS)
and additional placment offset

(c) Wolfgang Rosner 2024 - wolfagngr@github.com
License: LGPL 2+

# boilerplated from
# https://wiki.freecad.org/Create_a_FeaturePython_object_part_I#Complete_code
"""



import FreeCAD # as App

try:
    import FreeCADGui
except ImportError:
    print("GPattacher running in GUI-less mode")

##

def create_GPatt(obj_name = 'GPattach', attChild = None, attParent = None):
    """
    Object creation method
    target priority:
    - "attXXX" call argument
    - pop'd obj in GUI selection -> child
      pop'd obj in GUI selection -> parent
    - default: None - to be assigned later
    """

    obj = FreeCAD.ActiveDocument.addObject('App::LinkPython', obj_name)
    GPattach(obj)

    if not (attParent and attChild):
        try:
            selection = FreeCADGui.Selection.getSelection()
        except:
            selection = None
            print('no object selected')

    if attChild:
        obj.LinkedObject = attChild

    elif selection:
        obj.LinkedObject = selection.pop(0)


    if attParent:
        obj.a1AttParent = attParent
    elif selection:
        obj.a1AttParent = selection.pop(0)

    FreeCAD.ActiveDocument.recompute()
    return obj

##

class GPattach():
    def __init__(self, obj):
        """
        Default constructor
        """
        self.Type = 'GPattach'
        obj.Proxy = self

        obj.ViewObject.Proxy = 0


        # Parent
        obj.addProperty("App::PropertyLink", "a1AttParent", "Attachment",
            'The container Object where the attachment anchor resides in ')

        obj.addProperty("App::PropertyEnumeration", "a2AttParentSubobjects", "Attachment",
            'available subObjects of Parents - select Anchor')

        obj.addProperty("App::PropertyPlacement", "a3AttParentSubobjPlacement", "Attachment",
            'global Placement of selected Parent SubObject - read only')
        obj.setEditorMode("a3AttParentSubobjPlacement", ['ReadOnly'])

        obj.addProperty("App::PropertyPlacement", "c1AttachmentOffset", "Attachment",
            'offset to be added to parents anchor for effective Anchor Point - editable')

        # # Child
        # obj.addProperty("App::PropertyLink", "b1AttChild", "Attachment",
        #     'The container Object where the attachment child pivot resides in ')

        obj.addProperty("App::PropertyString", "b1AttChild", "Attachment",
             'The container Object to be attached - synced to Linked object - change this instead')
        obj.setEditorMode('b1AttChild', ['ReadOnly'])

        #
        obj.addProperty("App::PropertyEnumeration", "b2AttChildSubobjects", "Attachment",
            'available subObjects of child - select pivot')
        #
        obj.addProperty("App::PropertyPlacement", "b3AttChildSubobjPlacement", "Attachment",
            'global Placement of selected Child SubObject - read only')
        obj.setEditorMode("b3AttChildSubobjPlacement", ['ReadOnly'])

        # calculation
        obj.addProperty("App::PropertyPlacement", "c2AttChildPlcInverse", "Attachment",
            'inverse of global Placement of Link Target SubObject - read only')
        obj.setEditorMode("c2AttChildPlcInverse", ['ReadOnly'])

        obj.addProperty("App::PropertyPlacement", "c3AttChildResultPlc", "Attachment",
            'effective Placement matrix applied to the child = invert(ChildPLC) * AttOffs * ParentPLC')
        obj.setEditorMode("c3AttChildResultPlc", ['ReadOnly'])



    def onDocumentRestored(self, obj):
        """
        fix missing proxy issues
        https://wiki.freecad.org/FeaturePython_methods
        """
        obj.Proxy = self


    def execute(self, obj):

        # retrieve list of subobjects and set enum for selection
        if obj.a1AttParent:
            if hasattr(obj.a1AttParent, 'Group'):
                subobjs = [ itm.Name for itm in obj.a1AttParent.Group ]
                if hasattr(obj.a1AttParent, 'Origin'):
                    subobjs.append('Origin')

                obj.a2AttParentSubobjects = subobjs

        if obj.LinkedObject:       #obj.b1AttChild:
            obj.b1AttChild = obj.LinkedObject.Name
            if hasattr(obj.LinkedObject, 'Group'):
                subobjs = [ itm.Name for itm in obj.LinkedObject.Group ]
                if hasattr(obj.LinkedObject, 'Origin'):
                    subobjs.append('Origin')

                obj.b2AttChildSubobjects = subobjs
                if not subobjs:
                    print ('cannot attach: linked object does not yet contain any subobjects')
            else:
                print('cannot attach: linked object ist not of Group type - may be select a Part?')

        else:
            print('cannot attach: no Linked Object selected')

        # retrieve selected subobjects real global Placement
        plcParent = None
        plcChild_inv = None
        plcChild_inv = None

        pathParent = obj.a2AttParentSubobjects
        if obj.a1AttParent and pathParent:
            pathParent += '.'
            plcParent = obj.a1AttParent.getSubObject(pathParent,3)
            if plcParent:
                obj.a3AttParentSubobjPlacement =plcParent.Matrix
            else:
                print(f"cannot retrieve placement of parent subObject named >{pathParent}<")

        #
        pathChild = obj.b2AttChildSubobjects
        if obj.LinkedObject and pathChild:
            pathChild += '.'
            plcChild = obj.LinkedObject.getSubObject(pathChild,3)
            if plcChild:
                obj.b3AttChildSubobjPlacement = plcChild.Matrix
                plcChild_inv =  plcChild.inverse()
                obj.c2AttChildPlcInverse = plcChild_inv.Matrix

            else:
                print(f"cannot retrieve placement of child subObject named >{pathChild}<")

        # try to construct a final result?
        if  plcChild_inv  and plcParent:
            plcOffset = obj.c1AttachmentOffset
            plcResult = plcParent.multiply(plcOffset).multiply(plcChild_inv)
            obj.c3AttChildResultPlc = plcResult.Matrix

            # is there custom expression inside ....
            if 'LinkPlacement' in [ ex[0] for ex in  obj.ExpressionEngine ]:
                print ("custom expression in LinkPlacement - won't overwrite" )
            else:
                # do your job
                obj.LinkPlacement =  plcResult.Matrix

        else:
            print('cannot calculate final attachment')

