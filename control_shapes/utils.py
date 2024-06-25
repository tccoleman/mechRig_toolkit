"""Contains utility commands to help work and I/O nurbsCurve data."""
import json
import os

from maya import cmds
from maya import OpenMaya as om

SCRIPTS_DIR = os.path.dirname(__file__)


def validate_path(path=None):
    """Checks if the file already exists and provides a dialog to overwrite or not"""
    if os.path.isfile(path):
        confirm = cmds.confirmDialog(
            title="Overwrite file?",
            message="The file " + path + " already exists.Do you want to overwrite it?",
            button=["Yes", "No"],
            defaultButton="Yes",
            cancelButton="No",
            dismissString="No",
        )
        if confirm == "No":
            cmds.warning("The file " + path + " was not saved")
            return 0
    return 1


def load_data(path=None):
    """Loads raw JSON data from a file and returns it as a dict"""
    if os.path.isfile(path):
        f = open(path, "r")
        data = json.loads(f.read())
        f.close()
        return data
    else:
        cmds.error("The file " + path + " doesn't exist")


def save_data(path=None, data=None):
    """Saves a dictionary as JSON in a file"""
    if validate_path(path):
        f = open(path, "w")
        f.write(json.dumps(data, sort_keys=1, indent=4, separators=(",", ":")))
        f.close()
        return 1
    return 0


def get_knots(crvShape=None):
    mObj = om.MObject()
    sel = om.MSelectionList()
    sel.add(crvShape)
    sel.getDependNode(0, mObj)

    fnCurve = om.MFnNurbsCurve(mObj)
    tmpKnots = om.MDoubleArray()
    fnCurve.getKnots(tmpKnots)

    return [tmpKnots[i] for i in range(tmpKnots.length())]
