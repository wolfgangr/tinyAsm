
import FreeCAD
import FreeCADGui
from PySide import QtCore
# import threading
# import time
# import asyncio



## bare FPO w/ driving animator

def create_tinyAnimator(obj_name = 'tinyAnimator'):
    """
    bare FeaturePython with lean animator function

    Properties:

    Config:
    - tick: time in s between steps, mileage may vary below ~ 50 ms
    - steps: number of steps the animator is running from 0 to 1
    - idle_val: output when animator is not running

    Control:
    - run_now: True to start, False to stop animation
    - run_cont: False for single run, True for continuous repetition

    output:
    (read-only)
    float value [ 0 .. 1 ] resembling current animation state
    refer dependent objects to this Property to get animated

    (copyleft LGPL) Wolfgang Rosner, June 2024
    wolfgangr@github.com

    """

    obj = FreeCAD.ActiveDocument.addObject('App::FeaturePython', obj_name)
    tinyAnimator(obj)

    App.ActiveDocument.recompute()
    return obj

##
# called after timeout

def nextIteration(obj):
    # print('nextIteration')

    # cancel on manual stop?
    if not obj.run_now:
        obj.output = obj.idle_val
        # return

    else:
        out = obj.output
        out += 1/obj.steps

        if out > 1:
            if obj.run_cont:        # roll over
                obj.output = 0
                print("iteration rollover restart")
                # return

            else:                   # reached end of single run
                obj.run_now=False
                obj.output = obj.idle_val
                print("animation ending after single run")
                # return

        else:                       # normal increment
            obj.output = out        # this will trigger onChanged where we can reload
            # print(f"iteration {out}")
            # return

    # print("recalculate and update ")
    obj.touch()
    # obj.Document.recompute()
    # FreeCADGui.updateGui()



##

class tinyAnimator():
    def __init__(self, obj):
        """
        create empty solver object
        all parameters and communication goes via Properties
        """

        self.Type = 'tinyAnimator'
        obj.Proxy = self


        # properties
        grp = 'Config'

        # frequency of updates
        obj.addProperty("App::PropertyTime", "tick", grp,
            'time paused between adjacent animation steps')
        obj.tick = 1

        # number of steps
        obj.addProperty("App::PropertyInteger", 'steps', grp,
            'number of steps for a full animation cycle')
        obj.steps = 30

        # idle value
        obj.addProperty("App::PropertyFloat", 'idle_val', grp,
            'output value if Animator is not running')

        grp = 'Control'
        # execute control flags
        obj.addProperty("App::PropertyBool", "run_now", grp,
            "set true to run Animator - once run_cont=False; 'armed/disarmed' for 'cont'")
        obj.addProperty("App::PropertyBool", "run_cont", grp,
            "set true for continous animation, masked by disarmed")


        # one single output (0...1)
        obj.addProperty("App::PropertyFloat", "output", "Out",
            "output of the animator; cycles 0...1, bind your expressions hereto")
        obj.setPropertyStatus('output', ['ReadOnly', 'Transient', 'Output', 14, 21])

        # self.animator = threading.Thread(target = self.runAnimation, args=(obj,))


    def onDocumentRestored(self, obj):
        obj.Proxy = self


    def onChanged(self, obj, prop):
        match prop:
            case 'idle_val':
                obj.output = obj.idle_val
                obj.touch()

            case 'steps':
                if not obj.steps:
                    raise RuntimeWarning('steps = 0 will throw div-by-zero on animation')


            case 'run_now':
                if obj.run_now:
                    obj.output = 0

                # else:
                #     if hasattr(self, 'timer'):
                #         print('###TBD### canceled timer')
                #     else:
                #         print('noop stopped timer')



            case 'output':
                if obj.run_now:
                    QtCore.QTimer.singleShot(obj.tick.Value * 1000, lambda:  nextIteration(obj))
                    # print('re-started timer for next iteration')

                    obj.touch()
                    obj.Document.recompute()
                    FreeCADGui.updateGui()

            case _:
                # print (f'debug: Property {prop} changed - no special handling')
                pass

        # print ('debug: after onChanged match')


    # def execute(self, obj):
