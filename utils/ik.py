import logging

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
from maya import cmds


def get_aim_axis(joint_name):
    """Returns the axis pointed down the chain as a string

    Args:
        joint_name:  Name of joint to check for primary axis

    Example:
        get_aim_axis('joint4')
        # Result: 'y' #
    """
    child_joint = cmds.listRelatives(joint_name, c=True)

    if not child_joint:
        LOG.exception('{0} does not have any children to check the aim axis'.format(joint_name))
        return False

    else:
        # Get translate values for child joint
        tx = cmds.getAttr('{}.translateX'.format(child_joint[0]))
        ty = cmds.getAttr('{}.translateY'.format(child_joint[0]))
        tz = cmds.getAttr('{}.translateZ'.format(child_joint[0]))

        # Absolute translate values (basically always gives you a positive value
        atx = abs(tx)
        aty = abs(ty)
        atz = abs(tz)

        # Max function returns the largest value of the input values
        axis_tmp_val = max(atx, aty)
        axis_val = max(axis_tmp_val, atz)

        axes = ['x', 'y', 'z']
        trans = [tx, ty, tz]
        abs_trans = [atx, aty, atz]

        # Loop through abs translate values -
        # compare max trans value with each trans axis value
        for i in range(len(abs_trans)):
            if axis_val == abs_trans[i]:
                # if our highest trans axis value matches the current trans value
                # then we've found our axis, next determine if that axis is
                # positive or negative by checking if it's less than 0.0
                axis_tmp = axes[i]
                if trans[i] < 0.0:
                    axis = ('-{}'.format(axis_tmp))
                else:
                    axis = axis_tmp
        return (axis)


def add_attribute_separator(object, attr_name):
    """Create a separator attribute on the specified control object

    Args:
        control: The control to add the separator attribute to
        attr: The separator attribute name

    Returns:

    Example:
        add_attribute_separator('Lf_arm_ctrl', '___')
    """
    # Check that object exists
    if not cmds.objExists(object):
        raise Exception('Control object {} does not exist!'.format(object))

    # Check if attribute exists
    if cmds.objExists('{}.{}'.format(object, attr_name)):
        raise Exception('Control attribute {}.{} already exists!'.format(object, attr_name))

    # Create attribute
    cmds.addAttr(object, ln=attr_name, at='enum', en=':-:')
    cmds.setAttr('{}.{}'.format(object, attr_name), cb=True)
    cmds.setAttr('{}.{}'.format(object, attr_name), l=True)

    # Return result
    return ('{}.{}'.format(object, attr_name))


def add_softIK(ik_handle, ik_ctl, base_name):
    """Adds softIK to ikHandle to help avoid "popping" behavior as
    joint chain straightens.

    Note:  This method effectively moves the IK end effector's pivot
    as the length between the first ik joint and the anim control increases
    towards fully straightened

    Args:
        ik_handle:  IK handle that the soft ik effect will be added
        ik_ctl:  The anim control the ik_handle is constrained to
        base_name:  Base naming convention that will be used for newly created nodes

    Example:
        add_softIK( 'ikHandle2', 'ik_ctl', 'lf_arm')
    """
    if cmds.objExists(ik_handle):
        # Get end effector node from ik_handle
        end_effector = cmds.listConnections('{}.endEffector'.format(ik_handle))[0]

        # Get list of joints controlled by ik_handle
        ik_joints = cmds.ikHandle(ik_handle, q=True, jointList=True)
        if len(ik_joints) != 2:
            LOG.error('IK handle does not control enough joints, make sure this is a two bone IK setup')
        else:
            ik_joints.append(cmds.listRelatives(ik_joints[1], children=True, type='joint')[0])
        LOG.debug('IK joint list: {}'.format(ik_joints))

        # Find the first joints aim axis (primary axis), handle if axis is negative as well
        aim_axis = get_aim_axis(ik_joints[0])
        aim_axis = aim_axis.capitalize()
        LOG.debug('IK joint aim axis: {}'.format(aim_axis))

        neg_axis = False
        if '-' in aim_axis:
            neg_axis = True
            aim_axis = aimAxis.replace('-', '')
            aim_axis = aimAxis.capitalize()

        # Get abs ik mid and tip joints translate values to find that bones length
        mid_trans_axis_val = abs(cmds.getAttr('{}.translate{}'.format(ik_joints[1], aim_axis)))
        tip_trans_axis_val = abs(cmds.getAttr('{}.translate{}'.format(ik_joints[2], aim_axis)))
        chain_length = mid_trans_axis_val + tip_trans_axis_val

        # Create distance setup to track distance from start joint to controller
        start_pos_tfm = cmds.createNode('transform', name='{}_startPos_tfm'.format(base_name))
        end_pos_tfm = cmds.createNode('transform', name='{}_endPos_tfm'.format(base_name))
        cmds.pointConstraint(ik_joints[0], start_pos_tfm)
        cmds.pointConstraint(ik_ctl, end_pos_tfm)
        dist_node = cmds.createNode('distanceBetween', name='{}_softIk_distance'.format(base_name))
        cmds.connectAttr('{}.translate'.format(start_pos_tfm), '{}.point1'.format(dist_node))
        cmds.connectAttr('{}.translate'.format(end_pos_tfm), '{}.point2'.format(dist_node))

        # Add softIK attrs to control - do attr names make sense here?
        add_attribute_separator(ik_ctl, '___')
        cmds.addAttr(ik_ctl, ln='soft_value', at="double", min=0.001, max=2, dv=0.001, k=True, hidden=False)
        cmds.addAttr(ik_ctl, ln='dist_value', at="double", dv=0, k=True, hidden=False)
        cmds.addAttr(ik_ctl, ln='softIk', at="double", min=0, max=20, dv=0, k=True)
        cmds.connectAttr('{}.distance'.format(dist_node), '{}.dist_value'.format(ik_ctl))

        soft_remap = cmds.createNode('remapValue', n='{}_soft_remapValue'.format(base_name))
        cmds.setAttr('{}.inputMin'.format(soft_remap), 0)
        cmds.setAttr('{}.inputMax'.format(soft_remap), 20)
        cmds.setAttr('{}.outputMin'.format(soft_remap), 0.001)
        cmds.setAttr('{}.outputMax'.format(soft_remap), 2)
        cmds.connectAttr('{}.softIk'.format(ik_ctl), '{}.inputValue'.format(soft_remap))
        cmds.connectAttr('{}.outValue'.format(soft_remap), '{}.soft_value'.format(ik_ctl))

        # ==========
        # Add Utility nodes

        # Plus Minus Average nodes
        len_minus_soft_pma = cmds.createNode('plusMinusAverage', n='{}_len_minus_soft_pma'.format(base_name))  # lspma
        chaindist_minus_lenminussoft_pma = cmds.createNode('plusMinusAverage',
                                                           n='{}_chaindist_minus_lenminussoft_pma'.format(
                                                               base_name))  # dslspma
        one_minus_pow = cmds.createNode('plusMinusAverage', n='{}_one_minus_pow_pma'.format(base_name))  # opwpma
        plus_len_minus_soft_pma = cmds.createNode('plusMinusAverage',
                                                  n='{}_plus_len_minus_soft_pma'.format(base_name))  # plpma
        chain_dist_diff_pma = cmds.createNode('plusMinusAverage', n='{}_chain_dist_diff_pma'.format(base_name))  # ddpma
        default_position_pma = cmds.createNode('plusMinusAverage', n='{}_default_pos_pma'.format(base_name))  # dppma

        # Multiply Divide nodes
        nxm_mdn = cmds.createNode('multiplyDivide', n='{}_negate_x_minus_mdn'.format(base_name))
        ds_mdn = cmds.createNode('multiplyDivide', n='{}_divBy_soft_mdn'.format(base_name))
        pow_mdn = cmds.createNode('multiplyDivide', n='{}_pow_mdn'.format(base_name))
        ts_mdn = cmds.createNode('multiplyDivide', n='{}_times_soft_mdn'.format(base_name))

        # Add Double Linear nodes
        ee_adl = cmds.createNode('addDoubleLinear', n='{}_endeffector_adl'.format(base_name))

        # Condition node
        len_minus_soft_cond = cmds.createNode('condition', n='{}_len_minus_soft_cdn'.format(base_name))

        if neg_axis:
            neg_mdl = cmds.createNode('multDoubleLinear', n='{}_negative_mdl'.format(base_name))
            cmds.setAttr('{}.input2'.format(neg_mdl), -1.0)

        # ==========
        # Set Utility node values
        cmds.setAttr('{}.operation'.format(len_minus_soft_pma), 2)
        cmds.setAttr('{}.operation'.format(chaindist_minus_lenminussoft_pma), 2)
        cmds.setAttr('{}.operation'.format(nxm_mdn), 1)
        cmds.setAttr('{}.operation'.format(ds_mdn), 2)
        cmds.setAttr('{}.operation'.format(pow_mdn), 3)
        cmds.setAttr('{}.operation'.format(one_minus_pow), 2)
        cmds.setAttr('{}.operation'.format(ts_mdn), 1)
        cmds.setAttr('{}.operation'.format(plus_len_minus_soft_pma), 1)
        cmds.setAttr('{}.operation'.format(len_minus_soft_cond), 5)
        cmds.setAttr('{}.operation'.format(chain_dist_diff_pma), 2)
        cmds.setAttr('{}.operation'.format(default_position_pma), 2)

        # ==========
        # Connect Utility nodes
        cmds.setAttr('{}.input1D[0]'.format(len_minus_soft_pma), chain_length)
        cmds.connectAttr('{}.soft_value'.format(ik_ctl), '{}.input1D[1]'.format(len_minus_soft_pma))
        cmds.connectAttr('{}.distance'.format(dist_node), '{}.input1D[0]'.format(chaindist_minus_lenminussoft_pma))
        cmds.connectAttr('{}.output1D'.format(len_minus_soft_pma),
                         '{}.input1D[1]'.format(chaindist_minus_lenminussoft_pma))
        cmds.connectAttr('{}.output1D'.format(chaindist_minus_lenminussoft_pma), '{}.input1X'.format(nxm_mdn))
        cmds.setAttr('{}.input2X'.format(nxm_mdn), -1)
        cmds.connectAttr('{}.outputX'.format(nxm_mdn), '{}.input1X'.format(ds_mdn))
        cmds.connectAttr('{}.soft_value'.format(ik_ctl), '{}.input2X'.format(ds_mdn))
        cmds.setAttr('{}.input1X'.format(pow_mdn), 2.718281828)
        cmds.connectAttr('{}.outputX'.format(ds_mdn), '{}.input2X'.format(pow_mdn))
        cmds.setAttr('{}.input1D[0]'.format(one_minus_pow), 1)
        cmds.connectAttr('{}.outputX'.format(pow_mdn), '{}.input1D[1]'.format(one_minus_pow))
        cmds.connectAttr('{}.output1D'.format(one_minus_pow), '{}.input1X'.format(ts_mdn))
        cmds.connectAttr('{}.soft_value'.format(ik_ctl), '{}.input2X'.format(ts_mdn))
        cmds.connectAttr('{}.outputX'.format(ts_mdn), '{}.input1D[0]'.format(plus_len_minus_soft_pma))
        cmds.connectAttr('{}.output1D'.format(len_minus_soft_pma), '{}.input1D[1]'.format(plus_len_minus_soft_pma))
        cmds.connectAttr('{}.output1D'.format(len_minus_soft_pma), '{}.firstTerm'.format(len_minus_soft_cond))
        cmds.connectAttr('{}.distance'.format(dist_node), '{}.secondTerm'.format(len_minus_soft_cond))
        cmds.connectAttr('{}.distance'.format(dist_node), '{}.colorIfFalseR'.format(len_minus_soft_cond))
        cmds.connectAttr('{}.output1D'.format(plus_len_minus_soft_pma), '{}.colorIfTrueR'.format(len_minus_soft_cond))
        cmds.connectAttr('{}.outColorR'.format(len_minus_soft_cond), '{}.input1D[0]'.format(chain_dist_diff_pma))
        cmds.connectAttr('{}.distance'.format(dist_node), '{}.input1D[1]'.format(chain_dist_diff_pma))

        cmds.setAttr('{}.input1D[0]'.format(default_position_pma), 0)
        cmds.connectAttr('{}.output1D'.format(chain_dist_diff_pma), '{}.input1D[1]'.format(default_position_pma))
        cmds.connectAttr('{}.output1D'.format(default_position_pma), '{}.input1'.format(ee_adl))
        cmds.setAttr('{}.input2'.format(ee_adl), tip_trans_axis_val)

        # Connect final result to end effector's aim_axis
        ee_connected = cmds.listConnections('{}.translate{}'.format(end_effector, aim_axis), source=True,
                                            destination=False, plugs=True)
        if ee_connected:
            cmds.disconnectAttr(ee_connected[0], '{}.translate{}'.format(end_effector, aim_axis))

        if neg_axis:
            cmds.connectAttr('{}.output'.format(ee_adl), '{}.input1'.format(neg_mdn))
            cmds.connectAttr('{}.output'.format(neg_mdn), '{}.translate{}'.format(end_effector, aim_axis))
        else:
            cmds.connectAttr('{}.output'.format(ee_adl), '{}.translate{}'.format(end_effector, aim_axis))

        cmds.select(ik_ctl)
        return ik_ctl

    else:
        LOG.error('IK handle {} does not exist in scene'.format(ik_handle))

