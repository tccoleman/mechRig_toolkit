import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

from maya import cmds


def match_selection():
    """Matches first selected object(s) to last"""
    selection = cmds.ls(selection=True)

    if selection:
        if len(selection) > 1:
            last_obj = selection[-1]
            selection.remove(last_obj)
            for obj in selection:
                match(obj, last_obj)
                LOG.info('Matched {} to {}'.format(obj, last_obj))
    else:
        LOG.error('Nothing selected, select at least source and target objects')


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


def create_pole_vector_from_selection():
    """Select at least one IK handle and another transform to add as pole vector constraint"""
    selection = cmds.ls(selection=True)

    if len(selection) == 2:
        ik_handle = None
        pv_ctl = None
        if cmds.nodeType(selection[0]) == 'ikHandle':
            ik_handle = selection[0]
            pv_ctl = selection[1]
        elif cmds.nodeType(selection[1]) == 'ikHandle':
            ik_handle = selection[1]
            pv_ctl = selection[0]
        else:
            LOG.error('At least one object must be an IK handle')
            return

        create_pole_vector(pv_ctl, ik_handle)
        LOG.info('Created pole vector constraint from {} to {}'.format(pv_ctl, ik_handle))
        return True


def create_pole_vector(pv_ctl, ik_handle):
    """Positions pv_ctl and creates pole vector constraint for ik_handle to prevent any joint rotation

    Arguments:
        pv_ctl:    Transform to use as pole vector control

        ik_handle: IK handle to add pole vector constrain to

    Example:
        create_pole_vector( 'locator2', 'ikHandle1' )
    """
    # Find the start joint from querying ik handle
    start_joint = cmds.ikHandle(ik_handle, q=True, startJoint=True)
    mid_joint = cmds.listRelatives(start_joint, children=True, type='joint')

    # Constrain the pole vector control transform between start joint and ik_handle
    cmds.delete(cmds.pointConstraint(start_joint, ik_handle, pv_ctl))

    # Aim pole vector control to mid_joint - Aim X-axis
    cmds.delete(cmds.aimConstraint(mid_joint[0], pv_ctl, aim=[1, 0, 0], u=[0, 0, 1], wut='none'))

    # Find distance from pole vector control to mid_joint
    pv_pos = cmds.xform(pv_ctl, q=True, ws=True, t=True)
    mid_pos = cmds.xform(mid_joint[0], q=True, ws=True, t=True)
    pv_dist = (pv_pos[0] - mid_pos[0], pv_pos[1] - mid_pos[1], pv_pos[2] - mid_pos[2])

    # Add offset away from mid position
    # - Moves pole vector to mid position PLUS original distance from initial position to mid position
    pv_pos_off = (mid_pos[0] - pv_dist[0], mid_pos[1] - pv_dist[1], mid_pos[2] - pv_dist[2])
    cmds.xform(pv_ctl, t=pv_pos_off)

    # Add group node above pole vector control to zero it out
    pv_grp = cmds.duplicate(pv_ctl, po=True, name='{}_grp'.format(pv_ctl))[0]
    cmds.parent(pv_ctl, pv_grp)

    # Create pole vector constraint
    cmds.poleVectorConstraint(pv_ctl, ik_handle)

    return pv_pos_off


def create_category_ui():
    """User prompted to enter category attr name to add to selected"""
    selection = cmds.ls(selection=True)

    if selection:
        result = cmds.promptDialog(
            title='Add category',
            message='Enter Category Name:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel')

        if result == 'OK':
            cat_name = cmds.promptDialog(query=True, text=True)
            create_category(selection[0], cat_name)
    else:
        LOG.error('Please select at least one object to add category attribute to!')


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
            cond_node = cmds.createNode('condition', name='{}_{}_cond'.format(top_node, category_name))
            cmds.connectAttr('{}.{}'.format(top_node, category_name), '{}.firstTerm'.format(cond_node))
            cmds.setAttr('{}.secondTerm'.format(cond_node), 2)
            cmds.setAttr('{}.operation'.format(cond_node), 0)
            cmds.setAttr('{}.colorIfTrueR'.format(cond_node), 2)
            cmds.setAttr('{}.colorIfTrueR'.format(cond_node), 0)

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
            return True

        else:
            LOG.error('{} already exists'.format(category_name))
            return
    else:
        LOG.error('{} does not exist'.format(top_node))
        return


def add_transforms_selected():
    """Adds transforms to selected"""
    selection = cmds.ls(selection=True)

    if selection:
        add_transforms(selection)
        cmds.select(selection)
        return True
    else:
        LOG.error("No transform(s) selected, select at least one transform and try again...")
        return


def add_transforms(transform_list, search='_ctl', add_transforms=['_grp', '_off']):
    """Adds transforms on top of selected transform

    Arguments:
        search:         string to search for in selected transform to replace

        add_transforms: list of suffixes for each transform to create
                        (more can be added as needed)
    """
    for tfm in transform_list:
        if cmds.nodeType(tfm) == 'transform':
            created_tfms = list()
            for i in range(0, len(add_transforms)):
                add_tfm = cmds.duplicate(tfm, po=True, name=tfm.replace(search, add_transforms[i]))[0]
                created_tfms.append(add_tfm)
                if i:
                    cmds.parent(add_tfm, created_tfms[i - 1])
            cmds.parent(tfm, created_tfms[-1])
            #print ', '.join(created_tfms)
            #print ', '.join(map(str, created_tfms))
            LOG.info('Added transforms {} to {}'.format(', '.join(map(str, created_tfms)), tfm))

