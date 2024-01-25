"""
This module contains functions to provide a higher level of interaction with the commands in the core.py file.
The commands in this file are meant to be the ones used by the users, so they should be used in the UI.


A lot of credit for my version of the control_shapes module goes to vshotarov.
I've incorporated a mix of my own control shape with his code for this module
https://bindpose.com/creating-maya-control-shape-manager/
"""
import functools
import logging
import os

from maya import cmds

from mechRig_toolkit.control_shapes import core

log = logging.getLogger(__name__)


def get_available_control_shapes():
    """Returns a list of the available control shapes in the specified library. Each element
    of the list is a tuple containing the label (name) of the controlShape and a reference
    to the command to assign that shape via functools.partial

    :return:
    """
    lib = core.SHAPE_LIBRARY_PATH
    return [
        (x.split(".")[0], functools.partial(assign_control_shape, x.split(".")[0]))
        for x in os.listdir(lib)
    ]


def assign_color(*args):
    """Assigns args[0] as the overrideColor of the selected curves

    :param args:
    :return:
    """
    for each in cmds.ls(sl=1, fl=1):
        core.set_color(each, args[0])


def assign_control_shape(*args):
    """Assigns args[0] as the shape of the selected curves
    :param args:
    :return:
    """
    sel = cmds.ls(sl=1, fl=1)
    if sel:
        for each in sel:
            crv_shp = cmds.listRelatives(each, shapes=True, type="nurbsCurve")
            # If there's an existing curve under selection then
            if crv_shp:
                core.set_shape(each, core.load_from_lib(args[0]))
            # Otherwise, create a temp circle curve then replace it
            else:
                circle_temp = cmds.circle(
                    c=[0, 0, 0],
                    nr=[0, 1, 0],
                    sw=360,
                    r=1,
                    d=3,
                    ut=0,
                    tol=0.01,
                    s=8,
                    ch=0,
                )[0]
                circle_temp_shp = cmds.listRelatives(circle_temp, shapes=True)[0]
                cmds.parent(circle_temp_shp, each, r=True, s=True)
                cmds.rename(circle_temp_shp, "{}Shape".format(each))
                cmds.delete(circle_temp)
                core.set_shape(each, core.load_from_lib(args[0]))
            log.info("Created control shape {} on {}".format(args[0], each))
        cmds.select(sel)
    else:
        log.info("Nothing selected, creating control shape {}".format(args[0]))
        circle_temp = cmds.circle(
            name=args[0],
            c=[0, 0, 0],
            nr=[0, 1, 0],
            sw=360,
            r=1,
            d=3,
            ut=0,
            tol=0.01,
            s=8,
            ch=0,
        )[0]
        core.set_shape(circle_temp, core.load_from_lib(args[0]))
        cmds.select(circle_temp)


def save_ctl_shape_to_lib(*args):
    """Saves the selected shape in the defined control shape library

    :param args:
    :return:
    """
    result = cmds.promptDialog(
        title="Save Control Shape to Library",
        m="Control Shape Name",
        button=["Save", "Cancel"],
        cancelButton="Cancel",
        dismissString="Cancel",
    )
    if result == "Save":
        name = cmds.promptDialog(q=1, t=1)
        core.save_to_lib(cmds.ls(sl=1, fl=1)[0], name)
    # rebuild_UI()


def copy_ctl_shape(*args):
    """Copies the selected control's shape to a global variable for pasting

    :param args:
    :return:
    """
    global ctl_shape_clipboard
    global ctl_color_clipboard
    ctl_shape_clipboard = core.get_shape(cmds.ls(sl=1, fl=1)[0])
    ctl_color_clipboard = core.get_color(cmds.ls(sl=1, fl=1)[0])
    for ctlShape in ctl_shape_clipboard:
        ctlShape.pop("color")
    log.info("Copied curve shape from {}".format(ctlShape))


def paste_ctl_shape(*args):
    """Assigns the control's shape from the ctl_shape_clipboard global variable to the selected controls

    :param args:
    :return:
    """
    sel = cmds.ls(sl=1, fl=1)
    for each in sel:
        core.set_shape(each, ctl_shape_clipboard)
        core.set_color(each, ctl_color_clipboard)
    cmds.select(sel)
    log.info("Pasted curve shape to {}".format(ctl))


def delete_shapes():
    """Deletes curve shapes under selected

    :return:
    """
    sel = cmds.ls(sl=1, fl=1)
    for each in sel:
        shps = cmds.listRelatives(each, shapes=True, type="nurbsCurve")
        if shps:
            cmds.delete(shps)
    return
