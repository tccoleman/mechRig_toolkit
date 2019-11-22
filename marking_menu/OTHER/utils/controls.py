import os
import json
import logging

import pymel.core as pm
from maya import cmds

LOG = logging.getLogger(__name__)

CIRCLE_TYPE = 'circle'
SQUARE_TYPE = 'square'


def parseDefaultControls():
    """Get the default JSON control shapes file back as a Python dict.

    Returns:
        dict
    """
    ctlFile = os.path.join(os.path.dirname(__file__), 'defaultControlShapes.json')
    with open(ctlFile, 'r') as f:
        defaultCtlShapes = json.load(f)

    return defaultCtlShapes


def getControlShape(shapeName='circle'):
    """Get shapes data related to a default control.

    Args:
        shapeName (str): Name of the shape key from `defaultControlShapes.json`

    Returns:
        dict
    """
    defaultShapes = parseDefaultControls()

    if shapeName in defaultShapes:
        return defaultShapes[shapeName]

    return {}


def createControl(shapeData, node=None, parent=None, scale=1.0, approxScale=True):
    """Create a control at the given target with the given shape data.

    Args:
        shapeData (dict): Shape information for each curve to be created.
        node (pm.nt.Transform): If provided, shapes created are merged into the given transform.
        parent (pm.nt.Transform): Node to parent the new control object under.
        scale (float): Default scale to use for newly created control.
        approxScale (bool): Guess the scale for the newly created control.

    Returns:
        pm.nt.Transform
    """
    if node is not None and not isinstance(node, pm.nt.Transform):
        raise TypeError('Expected a Transform node, got {0}'.format(type(node).__name__))

    # create control with shape data under a new transform
    ctl = pm.createNode('transform', n='ctl#')
    addShapes(ctl, shapeData)

    # match new control to `node`
    if node is not None:
        if '_jnt' in node.nodeName():
            cleanNodeName = node.nodeName().replace('_jnt', '')
        else:
            cleanNodeName = node.nodeName()

        ctl.rename('{0}_ctl'.format(cleanNodeName))
        ctl.rotateOrder.set(node.rotateOrder.get())
        ctl.setTranslation(node.getTranslation('world'), 'world')
        ctl.setRotation(node.getRotation('world'), 'world')

    # set control's parent, if None parents to world
    ctl.setParent(parent)

    # scale the shapes nodes based off `node` bounding box
    if approxScale:
        scale = guessScale(ctl, node)
    scaleControl(str(ctl), [scale, scale, scale])

    # Rename ctl shape nodes
    rename_shapes(str(ctl))

    pm.select(cl=True)

    return ctl


def addShapes(node, shapeData):
    """Add all shapes for the given shape data to the given node.

    Args:
        node (pm.nt.Transform): PyMEL transform object.
        shapeData (dict): Shape data for position, knots, degree, and periodic.

    Returns:
        list: New shape nodes
    """
    if not isinstance(node, pm.nt.Transform):
        raise TypeError('Expected a Transform node, got {0}'.format(type(node).__name__))
    shapes = []
    for data in shapeData['shapes']:
        kw = dict()
        for k, v in data.items():
            kw[str(k)] = v
        curve = pm.curve(**kw)
        shape = curve.getShape()
        pm.parent(shape, node, s=True, r=True)
        pm.delete(curve)
        shapes.append(shape)
    return shapes


def removeShapes(node):
    """Remove the shape nodes from the given transform.

    Notes:
        Only works for meshes, curves, and nurbs surfaces.

    Args:
        node (pm.nt.Transform): PyMEL transform object.

    Returns:
        None
    """
    if not isinstance(node, pm.nt.Transform):
        raise TypeError('Expected a Transform node, got {0}'.format(type(node).__name__))
    for s in node.getShapes():
        if s.nodeType() in ('mesh', 'nurbsCurve', 'nurbsSurface'):
            pm.delete(s)


def replaceShapes(node, shapeData):
    """Replace the shapes on the given control node with the given shape data.

    Args:
        node (pm.nt.Transform): PyMEL transform object.
        shapeData (dict): Shape data for position, knots, degree, and periodic.

    Returns:
        None
    """
    if not isinstance(node, pm.nt.Transform):
        raise TypeError('Expected a Transform node, got {0}'.format(type(node).__name__))
    removeShapes(node)
    addShapes(node, shapeData)


def tagAsControl(node):
    """Add an attribute to the given node, this attribute uniquely identifies control objects.

    Args:
        node (str): Node name or PyMEL node object.

    Returns:
        None
    """
    if isinstance(node, basestring):
        node = pm.PyNode(node)

    if node.hasAttr('isControl'):
        return

    node.addAttr('isControl', at=bool, dv=True)
    node.isControl.setKeyable(False)
    node.showInChannelBox(False)
    node.setLocked(True)


def guessScale(ctl, node):
    """Approximate the scale for a given control by a given node, its parent and children.

    Args:
        ctl (pm.nt.Transform): PyMEL node object, of control to scale.
        node (pm.nt.Transform): PyMEL node object, of node to base scale from.

    Returns:
        float
    """
    lengths = []
    if isinstance(node, pm.nt.Joint):
        pStart = node.getTranslation(space='world')
        if node.getParent():
            pEnd = node.getParent().getTranslation(space='world')
            lengths.append((pEnd - pStart).length())
        elif node.getChildren():
            childLengths = []
            for child in node.getChildren():
                pEnd = child.getTranslation(space='world')
                childLengths.append((pEnd - pStart).length())
            lengths.append(sum(childLengths) / len(childLengths))
    elif node is not None:
        bb = node.boundingBox()
        lengths.append((bb[1] - bb[0]).length())

    if not len(lengths):
        lengths = [1.0]

    averageJointLengths = sum(lengths) / len(lengths)
    bb = ctl.boundingBox()
    componentSize = (bb[1] - bb[0]).length()
    scale = averageJointLengths / componentSize

    return (min(max(scale, 0.1), 100) + 1) / 2


def selectControlCVs(*controls):
    """Select control points for the given nodes, if no nodes are provided, uses current selection.

    Args:
        *controls: Nodes

    Returns:
        None
    """
    if not controls:
        controls = pm.selected()

    result = []
    for x in controls:
        shapes = x.getShapes()
        for sh in shapes:
            result.append(sh.cv[:])

    pm.select(result, r=True)


def createControlsFromSelection(shapeName):
    """Create new control objects from current selection.

    The selection is used to snap the controls to each selected
    object. If there is nothing selection, creates a new control at the origin.

    Args:
        shapeName (str): Name of a shape from `defaultControlShapes.json`.

    Returns:
        None
    """
    shapeData = getControlShape(shapeName)

    selection = pm.selected()

    if not selection:
        createControl(shapeData)
    else:
        for obj in selection:
            createControl(shapeData, obj)


def centerPivotToCVs():
    """Move the selected node's shape's control points to the location of the pivot position.

    This command offsets each control point of a curve by its transform's pivot location.

    Returns:
        None
    """
    for x in pm.selected():
        sumOfShapeCenters = pm.dt.Vector()

        shapes = x.getShapes()
        for sh in shapes:
            cvs = sh.cv[:]

            sumOfPositions = pm.dt.Vector()
            for cv in cvs:
                sumOfPositions += cv.getPosition('world')

            centerPoint = sumOfPositions / len(cvs)
            sumOfShapeCenters += centerPoint

            diff = x.getTranslation('world') - centerPoint
            for cv in cvs:
                cv.setPosition(pm.dt.Point(diff + cv.getPosition('world')), 'world')

            sh.updateCurve()

        shapesCenter = sumOfShapeCenters / len(shapes)
        x.setTranslation(shapesCenter, 'world')


def centerCVsToPivot():
    """Move the selected control object's control points to it's transform's pivot location.

    Returns:
        None
    """
    for x in pm.selected():
        shapes = x.getShapes()
        for sh in shapes:
            cvs = sh.cv[:]

            sumOfPositions = pm.dt.Vector()
            for cv in cvs:
                sumOfPositions += cv.getPosition('world')

            centerPoint = sumOfPositions / len(cvs)
            diff = x.getTranslation('world') - centerPoint
            for cv in cvs:
                cv.setPosition(pm.dt.Point(diff + cv.getPosition('world')), 'world')

            sh.updateCurve()


def get_shape(node, intermediate=False):
    """
    Get the shape node of a transform.
    This is useful if you don't want to have to check if a node is a shape node
    or transform.  You can pass in a shape node or transform and the function
    will return the shape node.

    Args:
        node: The name of the node.
        intermediate: True to get the intermediate shape.

    Returns: The name of the shape node.

    """
    returnShapes = []
    if cmds.nodeType(node) == 'transform' or 'joint':
        shapes = cmds.listRelatives(node, shapes=True, path=True)
        if not shapes:
            shapes = []
        for shape in shapes:
            is_intermediate = cmds.getAttr('%s.intermediateObject' % shape)
            if intermediate and is_intermediate and cmds.listConnections(shape, source=False):
                returnShapes.append(shape)
                # return shape
            elif not intermediate and not is_intermediate:
                returnShapes.append(shape)
                # return shape
        return returnShapes
        if shapes:
            return shapes[0]
    elif cmds.nodeType(node) in ['mesh', 'nurbsCurve', 'nurbsSurface']:
        is_intermediate = cmds.getAttr('%s.intermediateObject' % node)
        if is_intermediate and not intermediate:
            node = cmds.listRelatives(node, parent=True, path=True)[0]
            return get_shape(node)
        else:
            return node
    return None

def scaleControl(node, scaleVector):
    """
    Scale controlCurve by [x, y, z].
    Adjust controlCurve size of selected transform nodes.

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
        LOG.warning(node + ' does not exist.')
        return
    elif not (cmds.objectType(node, isType='transform') or cmds.objectType(node, isType='joint')):
        LOG.warning('Input node requires transform or joint type.')
        return
    elif len(scaleVector) != 3:
        LOG.warning('Input scaleVector requires a list of three.')
        return

    shapeList = get_shape(node)
    for shape in shapeList:
        cmds.select(cl=1)
        cmds.select(shape + '.cv[:]')
        cmds.scale(scaleVector[0], scaleVector[1], scaleVector[2], r=1, ocp=0)
    cmds.select(node)


def scaleUpSelected(scaleValue=1.1):
    sel = cmds.ls(selection=True)
    if sel:
        for ctl in sel:
            scaleControl(ctl, [scaleValue,scaleValue,scaleValue])
        cmds.select(sel)
        return True


def scaleDownSelected(scaleValue=.9):
    sel = cmds.ls(selection=True)
    if sel:
        for ctl in sel:
            scaleControl(ctl, [scaleValue,scaleValue,scaleValue])
        cmds.select(sel)
        return True


def rename_shapes(node):
    """Renames shape nodes under transform node"""
    shps = cmds.listRelatives(node, shapes=True)
    if shps:
        for shp in shps:
            cmds.rename(shp, '{}Shape#'.format(node))
