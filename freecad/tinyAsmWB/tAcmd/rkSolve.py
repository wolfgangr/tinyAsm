"""
freecad/tinyAsmWB/tAcmd/rkSolve.py

(c) Wolfgang Rosner 2024 - wolfagngr@github.com
License: LGPL 2+

                'ToolTip' : "given \n"
                    + "- a FreeCAD project with 6 DoF\n"
                    + "- a target object to be placed\n"
                    + "- a target placement value\n"
                    + "solver modifies the model's DoF\n  until placement matches\n"
                    + "(uses scipy.optimize.fsolve)"

"""



import FreeCAD
import FreeCADGui
from pivy import coin

import numpy as np
from scipy.optimize import fsolve
import pprint
import re
import time

import os
from freecad.tinyAsmWB import ICON_PATH

##

def recompute_cells(obj):
    """ required if we overload execute()
        since sheets show a peculiar recomputing behaviur
    """
    u_range = obj.getUsedRange()
    range_str = u_range[0] + ':' + u_range[1]
    if range_str != '@0:@0':       # if sheet is not empty
        obj.recomputeCells(range_str)



def parsePropPath( proppath , default_sheet = 'pySheet'):
    """ parse source/target object path
        template:
            DocName#pySheet.cpy_res_posTip
    """

    match = re.match(r"^(([\w]+)(#))?(([\w]+)(\.))?([\w]+)$", proppath)
    if not match:
        print(f"canot parse property path: {proppath}")
        return None

    print ("match.groups(): ", match.groups())
    docpath = match.groups()[1]
    sheetpath = match.groups()[4]
    prop_subpath = match.groups()[6]

    if docpath:
        doc = FreeCAD.getDocument(docpath)
    else:
        doc = FreeCAD.ActiveDocument

    if not sheetpath:
        sheetpath = default_sheet
    sheet = doc.getObject(sheetpath)

    return (doc, sheet, prop_subpath)


def stratifyPlacement(plc: FreeCAD.Placement, clen=1):
    """ return a optimizable 6 DoF vector derivate from placement """
    base = plc.Base
    # cannot solve for seven variable with 6 inputs
    # so we go for euler angles instead
    # rotQ  = plc.Rotation.Q      # normed quaternion
    ypr = plc.Rotation.getYawPitchRoll()
    rv   = list(base / clen)
    # rv.extend(list(rotQ))
    rv.extend(list(ypr))
    rv_ary = np.array(rv)
    return rv_ary



class wrapModel:
    """ wraps acces to FC model via spreadsheet properties
    to flat python callable format
    input:  model input, i.e. written to sheet, property outside sheet
        supposedly a vector i.e. List or tuple
    output: model output, i.e. read from sheet, may be property or cell
        supposedly a placement
    target: target placement to be substracted (or whatever) since solver
        targets to all over zeros
    """

    def __init__(self, solvBase = None,
                input:  str='', inprop:  str='',
                output: str='', outprop: str='',
                target: FreeCAD.Placement = None,
                clen: float =1 ):

        self.solvBase = solvBase
        self.iDoc, self.iObj, self.iPropName = parsePropPath(input)
        self.oDoc, self.oObj, self.oPropName = parsePropPath(output)
        self.inProp  = inprop
        self.outProp = outprop

        self.clen = clen # normalize placement to match ~ quaternion components < 1

        if target:
            self.target = target
        else:
            self.target = FreeCAD.Placement()

        self.stratTarget = stratifyPlacement(target, self.clen)

        # self.t0 = time.perf_counter(), time.process_time()

    def check_setup(self):
        """ check model valididy to avoid exceptions during setup """
        # if not self.inProp:
        #     print("input property not configured")
        #     return False
        if not self.iObj:
            print("input Object not configured")
            return False
        if not self.oObj:
            print("output Object not configured")
            return False
        # else:
            return True

    def callModel(self, vect_in):
        # print  (list(vect_in))
        setattr(self.solvBase, self.inProp,  list(vect_in) )
        setattr(self.iObj, self.iPropName,  list(vect_in) )

        self.iObj.touch()

        # t2 = time.perf_counter(), time.process_time()
        recompute_cells(self.iObj)
        self.oDoc.recompute([self.oObj])
        self.oDoc.recompute()
        # t3 = time.perf_counter(), time.process_time()

        plc = self.oObj.getSubObject(self.oPropName + '.', retType=3)
        # for debugging and final result
        setattr(self.solvBase, self.outProp,  plc )
        stratPlc = stratifyPlacement(plc, self.clen)
        # perform vector like substraction on lists
        rv_ary = np.subtract(stratPlc, self.stratTarget)

        # t4 = time.perf_counter(), time.process_time()

        # print(list(rv_ary))

        # print ("time outside : ", t1[0] - self.t0[0]  ,  t1[1] - self.t0[1])
        # print ("time setup   : ", t2[0] - t1[0], t2[1] - t1[1])
        # print ("time recomp  : ", t3[0] - t2[0], t3[1] - t2[1])
        # print ("time result  : ", t4[0] - t3[0], t4[1] - t3[1])
        # t5 = time.perf_counter(), time.process_time()
        # print ("time print   : ", t5[0] - t4[0], t5[1] - t4[1])

        # self.t0 = time.perf_counter(), time.process_time()

        return rv_ary




## bare FPO w/ driving solver

def create_rkSolver(obj_name = 'pySolver'):
    """
    bare FeaturePython with attached solver for reverse kinematic problem
    """

    obj = FreeCAD.ActiveDocument.addObject('App::FeaturePython', obj_name)
    rkSolver(obj)
    return obj



##


class rkSolverViewProvider:
    ''' basic defs '''

    def __init__(self, obj):
        obj.Proxy = self
        self.vObject = obj

    def attach(self, vobj):
        self.standard = coin.SoGroup()
        vobj.addDisplayMode(self.standard,"Standard");

    def getDisplayModes(self,obj):
        "'''Return a list of display modes.'''"
        return ["Standard"]

    def getDefaultDisplayMode(self):
        "'''Return the name of the default display mode. It must be defined in getDisplayModes.'''"
        return "Standard"

    # start/stop by double click in tree view, change icon
    def getIcon(self):
        icon_stopped = os.path.join(ICON_PATH , 'taSolver_idle.svg')
        icon_running = os.path.join(ICON_PATH , 'taSolver_running.svg')
        if self._isRunning():
            return icon_running
        else:
            return icon_stopped

    def updateData(self, fp, prop):
        '''If a property of the handled feature has changed we have the chance to handle this here'''
        # fp is the underlying Base object?
        # if prop == "StartAnimating" or prop == "StopAnimating":
        # print("taAnimatorViewProvider.updateData.prop: ", prop)
        if prop == 'run_now':
            fp.ViewObject.signalChangeIcon()

    def doubleClicked(self,vobj):
        self._toggleRunning()

    def _isRunning(self):
        """ surface the 'run_now' property of the Base object """
        # console: getattr(obj.ViewObject.Object, 'run_now', False)
        solver = self.vObject.Object
        rv = getattr(solver, 'solve_now', False)
        return rv

    def _setRunning(self, mode: bool = True):
        solver = self.vObject.Object
        setattr(solver,  'solve_now', mode)

    def _toggleRunning(self):
        new_mode = not self._isRunning()
        self._setRunning(mode = new_mode)


##

class rkSolver():
    def __init__(self, obj):
        """
        create empty solver object
        all parameters and communication goes via Properties
        """

        self.Type = 'rkSolver'
        obj.Proxy = self
        rkSolverViewProvider(obj.ViewObject)

        # properties
        grp = 'solverConfig'

        # model in ref: str
        obj.addProperty("App::PropertyString", "ModelInRef", grp,
            'the sheet ( or whatsever) that href(reads) model input and gets touched to start recompute')

        # model out ref: str
        obj.addProperty("App::PropertyString", "ModelOutRef", grp,
            'the context&object to get target placement from; e.g Part_foo.LCS_bar')


        # target plc
        obj.addProperty("App::PropertyPlacement", "TargetPlacement", grp,
            'the placement of model tip where it should be moved to by the solver')

        # start vector
        obj.addProperty("App::PropertyPythonObject", "StartVector", grp,
            'initial Value of model input for the solver to start')

        # characteristic length (to scale pos rel to normed quaternion)
        obj.addProperty("App::PropertyDistance", "Clen", grp,
            'characteristic dimension of the target property to align scaling to 0...1 as of rot quaternion components')
        setattr(obj, "Clen", '100 mm')

        grp = 'solverOut'
        # model in vector
        # access with href() to keep solver out of DAG
        obj.addProperty("App::PropertyPythonObject", "ModelInVector", grp,
            'model input vector as supplied by the solver - read only')
        obj.setPropertyStatus('ModelInVector', ['ReadOnly', 'Transient', 'Output', 14, 21])

        # model out plc
        obj.addProperty("App::PropertyPlacement", "ModelOutPlacement", grp,
            'model output placement - for final processing - retrieved by solver code - read only')
        obj.setPropertyStatus('ModelOutPlacement', ['ReadOnly', 'Transient', 'Output', 14, 21])

        # execute control flags
        grp = 'solverControl'
        obj.addProperty("App::PropertyBool", "solve_now", grp,
            "set true to run solver once on execute if solve_cont=False; 'armed/disarmed' for 'cont'")

        obj.addProperty("App::PropertyBool", "solve_cont", grp,
            "set true for continous solving on everey recompute, masked by disarmed")

        # set model in to start vector
        self.resetModel(obj)
        # ============~~~~~~~–-------------------------



    def resetModel(self, obj):
        """
            set model in to start vector independent of solver
            to be called at init, restore, change, non-solivng execute
        """
        vec = obj.StartVector
        setattr(obj, 'ModelInVector', vec)

    def updateStartVec(self, obj):
        vec = obj.ModelInVector
        setattr(obj, 'StartVector', vec)


    # def onChanged(self, obj, prop):

    def onDocumentRestored(self, obj):
        obj.Proxy = self
        self.resetModel(obj)
        # self.execute(obj)

    # def onChanged(self, obj, prop):
    #     """ recompute upon change in solve_now """
    #
    #     match prop:
    #         case 'solve_now':
    #             obj.touch()
    #             obj.Document.recompute()
    #             FreeCADGui.updateGui()
    #
    #         case _:
    #             # print (f'debug: Property {prop} changed - no special handling')
    #             pass


    def execute(self, obj):
        """
        this is where the simulation is started
        to avoid recursive recomputes, place solver in own FCStd document
        """
        print('Recomputing {0:s} ({1:s})'.format(obj.Name, self.Type))

        # are we started?
        if not getattr(obj, "solve_now", None):
            return None

        # are we configured?
        input   =  obj.ModelInRef
        output  =  obj.ModelOutRef
        if (not input) or (not output):
            print("model in / out ref not configured")
            setattr(obj, "solve_now", False)
            return None

        t0 = time.perf_counter(), time.process_time()

        model = wrapModel(
                solvBase = obj,
                input   =  input,                   # obj.ModelInRef,
                inprop  = 'ModelInVector',          # obj.ModelInVector,
                output  =  output,                  # obj.ModelOutRef,
                outprop = 'ModelOutPlacement',      # obj.ModelOutPlacement,
                target  =  obj.TargetPlacement,
                clen    =  obj.Clen
            )

        if not model.check_setup():
            print("   ... aborting solver")
            setattr(obj, "solve_now", False)
            return None

        startVec = obj.StartVector
        if  len(startVec) != 6:
            print("len(start Vector) != 6 .... aborting solver")
            setattr(obj, "solve_now", False)
            return None

        t1 = time.perf_counter(), time.process_time()

        solutionInfo=fsolve(model.callModel, startVec, full_output=1)

        t2 = time.perf_counter(), time.process_time()
        pprint.pprint(solutionInfo)

        t3 = time.perf_counter(), time.process_time()

        print ("time setup   : ", t1[0] - t0[0], t1[1] - t0[1])
        print ("time solve   : ", t2[0] - t1[0], t2[1] - t1[1])
        print ("time output  : ", t3[0] - t2[0], t3[1] - t2[1])


        if not getattr(obj, "solve_cont", None):
            setattr(obj, "solve_now", False)


