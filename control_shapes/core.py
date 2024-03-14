"""
Contains the core low level functionality of the control shape manager. The functions here work directly
with the data in the nurbs curves.
"""
import logging
import os
import re
import subprocess

from maya import cmds

from mechRig_toolkit.control_shapes import utils

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

CURRENT_DIRECTORY = os.path.dirname(__file__)
SHAPE_LIBRARY_PATH = os.path.join(CURRENT_DIRECTORY, "shapes")


def get_shape(crv=None):
    """Returns a dictionary containing all the necessery information for rebuilding the passed in crv."""
    crvShapes = validate_curve(crv)

    crvShapeList = []

    for crvShape in crvShapes:
        crvShapeDict = {
            "points": [],
            "knots": [],
            "form": cmds.getAttr(crvShape + ".form"),
            "degree": cmds.getAttr(crvShape + ".degree"),
            "color": cmds.getAttr(crvShape + ".overrideColor"),
        }
        points = []

        for i in range(cmds.getAttr(crvShape + ".controlPoints", s=1)):
            points.append(cmds.getAttr(crvShape + ".controlPoints[%i]" % i)[0])

        crvShapeDict["points"] = points
        crvShapeDict["knots"] = utils.get_knots(crvShape)

        crvShapeList.append(crvShapeDict)

    return crvShapeList


def set_shape(crv, crvShapeList):
    """Creates a new shape on the crv transform, using the properties in the crvShapeDict."""
    crvShapes = validate_curve(crv)
    if crvShapes:
        oldcolor = cmds.getAttr(crvShapes[0] + ".overrideColor")
        cmds.delete(crvShapes)

    for i, crvShapeDict in enumerate(crvShapeList):
        tmpCrv = cmds.curve(
            p=crvShapeDict["points"],
            k=crvShapeDict["knots"],
            d=crvShapeDict["degree"],
            per=bool(crvShapeDict["form"]),
        )
        newShape = cmds.listRelatives(tmpCrv, s=1)[0]
        cmds.parent(newShape, crv, r=1, s=1)

        cmds.delete(tmpCrv)
        newShape = cmds.rename(newShape, crv + "Shape")

        cmds.setAttr(newShape + ".overrideEnabled", 1)


def validate_curve(crv=None):
    """Checks whether the transform we are working with is actually a curve and returns it's shapes"""
    # if cmds.nodeType(crv) == "transform" and cmds.nodeType(cmds.listRelatives(crv, c=1, s=1)[0]) == "nurbsCurve":
    #    crvShapes = cmds.listRelatives(crv, c=1, s=1)
    if cmds.nodeType(crv) == "transform" or cmds.nodeType(crv) == "joint":
        if cmds.listRelatives(crv, c=1, s=1):
            crvShapes = cmds.listRelatives(crv, c=1, s=1)
        else:
            crvShapes = list()
    elif cmds.nodeType(crv) == "nurbsCurve":
        crvShapes = cmds.listRelatives(cmds.listRelatives(crv, p=1)[0], c=1, s=1)
    else:
        cmds.error("The object " + crv + " passed to validate_curve() is not a curve")
    return crvShapes


def load_from_lib(shape=None):
    """Loads the shape data from the shape file in the SHAPE_LIBRARY_PATH directory"""
    path = os.path.join(SHAPE_LIBRARY_PATH, shape + ".json")
    data = utils.load_data(path)
    return data


def save_to_lib(crv=None, shapeName=None):
    """Saves the shape data to a shape file in the SHAPE_LIBRARY_PATH directory"""
    crvShape = get_shape(crv=crv)
    path = os.path.join(SHAPE_LIBRARY_PATH, re.sub("\s", "", shapeName) + ".json")
    for shapeDict in crvShape:
        shapeDict.pop("color", None)
    utils.save_data(path, crvShape)


def set_color(crv, color):
    """Sets the overrideColor of a curve"""
    if cmds.nodeType(crv) == "transform":
        crvShapes = cmds.listRelatives(crv)
    else:
        crvShapes = [crv]
    for crv in crvShapes:
        cmds.setAttr(crv + ".overrideColor", color)


def get_color(crv):
    """Returns the overrideColor of a curve"""
    if cmds.nodeType(crv) == "transform":
        crv = cmds.listRelatives(crv)[0]
    return cmds.getAttr(crv + ".overrideColor")


def open_control_shape_directory():
    subprocess.Popen(r'explorer /open,"%s"' % SHAPE_LIBRARY_PATH.replace("/", "\\"))
    log.info("Exploring to %s" % SHAPE_LIBRARY_PATH)
