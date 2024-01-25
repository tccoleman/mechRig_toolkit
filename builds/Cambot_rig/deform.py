import logging

from maya import cmds

from mechRig_toolkit.utils import skin


logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def skin_geo():
    """Skins geometry to influence objects"""
    PROJ_PATH = cmds.workspace(query=True, rd=True)
    DATA_PATH = PROJ_PATH + "data/"

    cmds.skinCluster(
        ["lf_legFrontUpperPiston_jnt"],
        "lf_frontThighPiston_mesh",
        n="lf_frontThighPiston_mesh_sc",
        tsb=True,
    )
    cmds.skinCluster(
        ["lf_legFrontUpper_jnt"],
        "lf_frontThigh_mesh",
        n="lf_frontThigh_mesh_sc",
        tsb=True,
    )
    cmds.skinCluster(
        ["cn_body_jnt", "lf_shoulderFront_jnt"],
        "lf_frontShoulderHinge_mesh",
        n="lf_frontShoulderHinge_mesh_sc",
        tsb=True,
    )
    cmds.skinCluster(
        ["rt_legRearShin_jnt"], "rt_rearFoot_mesh", n="rt_rearFoot_mesh_sc", tsb=True
    )
    cmds.skinCluster(
        ["cn_body_jnt", "rt_shoulderFront_jnt"],
        "rt_frontShoulderHinge_mesh",
        n="rt_frontShoulderHinge_mesh_sc",
        tsb=True,
    )
    cmds.skinCluster(
        ["rt_legFrontLower_jnt"],
        "rt_frontShin_mesh",
        n="rt_frontShin_mesh_sc",
        tsb=True,
    )
    cmds.skinCluster(["cn_neck_jnt"], "cn_neck_mesh", n="cn_neck_mesh_sc", tsb=True)
    cmds.skinCluster(
        ["cn_body_jnt"], "cn_mainBody_mesh", n="cn_mainBody_mesh_sc", tsb=True
    )
    cmds.skinCluster(
        ["rt_legFrontUpper_jnt"],
        "rt_frontThigh_mesh",
        n="rt_frontThigh_mesh_sc",
        tsb=True,
    )
    cmds.skinCluster(
        ["rt_legFrontUpperPiston_jnt"],
        "rt_frontThighPiston_mesh",
        n="rt_frontThighPiston_mesh_sc",
        tsb=True,
    )
    cmds.skinCluster(
        ["lf_legFrontLowerPiston_jnt", "lf_legFrontUpperPiston_jnt"],
        "lf_frontShinPiston_mesh",
        n="lf_frontShinPiston_mesh_sc",
        tsb=True,
    )
    cmds.skinCluster(
        ["lf_legFrontShin_jnt"], "lf_frontFoot_mesh", n="lf_frontFoot_mesh_sc", tsb=True
    )
    cmds.skinCluster(
        ["lf_legRearUpperPiston_jnt"],
        "lf_rearThighPiston_mesh",
        n="lf_rearThighPiston_mesh_sc",
        tsb=True,
    )
    cmds.skinCluster(
        ["lf_legRearLower_jnt"], "lf_rearShin_mesh", n="lf_rearShin_mesh_sc", tsb=True
    )
    cmds.skinCluster(
        ["cn_body_jnt", "lf_shoulderRear_jnt"],
        "lf_rearShoulderHinge_mesh",
        n="lf_rearShoulderHinge_mesh_sc",
        tsb=True,
    )
    cmds.skinCluster(
        ["lf_legRearUpper_jnt"], "lf_rearThigh_mesh", n="lf_rearThigh_mesh_sc", tsb=True
    )
    cmds.skinCluster(
        ["rt_legFrontShin_jnt"], "rt_frontFoot_mesh", n="rt_frontFoot_mesh_sc", tsb=True
    )
    cmds.skinCluster(
        ["rt_legFrontLowerPiston_jnt", "rt_legFrontUpperPiston_jnt"],
        "rt_frontShinPiston_mesh",
        n="rt_frontShinPiston_mesh_sc",
        tsb=True,
    )
    cmds.skinCluster(
        ["rt_legRearUpper_jnt"], "rt_rearThigh_mesh", n="rt_rearThigh_mesh_sc", tsb=True
    )
    cmds.skinCluster(
        ["rt_legRearUpperPiston_jnt"],
        "rt_rearThighPiston_mesh",
        n="rt_rearThighPiston_mesh_sc",
        tsb=True,
    )
    cmds.skinCluster(
        ["lf_legFrontLower_jnt"],
        "lf_frontShin_mesh",
        n="lf_frontShin_mesh_sc",
        tsb=True,
    )
    cmds.skinCluster(
        ["lf_legRearLowerPiston_jnt", "lf_legRearUpperPiston_jnt"],
        "lf_rearShinPiston_mesh",
        n="lf_rearShinPiston_mesh_sc",
        tsb=True,
    )
    cmds.skinCluster(
        ["lf_legRearShin_jnt"], "lf_rearFoot_mesh", n="lf_rearFoot_mesh_sc", tsb=True
    )
    cmds.skinCluster(
        ["cn_body_jnt", "rt_shoulderRear_jnt"],
        "rt_rearShoulderHinge_mesh",
        n="rt_rearShoulderHinge_mesh_sc",
        tsb=True,
    )
    cmds.skinCluster(
        ["rt_legRearLowerPiston_jnt", "rt_legRearUpperPiston_jnt"],
        "rt_shinPiston_mesh",
        n="rt_shinPiston_mesh_sc",
        tsb=True,
    )
    cmds.skinCluster(
        ["rt_legRearLower_jnt"], "rt_rearShin_mesh", n="rt_rearShin_mesh_sc", tsb=True
    )

    # Example of skinning head mesh and importing skin weights
    cmds.skinCluster(
        ["cn_head_jnt", "lf_antennaRear_jnt", "lf_antenna_jnt"],
        "cn_head_mesh",
        n="cn_head_mesh_sc",
        tsb=True,
    )
    cmds.deformerWeights(
        "cn_head_mesh.xml",
        im=True,
        method="index",
        deformer="cn_head_mesh_sc",
        path=DATA_PATH,
    )
    cmds.skinCluster("cn_head_mesh_sc", edit=True, forceNormalizeWeights=True)

    # OR just do a mass import of skin weight files onto the meshes in your scene
    skin_meshes = cmds.listRelatives("geo", children=True)
    if skin_meshes:
        cmds.select(skin_meshes)
        skin.import_skin_weights_selected()

    log.info("Successfully skinned geometry")
