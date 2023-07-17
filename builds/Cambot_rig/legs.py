"""
    Connect ik legs to skin legs
    Cleanup/restrict channels on controls and nodes

"""
import logging

from maya import cmds

from mechRig_toolkit.utils import utility as util
from mechRig_toolkit.utils import joints as jnt
from mechRig_toolkit.utils import ik

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# NODE NAMING VARIABLES
MASTER_OFFSET = "cn_masterOffset_ctl"
COG = "cn_cog_ctl"

# SUFFIX VARIABLES
GRP = "_grp"
OFF = "_off"
CTL = "_ctl"


def rig_pistons():
    """Rig all Cambot pistons"""
    piston_up = piston_setup(
        "lf_legFront",
        "lf_legFrontLowerPiston_jnt",
        "lf_legFrontUpperPiston_jnt",
        aim=[0, 1, 0],
        up=[0, 0, 1],
    )
    cmds.parent(piston_up[0], "lf_legFrontLower_ikj")
    cmds.parent(piston_up[1], "lf_legFrontUpper_ikj")

    piston_up = piston_setup(
        "rt_legFront",
        "rt_legFrontLowerPiston_jnt",
        "rt_legFrontUpperPiston_jnt",
        aim=[0, -1, 0],
        up=[0, 0, -1],
    )
    cmds.parent(piston_up[0], "rt_legFrontLower_ikj")
    cmds.parent(piston_up[1], "rt_legFrontUpper_ikj")

    piston_up = piston_setup(
        "lf_legRear",
        "lf_legRearLowerPiston_jnt",
        "lf_legRearUpperPiston_jnt",
        aim=[0, -1, 0],
        up=[0, 0, -1],
    )
    cmds.parent(piston_up[0], "lf_legRearLower_ikj")
    cmds.parent(piston_up[1], "lf_legRearUpper_ikj")

    piston_up = piston_setup(
        "rt_legRear",
        "rt_legRearLowerPiston_jnt",
        "rt_legRearUpperPiston_jnt",
        aim=[0, 1, 0],
        up=[0, 0, 1],
    )
    cmds.parent(piston_up[0], "rt_legRearLower_ikj")
    cmds.parent(piston_up[1], "rt_legRearUpper_ikj")


def rig_legs():
    """Rig all Cambot legs"""
    sides = ["lf", "rt"]
    dirs = ["Front", "Rear"]

    for side in sides:
        for dir in dirs:
            shoulder_setup(
                "{}_shoulder{}_ctl".format(side, dir),
                "{}_shoulder{}_jnt".format(side, dir),
            )

            leg_joints = [
                "{}_shoulder{}_jnt".format(side, dir),
                "{}_leg{}Upper_jnt".format(side, dir),
                "{}_leg{}Lower_jnt".format(side, dir),
                "{}_leg{}Shin_jnt".format(side, dir),
                "{}_leg{}ToeTip_jnt".format(side, dir),
            ]

            leg_setup(
                "{}_leg{}".format(side, dir),
                leg_joints,
                "{}_leg{}_ctl".format(side, dir),
                shin_poleVectorTwist=90,
            )

            connect_leg_to_shoulder(
                "{}_leg{}".format(side, dir),
                "{}_leg{}_ctl".format(side, dir),
                "{}_shoulder{}_ctl".format(side, dir),
                "{}_shoulder{}_ikj".format(side, dir),
            )

            connect_leg_to_body(
                "{}_leg{}".format(side, dir),
                "{}_leg{}_ctl".format(side, dir),
                "cn_cog_ctl",
            )

            orient_constrain_chain(
                leg_joints, source_suffix="_jnt", target_suffix="_ikj"
            )

            cmds.hide("{}_shoulder{}_ikj".format(side, dir))

            # Add leg softIK
            ik.add_softIK(
                "{}_leg{}Upper_ikh".format(side, dir),
                "{}_leg{}SoftIK_loc".format(side, dir),
                "{}_leg{}".format(side, dir),
            )
            cmds.setAttr("{}_leg{}SoftIK_loc.softIk".format(side, dir), 10)

            log.info(
                "Successfully rigged leg:  {}".format("{}_leg{}".format(side, dir))
            )

    # Set shin ik twists to keep shin joints zeroed
    cmds.setAttr("lf_legFrontLower_ikh.twist", 90)
    cmds.setAttr("lf_legRearLower_ikh.twist", 180)
    cmds.setAttr("rt_legRearLower_ikh.twist", 180)
    cmds.setAttr("rt_legFrontLower_ikh.twist", 180)


def leg_shoulder_setup(
    base_name,
    shoulder_control,
    shoulder_joint,
    foot_control,
    side="lf",
    foot_pivots=[0.5, -0.5],
    shin_poleVectorTwist=180,
):
    shoulder_setup(shoulder_control, shoulder_joint)

    ik_jnt = leg_setup(
        base_name,
        leg_joints,
        foot_control,
        side=side,
        foot_pivots=foot_pivots,
        shin_poleVectorTwist=shin_poleVectorTwist,
    )

    connect_leg_to_shoulder(base_name, leg_control, shoulder_control, ik_jnt)

    connect_leg_to_body(base_name, leg_control, COG)


def shoulder_setup(shoulder_control, shoulder_joint):
    """Constrains, parents and sets channels for shoulder rig

    shoulder_setup('rt_shoulderFront_ctl', 'rt_frontShoulder_jnt')
    """
    try:
        cmds.parentConstraint(
            COG, shoulder_control.replace(CTL, GRP), maintainOffset=True
        )
        cmds.parent(shoulder_control.replace(CTL, GRP), MASTER_OFFSET)

        log.info(
            "Successfully rigged shoulder: {} and {}".format(
                shoulder_control, shoulder_joint
            )
        )

    except:
        raise Exception(
            "Error creating shoulder setup for {} and {}".format(
                shoulder_control, shoulder_joint
            )
        )


def leg_setup(
    base_name,
    leg_joints,
    foot_control,
    side="lf",
    foot_pivots=[0.5, -0.5],
    shin_poleVectorTwist=180,
):
    """
    leg_joints = ['lf_frontShoulder_jnt', 'lf_frontUpperLeg_jnt', 'lf_frontLowerLeg_jnt', 'lf_frontShin_jnt', 'lf_frontToeTip_jnt']
    leg_setup('lf_legFront', leg_joints, 'lf_legFront_ctl', shin_poleVectorTwist=90)
    """
    dir = 1
    leg_pos = cmds.xform(leg_joints[0], q=True, ws=True, t=True)
    if leg_pos[2] < 0:
        dir = -1

    # Create IK joint chain
    ik_jnts = jnt.duplicate_joint_chain(leg_joints[0], search="_jnt", replace="_ikj")

    # Create Leg IK and Pole Vector
    leg_ik = cmds.ikHandle(
        startJoint=leg_joints[1].replace("_jnt", "_ikj"),
        ee=leg_joints[3].replace("_jnt", "_ikj"),
        name="{}Upper_ikh".format(base_name),
        solver="ikRPsolver",
    )
    leg_pv = cmds.spaceLocator(name="{}UpperPV_ctl".format(base_name))[0]
    ik.create_pole_vector(leg_pv, leg_ik[0])

    # Create Shin IK and Pole Vector
    shin_ik = cmds.ikHandle(
        startJoint=leg_joints[3].replace("_jnt", "_ikj"),
        ee=leg_joints[4].replace("_jnt", "_ikj"),
        name="{}Lower_ikh".format(base_name),
        solver="ikRPsolver",
    )
    shin_pv = cmds.spaceLocator(name="{}LowerPV_ctl".format(base_name))[0]
    util.match(shin_pv, leg_joints[3].replace("_jnt", "_ikj"))
    cmds.parent(shin_pv, leg_joints[3].replace("_jnt", "_ikj"))
    cmds.select(shin_pv)
    cmds.move(0, 0, (10 * dir), relative=True)
    cmds.parent(shin_pv, world=True)
    cmds.poleVectorConstraint(shin_pv, shin_ik[0])[0]
    cmds.setAttr("{}.twist".format(shin_ik[0]), shin_poleVectorTwist)

    # Foot Pivots
    foot_piv_grp = cmds.duplicate(
        foot_control, parentOnly=True, name=foot_control.replace(CTL, "Pivot_grp")
    )[0]
    foot_piv_front = cmds.duplicate(
        foot_control, parentOnly=True, name=foot_control.replace(CTL, "FrontPivot_grp")
    )[0]
    foot_piv_rear = cmds.duplicate(
        foot_control, parentOnly=True, name=foot_control.replace(CTL, "RearPivot_grp")
    )[0]
    cmds.setAttr("{}.translateZ".format(foot_piv_front), foot_pivots[0])
    cmds.setAttr("{}.translateZ".format(foot_piv_rear), foot_pivots[1])
    cmds.pointConstraint(foot_control, foot_piv_grp)
    cmds.parent(foot_piv_front, foot_piv_grp)
    cmds.parent(foot_piv_rear, foot_piv_front)

    cmds.parent(
        leg_ik[0], leg_pv.replace("_ctl", "_grp"), shin_ik[0], shin_pv, foot_piv_rear
    )
    cmds.hide(foot_piv_rear)

    # Foot Pivot Rotation Limits
    cmds.connectAttr(
        "{}.rotateX".format(foot_control), "{}.rotateX".format(foot_piv_front)
    )
    cmds.connectAttr(
        "{}.rotateX".format(foot_control), "{}.rotateX".format(foot_piv_rear)
    )
    cmds.transformLimits(foot_piv_front, rx=[0, 45], erx=[1, 0])
    cmds.transformLimits(foot_piv_rear, rx=[-45, 0], erx=[0, 1])

    return ik_jnts[0]


def connect_leg_to_shoulder(base_name, leg_control, shoulder_control, leg_ik_joint):
    """Connects leg rig hierarchy to shoulder control

    connect_leg_to_shoulder('lf_legFront', 'lf_legFront_ctl', 'lf_shoulderFront_ctl', 'lf_frontShoulder_ikj')
    """
    # Duplicate shoulder control to use as pivot for leg control
    shoulder_leg_pivot = cmds.duplicate(
        shoulder_control, parentOnly=True, name="{}ShldrRot_off".format(base_name)
    )[0]
    leg_zero_pivot = cmds.duplicate(
        leg_control, parentOnly=True, name=leg_control.replace(CTL, "_zro")
    )[0]

    cmds.parent(shoulder_leg_pivot, leg_control.replace(CTL, GRP))
    cmds.parent(leg_zero_pivot, shoulder_leg_pivot)
    cmds.parent(leg_control.replace(CTL, OFF), leg_zero_pivot)

    cmds.parent(leg_ik_joint, shoulder_control)

    cmds.connectAttr(
        "{}.rotateY".format(shoulder_control), "{}.rotateY".format(shoulder_leg_pivot)
    )

    return shoulder_leg_pivot


def connect_leg_to_body(base_name, leg_control, body_control):
    """Connects leg rig hierarchy to body

    connect_leg_to_body('lf_legFront', 'lf_legFront_ctl', 'cn_cog_ctl')
    """
    leg_body_pivot = cmds.duplicate(
        body_control, parentOnly=True, name="{}BodyFollow_grp".format(base_name)
    )[0]
    leg_grp = leg_control.replace(CTL, GRP)
    leg_child = cmds.listRelatives(leg_grp, children=True)
    cmds.parent(leg_body_pivot, leg_grp)

    if leg_child:
        cmds.parent(leg_child, leg_body_pivot)
    cmds.parentConstraint(
        body_control,
        leg_body_pivot,
        skipTranslate=["y", "z"],
        skipRotate=["x"],
        mo=True,
    )

    cmds.parent(leg_grp, MASTER_OFFSET)


def piston_setup(base_name, pistonA, pistonB, aim=[0, 1, 0], up=[0, 0, 1]):
    """Creates aim constraint piston rig

    piston_setup('lf_legFront', 'lf_legFrontLowerPiston_jnt', 'lf_legFrontUpperPiston_jnt', aim=[0,1,0], up=[0,0,1])
    """
    # Create up vectors
    pistonA_up = cmds.spaceLocator(name="{}_up".format(pistonA))[0]
    cmds.parent(pistonA_up, pistonA)
    cmds.setAttr("{}.translate".format(pistonA_up), *up)
    cmds.setAttr("{}.rotate".format(pistonA_up), 0, 0, 0)
    cmds.parent(pistonA_up, world=True)

    pistonB_up = cmds.spaceLocator(name="{}_up".format(pistonB))[0]
    cmds.parent(pistonB_up, pistonB)
    cmds.setAttr("{}.translate".format(pistonB_up), *up)
    cmds.setAttr("{}.rotate".format(pistonB_up), 0, 0, 0)
    cmds.parent(pistonB_up, world=True)

    # Create aim constraints
    cmds.aimConstraint(
        pistonB, pistonA, wut="object", wuo=pistonA_up, aimVector=aim, upVector=up
    )
    cmds.aimConstraint(
        pistonA, pistonB, wut="object", wuo=pistonB_up, aimVector=aim, upVector=up
    )

    return [pistonA_up, pistonB_up]


def orient_constrain_chain(source_chain, source_suffix="_jnt", target_suffix="_ikj"):
    """Orient constrain source chain to target chain using search and replace suffix

    ikjs = ['lf_shoulderFront_ikj', 'lf_legFrontUpper_ikj', 'lf_legFrontLower_ikj', 'lf_legFrontShin_ikj', 'lf_legFrontToeTip_ikj']
    orient_constrain_chain(ikjs, source_suffix='_ikj', target_suffix='_jnt')
    """
    for jnt in source_chain:
        if cmds.objExists(jnt) and cmds.objExists(
            jnt.replace(source_suffix, target_suffix)
        ):
            cmds.orientConstraint(jnt.replace(source_suffix, target_suffix), jnt)
            log.debug(
                "Orient constrained {} to {}".format(
                    jnt, jnt.replace(source_suffix, target_suffix)
                )
            )
        else:
            log.error(
                "{} or {} does not exist!".format(
                    jnt, jnt.replace(source_suffix, target_suffix)
                )
            )


def leg_rig_cleanup():
    pass
