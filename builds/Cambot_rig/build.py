"""

    CamBot Scripted Rig Build - Tim Coleman, CGMA Mechanical Rigging

        This is an example of a scripted rig build in Maya.  The "build_rig" function here is called
        which runs a series of functions in a particular order to create different parts of the rig,
        the end result being the finished rig.  The benefits of a scripted rig are numerous since at
        any time the rig can be rebuilt.  Changes can be made to skeleton, geometry, controls and the build
        run again to build with the changed elements.  There of course is a learning curve and some coding up
        front.  However, the more general you can make your rig building code, the more reusable it becomes.

    To Run the Cambot Scripted Rig Build:

    1)  Download and Unzip the "Cambot.zip" file located in this same folder this script is in.

    2)  Set your Maya project to the downloaded/unzipped "Cambot" Maya project.  Make sure there is a "CamBot_build_v1.ma"
        in the scenes folder of this project.  The model and textures are not provided with this Maya project, so you will
        have to copy your latest Cambot model and textures into the models and textures directories in this Cambot
        Maya project.

    3)  Copy and paste the following into your Maya Script Editor (no need to have any files open beforehand):

        from mechRig_toolkit.builds import Cambot_rig
        Cambot_rig.build.run()

"""
import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

from maya import cmds

from mechRig_toolkit.utils import utility as util
reload(util)

import legs
reload(legs)

import deform
reload(deform)


ASSET = 'Cambot'
PROJ_PATH = cmds.workspace(query=True, rd=True)
RIG_BUILD_FILE = "CamBot_build_v1.ma"
RIG_OUTPUT_FILE = "CamBot_rig_v1.mb"


def run():
    """Builds Cambot animation rig"""

    cmds.file(force=True, new=True)

    #=========================
    # Import Build File
    #=========================
    cmds.file('{}scenes/{}'.format(PROJ_PATH, RIG_BUILD_FILE), i=True)

    #=========================
    # Top Rig Hierarchy
    #=========================
    top_node = cmds.group(name='{}_rig'.format(ASSET), empty=True)
    util.lock_unlock_channels(lock=True, attrs=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])

    geo_node = util.create_category(top_node, 'geo')
    skl_node = util.create_category(top_node, 'skeleton')
    rig_node = util.create_category(top_node, 'rig')
    nox_node = util.create_category(top_node, 'noXform')

    cmds.parent('cn_root_jnt', skl_node)
    cmds.parent('cn_master_grp', rig_node)

    # Constrain root joint to master offset
    cmds.parentConstraint('cn_masterOffset_ctl', 'cn_root_jnt')
    cmds.scaleConstraint('cn_masterOffset_ctl', 'cn_root_jnt')

    #=========================
    # Body and Cog
    #=========================
    cmds.parentConstraint('cn_cog_ctl', 'cn_body_jnt', mo=True)

    #=========================
    # Head Rig Build
    #=========================
    connect_control_to_joint('cn_head_ctl', 'cn_head_jnt', connections=['rotateX'], connect_offset=True)

    # Head aim (simple version)
    cmds.aimConstraint('cn_headAim_ctl', 'cn_head_off', mo=True, aim=[0,0,1], u=[0,-1,0], wuo='cn_body_jnt', skip=['y','z'])
    cmds.pointConstraint('cn_cog_ctl', 'cn_head_grp', mo=True, skip=['x','y'])

    #=========================
    # Neck Rig Build
    #=========================
    connect_control_to_joint('cn_neck_ctl', 'cn_neck_jnt', connections=['rotateY'], connect_offset=True)

    #=========================
    # Shoulders/Legs Build
    #=========================
    legs.rig_legs()
    #legs.add_softIK()

    #=========================
    # Leg Pistons
    #=========================
    legs.rig_pistons()

    #=========================
    # Antenna Rig Build
    #=========================
    ant_up = antenna_setup('cn_antSide', 'cn_antSide_ctl', 'lf_antenna_jnt', aim=[0, 1, 0], up=[0, 0, 1])
    cmds.parent(ant_up, 'cn_head_ctl')

    ant_up = antenna_setup('cn_antRear', 'cn_antRear_ctl', 'lf_antennaRear_jnt', aim=[0, 1, 0], up=[0, 0, 1])
    cmds.parent(ant_up, 'cn_head_ctl')

    # add_antenna_jiggle()

    #=========================
    # Cable Rig Build
    #=========================
    # add_cable_rig()
    # add_cable_jiggle()

    #=========================
    # Import referenced model and remove model namespace
    #=========================
    import_references()
    remove_namespace('model')
    cmds.parent('{}_model'.format(ASSET), geo_node)

    #=========================
    # Skin model
    #=========================
    deform.skin_geo()

    #=========================
    # Cleanup scene
    #=========================
    lock_channels()

    #=========================
    # Set final display
    #=========================
    cmds.select(clear=True)
    cmds.viewFit()
    cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)
    cmds.setAttr("hardwareRenderingGlobals.lineAAEnable", 1)

    cmds.setAttr("{}_rig.geo".format(ASSET), 2)
    cmds.setAttr("{}_rig.skeleton".format(ASSET), 0)
    cmds.setAttr("{}_rig.noXform".format(ASSET), 0)

    #=========================
    # Save final rig
    #=========================
    cmds.file(rename='{}scenes/{}'.format(PROJ_PATH, RIG_OUTPUT_FILE))
    cmds.file(save=True)

    LOG.info('Successfully built: {} Rig'.format(ASSET))


def import_references():
    """Import all referenced files into scene"""
    refs = cmds.file(q=True, r=True)
    for ref in refs:
        LOG.debug('Importing Reference..')
        if cmds.referenceQuery(ref, il=True):
            cmds.file(ref, ir=True)


def remove_namespace(namespace_string):
    """Remove namespace from the current Maya scene.

    Args:
        namespace_string: Namespace to remove

    remove_namespace('model')
    """
    namespaces = cmds.namespaceInfo(lon=True, r=True)
    for ns in namespaces:
        if namespace_string in ns:
            try:
                cmds.namespace(rm=ns, mnr=True)
                LOG.debug('Removed namespace: `{0}`'.format(ns))
            except RuntimeError as e:
                LOG.exception('Could not remove namespace, it might not be empty: {}'.format(e))


def connect_control_to_joint(control, joint, connections=['rotateX'], connect_offset=True):
    """Connects control and optionally offset to joint via plusMinusAverage node"""

    # Make sure rig inputs exist
    if cmds.objExists(control) and cmds.objExists(joint):

        for attr in connections:
            # Create plusMinusAverage node to combine the rotation of head control/offset to head joint
            pma = cmds.createNode('plusMinusAverage', name='{}{}_pma'.format(control, attr))

            # Connect control to pma
            cmds.connectAttr('{}.{}'.format(control, attr), '{}.input1D[0]'.format(pma))

            if connect_offset:
                # Find offset transform and connect to pma as well
                offset = cmds.listRelatives(control, parent=True)

                if offset:
                    cmds.connectAttr('{}.{}'.format(offset[0], attr), '{}.input1D[1]'.format(pma))

            cmds.connectAttr('{}.output1D'.format(pma), '{}.{}'.format(joint, attr), force=True)

    else:
        LOG.error('Control or joint does not exist!')
        return


def orient_constrain_chain(source_chain, source_suffix='_jnt', target_suffix='_ikj'):
    """Orient constrain source chain to target chain using search and replace suffix

    ikjs = ['lf_shoulderFront_ikj', 'lf_legFrontUpper_ikj', 'lf_legFrontLower_ikj', 'lf_legFrontShin_ikj', 'lf_legFrontToeTip_ikj']
    orient_constrain_chain(ikjs, source_suffix='_ikj', target_suffix='_jnt')
    """
    for jnt in source_chain:
        if cmds.objExists(jnt) and cmds.objExists(jnt.replace(source_suffix, target_suffix)):
            cmds.orientConstraint(jnt.replace(source_suffix, target_suffix), jnt)
            LOG.debug('Orient constrained {} to {}'.format(jnt, jnt.replace(source_suffix, target_suffix)))
        else:
            LOG.error('{} or {} does not exist!'.format(jnt, jnt.replace(source_suffix, target_suffix)))


def antenna_setup(base_name, control, joint, aim=[0, 1, 0], up=[0, 0, 1]):
    """Creates aim constraint antenna rig

    antenna_setup('cn_antSide', 'cn_antSide_ctl', 'lf_antenna_jnt', aim=[0,1,0], up=[0,0,1])
    """
    # Create up vectors
    ant_up = cmds.spaceLocator(name='{}_up'.format(joint))[0]
    cmds.parent(ant_up, joint)
    cmds.setAttr('{}.translate'.format(ant_up), *up)
    cmds.setAttr('{}.rotate'.format(ant_up), 0, 0, 0)
    cmds.parent(ant_up, world=True)
    cmds.hide(ant_up)

    # Create aim constraints
    cmds.aimConstraint(control, joint, wut='object', wuo=ant_up, aimVector=aim, upVector=up)

    return ant_up


def lock_channels():
    """Locks CamBot channel attrs"""

    LOCK_ALL = cmds.ls('*_grp')
    cmds.select(clear=True)
    cmds.select(LOCK_ALL)
    util.lock_unlock_channels(lock=True, attrs=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])

    BODY = cmds.ls('cn_body_off', 'cn_body_ctl', 'cn_cog_off', 'cn_cog_ctl')
    cmds.select(clear=True)
    cmds.select(BODY)
    util.lock_unlock_channels(lock=True, attrs=['tx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])

    XROT_ONLY = ['cn_head_off', 'cn_head_ctl']
    cmds.select(clear=True)
    cmds.select(XROT_ONLY)
    util.lock_unlock_channels(lock=True, attrs=['tx', 'ty', 'tz', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])

    YROT_ONLY = cmds.ls('cn_neck_off', 'cn_neck_ctl', '*_shoulder*_off', '*_shoulder*_ctl')
    cmds.select(clear=True)
    cmds.select(YROT_ONLY)
    util.lock_unlock_channels(lock=True, attrs=['tx', 'ty', 'tz', 'rx', 'rz', 'sx', 'sy', 'sz', 'v'])

    FEET = cmds.ls('*_leg*_off', '*_leg*_ctl')
    cmds.select(clear=True)
    cmds.select(FEET)
    util.lock_unlock_channels(lock=True, attrs=['tx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])

    ANTENNA = cmds.ls('*_ant*_off', '*_ant*_ctl')
    cmds.select(clear=True)
    cmds.select(ANTENNA)
    util.lock_unlock_channels(lock=True, attrs=['ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])

    LOG.debug('Successfully locked attribute channels')

