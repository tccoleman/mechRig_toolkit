"""
joints.py

Various functions for creating and editing joints and their axis.

    from mechRig_toolkit.builds import Cambot_rig
    reload(Cambot_rig)# Run this to pick up any changes made
    Cambot_rig.build.run()

"""

import logging

from maya import cmds

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def orientJoint(joints, aimAxis, upAxis, worldUpAxis):
    """Orient joints.

    Adjust joint orientation of selected joints by a certain degree.

    Args:
        joints: List of joints to orient.
        aimAxis: Array(x, y, z) of what axis of joint does aim.
        upAxis: Array(x, y, z) of what axis of joint does up.
        worldUpAxis: World axis used for up direction.
    Returns:
        None.
    Raises:
        Logs warning if nothing is selected.
        Logs warning if axis input is NOT xyz.
        Logs warning if operator input is NOT +-.
    """
    for i in xrange(len(joints)):
        # Find unparent children
        children = cmds.listRelatives(joints[i], children=1, pa=1, type="transform")
        if children and (len(children) > 0):
            # Unparent and get names of the objects(possibly renamed)
            children = cmds.parent(children, w=1)

        # Find parent
        parent = cmds.listRelatives(joints[i], pa=1, parent=1)
        if parent:
            parent = parent[0]

        # If joints[i] has a child joint, aim to that
        aimTarget = ""
        if children:
            for child in children:
                if cmds.objectType(child, isType="joint"):
                    aimTarget = child
                    break

        if aimTarget != "":
            aCons = cmds.aimConstraint(
                aimTarget,
                joints[i],
                aim=aimAxis,
                upVector=upAxis,
                worldUpVector=worldUpAxis,
                worldUpType="vector",
            )
            cmds.delete(aCons)

        elif parent:
            # If there is no target, dup orientation of parent
            oCons = cmds.orientConstraint(parent, joints[i])
            cmds.delete(oCons)

        cmds.joint(joints[i], edit=True, zso=1)
        cmds.makeIdentity(joints[i], apply=1, r=True)

        if children and (len(children) > 0):
            cmds.parent(children, joints[i])


def orientTo():
    """Match specified joint orientation to a target transform.

    Select one source joint and one or more target joints.

    Args:
    Returns:
        None.
    Raises:
        Logs warning if less than 2 objects are selected.
        Logs warning if selections contain non-joint type.
    """
    sel = cmds.ls(sl=1)
    if len(sel) < 2:
        log.warning("Please select one source joint and one or more target joints.")
        return

    for jnt in sel:
        if not cmds.objectType(jnt, isType="joint"):
            log.warning("Please select joints only.")

    for i in xrange(1, len(sel)):
        # Find unparent children
        children = cmds.listRelatives(sel[i], children=1, type="transform")
        if children and (len(children) > 0):
            # Unparent and get names of the objects(possibly renamed)
            children = cmds.parent(children, w=1)

        oCons = cmds.orientConstraint(sel[0], sel[i])
        cmds.delete(oCons)

        cmds.joint(sel[i], edit=True, zso=1)
        cmds.makeIdentity(sel[i], apply=1, r=True)

        if children and (len(children) > 0):
            cmds.parent(children, sel[i])


def planarOrient(joints, aimAxis, upAxis):
    """Adjust the joint orientation of three joints to their invisible plane.

    Args:
        joints: List of 3 joints.
        aimAxis: Array(x, y, z) of what axis of joint does aim.
        upAxis: Array(x, y, z) of what axis of joint does up.
        crossVector: World axis used for up direction.
    Returns:
        None.
    Raises:
        Logs warning if the length of joints is not 3.
        Logs warning if joints contain non-joint type.
    """
    if len(joints) != 3:
        log.warning("Please select 3 joints.")
        return

    for jnt in joints:
        if not cmds.objectType(jnt, isType="joint"):
            log.warning("Please select joints only.")

    jnt1 = cmds.xform(joints[0], ws=1, t=1, q=1)
    jnt2 = cmds.xform(joints[1], ws=1, t=1, q=1)
    jnt3 = cmds.xform(joints[2], ws=1, t=1, q=1)

    vector1 = [jnt2[0] - jnt1[0], jnt2[1] - jnt1[1], jnt2[2] - jnt1[2]]
    vector2 = [jnt3[0] - jnt2[0], jnt3[1] - jnt2[1], jnt3[2] - jnt2[2]]
    crossVector = cross(vector1, vector2)

    orientJoint(joints, aimAxis, upAxis, crossVector)


def cross(a, b):
    """
    Cross product.

    Args:
        a: Vector a.
        b: Vector b.

    Returns: Cross product of a and b.

    """
    c = [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]

    return c


def duplicate_joint_chain(source_joint, search="_jnt", replace="_ik"):
    """Duplicates full skeleton chain from source_joint

    duplicate_joint_chain('rt_frontShoulder_jnt', search='_jnt', replace='_ik')
    """
    dupe_chain = cmds.duplicate(
        source_joint, name=source_joint.replace(search, replace)
    )
    dupe_child = cmds.listRelatives(dupe_chain[0], ad=True, f=True)
    dupe_child.sort(reverse=True)
    for jnt in dupe_child:
        cmds.rename(jnt, jnt.split("|")[-1].replace(search, replace))

    # Re-list new joint chain to return cleaner list of the new joints
    new_chain = cmds.listRelatives(dupe_chain[0], ad=True)
    new_chain.sort(reverse=True)
    new_chain.insert(0, dupe_chain[0])

    return new_chain
