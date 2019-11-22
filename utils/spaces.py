"""

    Attach
        Find space constraint node
        Find space offset node
        Create parent constraint
        Get offset, switch constraint and set offset

"""
import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

from maya import cmds

'''
def get_parent_constraint(space_constraint_node):
    """Returns parent constraint node connected to input node"""
    return cmds.listConnections('{}.parentInverseMatrix'.format(space_constraint_node), s=False, d=True)

def has_space_setup():
    """Returns true if input node has necessary space transforms"""

def attach(source, target):
    """ 
    Create a parent constrain with  zero offset
    
    """
    # Get associated space nodes
    space_constraint = 'cn_mainArm_spaceConstrain'
    space_offset = 'cn_mainArm_spaceOffset'
    
    # Get current location in world space
    current_world_pos = cmds.xform(source, q=True, rp=True, ws=True) 
    current_world_rot = cmds.xform(source, q=True, ro=True, ws=True)
    
    # Get parent constraint
    
    # Get current parent constraint weight
    
    # Set target parent constraint weight
    
    # Set offset position and rotation to spaceOffset node
    
    
def _get_parent_constraint(obj):
    if REMOVE_CONTROL_SUFFIX:
        return _get_parent_handle(obj.replace(':', '_')) + PARENT_CONSTRAINT_SUFFIX
    else:
        return _get_parent_handle(obj) + PARENT_CONSTRAINT_SUFFIX


def _get_world_location(obj):
    
    return [cmds.xform(obj, q=True, rp=True, ws=True), cmds.xform(obj, q=True, ro=True, ws=True)]


def _set_world_location(obj, pos_rot):
    pos = pos_rot[0]
    rot = pos_rot[1]
    obj_piv = cmds.xform(obj, q=True, rp=True, ws=True)
    diff = (pos[0] - obj_piv[0], pos[1] - obj_piv[1], pos[2] - obj_piv[2])
    cmds.xform(obj, t=diff, r=True, ws=True)
    cmds.xform(obj, ro=rot, a=True, ws=True)

'''

# Attach animation control to an object
def attach(source, target):
    """

    attach( 'anim_ctl', 'spaceA')
    attach( 'anim_ctl', 'spaceB')
    """
    # Get space transforms
    space_constrain = get_message_attribute_connections(source, attrName="space_constraint")
    space_offset = get_message_attribute_connections(source, attrName="space_offset")

    if not space_constrain:
        LOG.error('There are no space transforms setup on {}'.format(source))
        return

    # Determine if there's an existing parent constrain on space_constrain node
    par_con = ""
    par_cons = get_parent_constraints(space_constrain[0])

    # Get world location of space offset
    space_offset_location = get_world_location(space_offset)

    # Time
    current_frame = cmds.currentTime(q=True)
    first_frame = cmds.playbackOptions(q=True, ast=True)

    # If there's an existing parent constraint
    if par_cons:
        LOG.info('Parent constraint exists')
        par_con = par_cons[0]
        # if the target is already active exit
        if target == get_active_constraint_target(par_con):
            LOG.error('{} is already active target for {}'.format(target, source))
            return

        target_list = cmds.parentConstraint(par_con, q=True, tl=True)
        print target_list

        # reset all targets
        for i in range(len(target_list)):
            cmds.setAttr('%s.w%d' % (par_con, i), 0.0)
            cmds.setKeyframe('%s.w%d' % (par_con, i), ott='step')

        # if the target is not present in the constraint then add it
        if target not in target_list:
            add_target_to_constraint(par_con, target)

            # set it to 0 in the first frame (since it's new), it's not valid if they are in the first frame
            if current_frame > first_frame:
                cmds.setKeyframe('%s.w%d' % (par_con, len(target_list)), ott='step', t=first_frame, v=0.0)

        # set it to 1 in the current frame
        target_id = cmds.parentConstraint(par_con, q=True, tl=True).index(target)
        cmds.setAttr('%s.w%d' % (par_con, target_id), 1.0)
        cmds.setKeyframe('%s.w%d' % (par_con, target_id), ott='step')
        print target_id

        # snap the position of the snap control on the previous position and set the keys of the snap control
        set_world_location(space_offset[0], space_offset_location)
        cmds.setKeyframe(space_offset[0], at=['translate', 'rotate'], ott='step')

    # else if there's not an existing parent constraint
    else:
        # Create constraint and set keyframe
        par_con = create_parent_constraint(space_constrain[0], target, '{}_parcon'.format(space_constrain[0]))
        cmds.setKeyframe(par_con, at='w0', ott='step')

        # Snap the position of the space offset transform and set keyframes
        set_world_location(space_offset[0], space_offset_location)
        cmds.setKeyframe(space_offset[0], at=['translate', 'rotate'], ott='step')

        # Set it to 0 on the first frame
        if current_frame > first_frame:
            cmds.setKeyframe(par_con, at='w0', ott='step', t=first_frame, v=0.0)
            cmds.setKeyframe(space_offset[0], at=['translate', 'rotate'], ott='step', t=first_frame, v=0.0)

    # set keyframes to green
    cmds.keyframe([space_offset[0], par_con], tds=True)

    # set the curve step
    cmds.keyTangent([space_offset[0], par_con], ott='step')

    return space_constrain


def get_obj_name(obj):
    idx = max(obj.rfind('|'), obj.rfind(':'))
    return obj[idx + 1:]


def add_target_to_constraint(cns, target):
    target_list = cmds.parentConstraint(cns, q=True, tl=True)
    count = len(target_list)
    cmds.addAttr(cns, sn='w%d' % count, ln='%sW%d' % (get_obj_name(target), count), dv=1.0, min=0.0, at='double',
                 k=True)
    cmds.setAttr('%s.w%d' % (cns, count), 0.0)

    cmds.connectAttr('%s.t' % target, '%s.tg[%d].tt' % (cns, count))
    cmds.connectAttr('%s.rp' % target, '%s.tg[%d].trp' % (cns, count))
    cmds.connectAttr('%s.rpt' % target, '%s.tg[%d].trt' % (cns, count))
    cmds.connectAttr('%s.r' % target, '%s.tg[%d].tr' % (cns, count))
    cmds.connectAttr('%s.ro' % target, '%s.tg[%d].tro' % (cns, count))
    cmds.connectAttr('%s.s' % target, '%s.tg[%d].ts' % (cns, count))
    cmds.connectAttr('%s.pm' % target, '%s.tg[%d].tpm' % (cns, count))

    cmds.connectAttr('%s.w%d' % (cns, count), '%s.tg[%d].tw' % (cns, count))


def get_world_location(node):
    """Returns two arrays for position and rotation"""
    return [cmds.xform(node, q=True, rp=True, ws=True), cmds.xform(node, q=True, ro=True, ws=True)]


def set_world_location(node, pos_rot):
    """Set position and rotation to input arrays"""
    pos = pos_rot[0]
    rot = pos_rot[1]
    obj_piv = cmds.xform(node, q=True, rp=True, ws=True)
    diff = (pos[0] - obj_piv[0], pos[1] - obj_piv[1], pos[2] - obj_piv[2])
    cmds.xform(node, t=diff, r=True, ws=True)
    cmds.xform(node, ro=rot, a=True, ws=True)


def get_parent_constraints(node):
    """Returns any connected parent constraints to node

    get_parent_constraints('anim_spaceConstrain')
    """
    if cmds.objExists(node):
        return cmds.listConnections('{}.parentInverseMatrix'.format(node), s=False, d=True, type='parentConstraint')


def get_active_constraint_target(constraint_name):
    """Returns the active target (the one with weight 1) for the specified constrain."""

    targets = cmds.parentConstraint(constraint_name, q=True, tl=True)
    active_target = None
    for i in range(len(targets)):
        if cmds.getAttr('%s.w%d' % (constraint_name, i)) == 1.0:
            active_target = targets[i]
            break
    return active_target


def create_parent_constraint(source, target, constraint_name):
    """Creates parent constraint"""

    ta = ('tx', 'ty', 'tz')
    ra = ('rx', 'ry', 'rz')

    # evaluate which are the attributes that should not be forced
    avail_attrs = cmds.listAttr(source, k=True, u=True, sn=True) or []
    skip_translate = [s[1] for s in ta if s not in avail_attrs]
    skip_rotate = [s[1] for s in ra if s not in avail_attrs]

    # if all listed launch the error
    if len(skip_translate) == 3 and len(skip_rotate) == 3:
        raise Exception('The attributes of the selected object are locked')

    # creates the constraint
    set_root_namespace()
    pc = cmds.parentConstraint(target, source, mo=False, n=constraint_name, w=1, st=skip_translate, sr=skip_rotate)[0]

    # reset the rest position
    cmds.setAttr('%s.restTranslate' % pc, 0.0, 0.0, 0.0)
    cmds.setAttr('%s.restRotate' % pc, 0.0, 0.0, 0.0)

    return constraint_name


def set_root_namespace():
    if cmds.namespaceInfo(cur=True) != ':':
        cmds.namespace(set=':')


# =================================================


def add_space_switch_transforms(transform_node=None):
    """Adds spaceConstraint and spaceOffset node above transform_node

    add_space_switch_transforms('cn_mainArm_ctl')
    """
    if not transform_node:
        if cmds.ls(selection=True):
            transform_node = cmds.ls(selection=True)[0]
        else:
            LOG.error('No node specified/selected to add space switch transforms to')
            return

    if cmds.objExists(transform_node):
        baseName = transform_node
        if '_ctl' in transform_node:
            baseName = transform_node.replace('_ctl', '')

        # Create spaceOffset and spaceConstrain nodes
        space_constraint = insert_as_parent(transform_node, name='{}_spaceConstrain'.format(baseName))
        space_offset = insert_as_parent(transform_node, name='{}_spaceOffset'.format(baseName))

        # Add message attribute connections so we can track these nodes in relation to original control node
        add_message_attribute(transform_node, [space_constraint], 'space_constraint')
        add_message_attribute(transform_node, [space_offset], 'space_offset')

        LOG.info('Successfully added space switch transforms to {}'.format(transform_node))
        return [space_constraint, space_offset]


def insert_as_parent(node, name=None, suffix=None, node_type='transform'):
    """Inserts a new node above specified node, requires passed in node to have a parent

    insert_as_parent('cn_mainArm_ctl', name='cn_mainArm_spaceOffset')
    """
    if cmds.objExists(node):
        # Find parent node
        parent = cmds.listRelatives(node, parent=True)

        # Create insert node
        if not name:
            name = '{}_{}'.format(node, suffix)
        insert_transform = cmds.createNode(node_type, name=name, parent=parent[0])

        # Match new insert node's position to original node
        match(insert_transform, node)

        # Parent original node under new insert node
        cmds.parent(node, insert_transform)

        return insert_transform

    else:
        LOG.error('{} does not exist!'.format(node))
        return


def match(transform, target):
    """Match transform to target transformation"""
    # Get target matrix
    targetMat = cmds.xform(target, q=True, ws=True, matrix=True)

    # Set source matrix
    cmds.xform(transform, ws=True, matrix=targetMat)


def add_message_attribute(src, tgts, attrName):
    """Adds message connection from src to tgts

    Args:
        src:  Object message attribute in added to
        tgts: List of objects src message attribute gets connected to
        attrName:  Name of the message attribute

    Usage:
        addMessageAttribute("box_fk_ctrl", ["box_pivot_ctl"], attrName="pivot_node")
    """
    try:
        if not cmds.attributeQuery(attrName, exists=True, node=src):
            cmds.addAttr(src, sn=attrName, at='message', m=True)

        i = 0
        while i < len(tgts):
            idx = get_next_free_multi_index("{}.{}".format(src, attrName), i)
            cmds.connectAttr("%s.message" % (tgts[i]), "%s.%s[%s]" % (src, attrName, str(idx)), f=True)
            i = i + 1

    except RuntimeError:
        LOG.error("Failed to create message attr connections")
        raise


def get_message_attribute_connections(src, attrName):
    """Returns a list of connection to srcObj message attr

    Args:
        src: Object with message attribute
        attrName:  The name of the message attribute to get connections from

    Usage:
        getMessageAttributeConnections("box_fk_ctrl", attrName="pivot_node")
    """
    try:
        if cmds.attributeQuery(attrName, exists=True, node=src):
            tgts = cmds.listConnections("%s.%s" % (src, attrName))
            return tgts
    except RuntimeError:
        LOG.error("Message attr %s cannot be found on %s" % (attrName, src))
        raise


def get_next_free_multi_index(attr_name, start_index):
    '''Find the next unconnected multi index starting at the passed in index.'''
    # assume a max of 10 million connections
    while start_index < 10000000:
        if len(cmds.connectionInfo('{}[{}]'.format(attr_name, start_index), sfd=True) or []) == 0:
            return start_index
        start_index += 1

    # No connections means the first index is available
    return 0

