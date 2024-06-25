import logging

from maya import cmds

from mechRig_toolkit.control_shapes import core

log = logging.getLogger(__name__)

def mirror_ctl_shapes(*args):
    """Mirrors the selected control's shape to the other control on the other side"""
    sel = cmds.ls(sl=1, fl=1)
    for ctl in sel:
        search = "lf_"
        replace = "rt_"
        if "rt_" in ctl:
            search = "rt_"
            replace = "lf_"
        shapes = core.get_shape(ctl)
        color_val = core.get_color(ctl)
        core.set_shape(ctl.replace(search, replace), shapes)
        flip_shape(ctl.replace(search, replace))
        core.set_color(ctl.replace(search, replace), color_val)
    cmds.select(sel)
    log.info(
        "Mirrored control shape {} to {}".format(ctl, ctl.replace(search, replace))
    )


def flip_shape_callback(*args):
    """Flips the selected control shapes to the other side in all axis"""
    sel = cmds.ls(sl=1, fl=1)
    for each in sel:
        flip_shape(each)
    cmds.select(sel)


def flip_shape_X(*args):
    """Flips the selected control shapes to the other side in X"""
    sel = cmds.ls(sl=1, fl=1)
    for each in sel:
        flip_shape(each, [-1, 1, 1])
    cmds.select(sel)


def flip_shape_Y(*args):
    """Flips the selected control shapes to the other side in Y"""
    sel = cmds.ls(sl=1, fl=1)
    for each in sel:
        flip_shape(each, [1, -1, 1])
    cmds.select(sel)


def flip_shape_Z(*args):
    """Flips the selected control shapes to the other side in Z"""
    sel = cmds.ls(sl=1, fl=1)
    for each in sel:
        flip_shape(each, [1, 1, -1])
    cmds.select(sel)


def flip_shape(crv=None, axis=[-1, -1, -1]):
    """Scales the points of the crv argument by the axis argument. This function is not meant to be
    called directly. Look at the flipCtlShape instead."""
    shapes = core.get_shape(crv)
    newShapes = []
    for shape in shapes:
        for i, each in enumerate(shape["points"]):
            shape["points"][i] = [
                each[0] * axis[0],
                each[1] * axis[1],
                each[2] * axis[2],
            ]
        newShapes.append(shape)
    core.set_shape(crv, newShapes)
    cmds.select(crv)


def return_shapes(node, intermediate=False):
    """
    Get the shape node of a transform.
    This is useful if you don't want to have to check if a node is a shape node
    or transform.  You can pass in a shape node or transform and the function
    will return the shape node.

    Args:
        node: The name of the node.
        intermediate: True to get the intermediate shape.

    Returns:
        The name of the shape node.
    """
    returnShapes = []
    if cmds.nodeType(node) == "transform" or "joint":
        shapes = cmds.listRelatives(node, shapes=True, path=True)
        if not shapes:
            shapes = []
        for shape in shapes:
            is_intermediate = cmds.getAttr("%s.intermediateObject" % shape)
            if (
                intermediate
                and is_intermediate
                and cmds.listConnections(shape, source=False)
            ):
                returnShapes.append(shape)
                # return shape
            elif not intermediate and not is_intermediate:
                returnShapes.append(shape)
                # return shape
        return returnShapes
        if shapes:
            return shapes[0]
    elif cmds.nodeType(node) in ["mesh", "nurbsCurve", "nurbsSurface"]:
        is_intermediate = cmds.getAttr("%s.intermediateObject" % node)
        if is_intermediate and not intermediate:
            node = cmds.listRelatives(node, parent=True, path=True)[0]
            return get_shape(node)
        else:
            return node
    return None


def rotate_shape(rotation):
    """Rotates the selected node's shape nodes by the input rotation in object space.

    Args:
        rotation (list): x, y, z values in degrees

    Returns:
        None
    """
    for node in cmds.ls(selection=True):
        for shape in node.getShapes():
            if cmds.nodeType(shape) == "mesh":
                cmds.rotate(shape.vtx, rotation, os=1)
            elif cmds.nodeType(shape) == "nurbsCurve":
                cmds.rotate(shape.cv, rotation, os=1)


def scale_shape(node, scaleVector):
    """Scale controlCurve by [x, y, z]. Adjust controlCurve size of selected transform nodes.

    Args:
        node: Transform node.
        scaleVector: Scale vector.
        ocp: Object Center Pivot.
    Returns:
        None.
    Raises:
        Logs warning if node does not exist.
        Logs warning if node is not tranform type.
        Logs warning if scaleVector is not a list of three.
    """
    if not cmds.objExists(node):
        log.warning(node + " does not exist.")
        return
    elif not (
        cmds.objectType(node, isType="transform")
        or cmds.objectType(node, isType="joint")
    ):
        log.warning("Input node requires transform or joint type.")
        return
    elif len(scaleVector) != 3:
        log.warning("Input scaleVector requires a list of three.")
        return

    shapeList = return_shapes(node)
    for shape in shapeList:
        cmds.select(cl=1)
        cmds.select(shape + ".cv[:]")
        cmds.scale(scaleVector[0], scaleVector[1], scaleVector[2], r=1, ocp=0)
    cmds.select(node)


def scale_up_selected(scaleValue=1.1):
    sel = cmds.ls(selection=True)
    if sel:
        for ctl in sel:
            scale_shape(ctl, [scaleValue, scaleValue, scaleValue])
        cmds.select(sel)
        return True


def scale_down_selected(scaleValue=0.9):
    sel = cmds.ls(selection=True)
    if sel:
        for ctl in sel:
            scale_shape(ctl, [scaleValue, scaleValue, scaleValue])
        cmds.select(sel)
        return True
