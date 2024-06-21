
# import dev.myTinyAsm.rkSolve as rkSolve
# import



import FreeCAD

import numpy as np
from scipy.optimize import fsolve
# https://realpython.com/python-pretty-print/
import pprint
import re
import time


# # required if we overload execute()
def recompute_cells(obj):
    u_range = obj.getUsedRange()
    range_str = u_range[0] + ':' + u_range[1]
    if range_str != '@0:@0':       # if sheet is not empty
        obj.recomputeCells(range_str)


# =Unnamed#pySheet.cpy_res_posTip
def parsePropPath( proppath , default_sheet = 'pySheet'):
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
    base = plc.Base
    # rotQ  = plc.Rotation.Q      # normed quaternion
    ypr = plc.Rotation.getYawPitchRoll()
    rv   = list(base / clen)
    # rv.extend(list(rotQ))
    rv.extend(list(ypr))
    rv_ary = np.array(rv)
    return rv_ary

# wraps acces to FC model via spreadsheet properties
#   to flat python callable format
#   input:  model input, i.e. written to sheet, property outside sheet
#       supposedly a vector i.e. List or tuple
#   output: model output, i.e. read from sheet, may be property or cell
#       supposedly a placement
#   target: target placement to be substracted (or whatever) since solver
#       targets to all over zeros
#  hangon .. can the quaternions be zero at all? better go for euler angles??

class wrapModel:

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


    def callModel(self, vect_in):
        # sheet.addProperty('App::PropertyPythonObject', 'D8' )
        # setattr(sheet, 'D8', propD8)
        # setattr(self.iSheet, self.iPropName, list(vect_in) )
        # t1 = time.perf_counter(), time.process_time()
        # print  (list(vect_in))
        setattr(self.solvBase, self.inProp,  list(vect_in) )
        setattr(self.iObj, self.iPropName,  list(vect_in) )

        self.iObj.touch()

        # t2 = time.perf_counter(), time.process_time()
        # recompute_cells(self.iObj)
        # self.iObj.recomputeCells(self.iPropName)
        recompute_cells(self.iObj)
        self.oDoc.recompute([self.oObj])
        self.oDoc.recompute()
        # # recompute_cells(self.iSheet)
        # #
        # # self.iDoc.recompute()
        # # if not self.iDoc == self.oDoc:
        # #     self.oDoc.recompute()

        # t3 = time.perf_counter(), time.process_time()

        plc = self.oObj.getSubObject(self.oPropName + '.', retType=3)
        # for debugging and final result - maybe move out later?
        ## ================================~~~~~~~~~~~~~~~~~~~~~~~~~~--------------------------------------
        setattr(self.solvBase, self.outProp,  plc )
        stratPlc = stratifyPlacement(plc, self.clen)
        # perform vector like substraction on lists
        # rv = [ i2 - i1  for i1, i2 in zip (stratPlc, self.stratTarget) ]
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

        ## TBD ---- current.multiply(inverse(target))
        # solver approaches all zeroes!
        # # dPlc = plc.multiply(self.iTarget)
        # #
        # # base = dPlc.Base
        # # ypr = dPlc.Rotation.getYawPitchRoll()
        # # rv = list(base / self.clen)
        # # rv.extend(ypr)
        return rv_ary




## bare FPO w/ driving solver

def create_rkSolver(obj_name = 'pySolver'):
    """
    bare FeaturePython with attached solver for reverse kinematic problem
    """

    obj = FreeCAD.ActiveDocument.addObject('App::FeaturePython', obj_name)
    # rkSolve.rkSolver(obj)
    rkSolver(obj)

    # App.ActiveDocument.recompute()
    return obj

class rkSolver():
    def __init__(self, obj):
        """
        create empty solver object
        all parameters and communication goes via Properties
        """

        self.Type = 'rkSolver'
        obj.Proxy = self


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


    # set model in to start vector independent of solver
    # to be called at init, restore, change, non-solivng execute
    def resetModel(self, obj):
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
        # pass

    def execute(self, obj):
        """
        Called on document recompute
        """
        print('Recomputing {0:s} ({1:s})'.format(obj.Name, self.Type))

        if not getattr(obj, "solve_now", None):
            return None

            # def __init__(self,
            #             input:  str, inprop:  str,
            #             output: str, outprop: str,
            #             target: FreeCAD.Placement = None,
            #             clen: float =1 ):
        t0 = time.perf_counter(), time.process_time()

        model = wrapModel(
                solvBase = obj,
                input   =  obj.ModelInRef,
                inprop  = 'ModelInVector',            # obj.ModelInVector,
                output  =  obj.ModelOutRef,
                outprop = 'ModelOutPlacement',       # obj.ModelOutPlacement,
                target  =  obj.TargetPlacement,
                clen    =  obj.Clen
            )

        startVec = obj.StartVector

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


