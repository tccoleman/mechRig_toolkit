import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

from maya import cmds

def lock_unlock_channels(lock=True, attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']):
    """Locks/Unlocks all default channles on selected"""
    selection = cmds.ls(selection=True)
    if selection:

        for node in selection:
            for attr in attrs:
                if lock:
                    cmds.setAttr('{}.{}'.format(node, attr), lock=True, keyable=False)
                else:
                    cmds.setAttr('{}.{}'.format(node, attr), lock=False, keyable=True)


def match(source, target):
    """Match source object to target

    example:
        match('locator1', 'locator2')
    """
    # Check that source and target objects exist
    if not cmds.objExists(source):
        raise Exception('Source object {} does not exist!'.format(source))

    if not cmds.objExists(target):
        raise Exception('Target object {} does not exist!'.format(target))

    # Get target matrix
    targetMat = cmds.xform(target, q=True, ws=True, matrix=True)

    # Set source matrix
    cmds.xform(source, ws=True, matrix=targetMat)


def create_category(top_node, category_name):
    """Creates category display attr on top_node connected to a create category transform

    create_category('rig_topnode', 'rig')
    """
    if cmds.objExists(top_node):

        if not cmds.objExists(category_name):

            cat_node = cmds.createNode('transform', name=category_name)
            cmds.parent(cat_node, top_node)
            cmds.addAttr(top_node, longName=category_name, at='enum', en="off:on:reference:")
            cmds.setAttr('{}.{}'.format(top_node, category_name), lock=False, keyable=True)
            cmds.connectAttr('{}.{}'.format(top_node, category_name), '{}.visibility'.format(category_name))

            # Create category condition node and connect category attribute to it
            cond_node = cmds.createNode('condition', name='{}_{}_cnd'.format(top_node, category_name))
            cmds.connectAttr('{}.{}'.format(top_node, category_name), '{}.firstTerm'.format(cond_node))
            cmds.setAttr('{}.secondTerm'.format(cond_node), 2)
            cmds.setAttr('{}.operation'.format(cond_node), 0)
            cmds.setAttr('{}.colorIfTrueR'.format(cond_node), 2)
            cmds.setAttr('{}.colorIfFalseR'.format(cond_node), 0)

            # Connect output of condition node to the display overrides of the category node
            cmds.connectAttr('{}.outColorR'.format(cond_node),
                             '{}.drawOverride.overrideDisplayType'.format(category_name))
            cmds.setAttr('{}.overrideEnabled'.format(category_name), 1)
            cmds.setAttr('{}.overrideEnabled'.format(category_name), lock=True)
            cmds.setAttr('{}.drawOverride.overrideDisplayType'.format(category_name), lock=True)

            # Set display to "on" by default and lock/hide all other attrs
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']:
                cmds.setAttr('{}.{}'.format(category_name, attr), lock=True, keyable=False)
            cmds.setAttr('{}.{}'.format(top_node, category_name), 1)

            cmds.select(category_name)
            LOG.info('Created category node/attr {} on {}'.format(category_name, top_node))

            return category_name

        else:
            LOG.error('{} already exists'.format(category_name))
            return
    else:
        LOG.error('{} does not exist'.format(top_node))
        return


"""
* Because the anim control curve shapes have "override enabled", it causes an issue with our "rig" vis switch.
The vis switch controls the overrideDisplayType of the "rig" node.  However, since each control curve shape in 
the rig has "overrideEnabled" turned on, it overrides what the overrideDisplay type occuring on the "rig" node.

To fix this, we need to connect the output of the vis switch's rig attr to the overrideDisplayType of each anim
control curve.
"""

def connect_controls_to_overrideDisplayType(driver_node='rig', control_parent='rig', control_suffix='_ctl'):
    """ Connects control shapes nodes to driver node's overrideDisplayType attribute

        Example:
            connect_controls_to_overrideDisplayType()
    """
    node_list = cmds.listRelatives(control_parent, ad=True)
    if node_list:
        for node in node_list:
            if control_suffix in node:
                if 'nurbsCurve' in cmds.nodeType(node):
                    try:
                        cmds.connectAttr('{}.drawOverride.overrideDisplayType'.format(driver_node),
                                         '{}.drawOverride.overrideDisplayType'.format(node))
                        LOG.info('Fixed control curve override display on {}'.format(node))
                    except:
                        pass