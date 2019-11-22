import logging

import pymel.core as pm


LOG = logging.getLogger(__name__)


def groupWithTransform(node, name=None):
    """Create a transform node, match it to the input node, and parent the input node to the new transform.

    Args:
        node: Transform to receive the offset transform.
        name: Base name to give the new offset transform node.

    Returns:
        pm.PyNode
    """
    if name is None:
        name = '{0}_zero'.format(node.nodeName())

    offset = pm.createNode('transform', n=name)
    matchTRS(node, offset)
    offset.setParent(node.getParent())
    node.setParent(offset)

    return offset


def matchTRS(source, target, translate=True, rotate=True, scale=True):
    """Match a object to another's world space transforms.

    Args:
        source: Leader that `target` should match.
        target: Follower that will match `source`.

    Returns:
        None
    """
    if isinstance(source, basestring):
        source = pm.PyNode(source)

    if isinstance(target, basestring):
        source = pm.PyNode(target)

    if translate:
        target.setTranslation(source.getTranslation('world'), 'world')
    if rotate:
        target.setRotation(source.getRotation('world'), 'world')
    if scale:
        target.scale.set(source.scale.get())


def hideChannelBoxInfo(*nodes):
    """Clean up channel box by hiding inputs, outputs, and shape nodes.

    Args:
        *nodes: Names of nodes to clean up.

    Returns:
        None
    """
    nodes = [pm.PyNode(x) for x in nodes]
    for node in nodes:
        node.ihi.set(0)
        node.drawOverride.set(l=1)
        for shape in node.getShapes():
            shape.ihi.set(0)
        for con in shape.listConnections():
            for conNode in con.listFuture():
                if not isinstance(conNode, pm.nt.SkinCluster):
                    conNode.ihi.set(0)


def rotateSelectedNodeComponents(rotation):
    """Rotates the selected node's shape nodes by the input rotation in object space.

    Args:
        rotation (list): x, y, z values in degrees

    Returns:
        None
    """
    for node in pm.selected():
        for shape in node.getShapes():
            if isinstance(shape, pm.nt.Mesh):
                pm.rotate(shape.vtx, rotation, os=1)
            elif isinstance(shape, pm.nt.NurbsCurve):
                pm.rotate(shape.cv, rotation, os=1)