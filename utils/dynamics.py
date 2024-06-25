"""

    dynamics.py

    Utility for adding dynamic jiggle to controls of a rig.

    from mechRig_toolkit.utils import dynamics
    dynamics.create_jiggle_locator('ball', 'my_jiggle')

"""
import logging

from maya import cmds

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def create_jiggle_locator(position_object, base_name):
    """Create jiggle rig at the specified postion, you will then need to make sure
    this jiggle rig is hooked up to be driven by the source rig

    Usage:
        create_jiggle_locator('ball', 'my_jiggle')
    """
    if cmds.objExists(position_object):
        # Get position of input object
        pos = cmds.xform(position_object, q=True, ws=True, t=True)

        # Create single particle
        part = cmds.particle(
            p=[pos[0], (pos[1]), pos[2]], c=1, name="{}_particle".format(base_name)
        )
        cmds.setAttr("{}.particleRenderType".format(part[1]), 4)

        # Goal particle to source object
        cmds.goal(part[0], goal=position_object, w=0.5, utr=True)

        # Create output transform
        jiggle_output = cmds.spaceLocator(name="{}_ctl".format(base_name))[0]
        cmds.connectAttr(
            "{}.worldCentroid".format(part[1]), "{}.translate".format(jiggle_output)
        )

        # Create jiggle control
        for attr in ["rx", "ry", "rz", "sx", "sy", "sz", "v"]:
            cmds.setAttr("{}.{}".format(jiggle_output, attr), k=False, lock=True)

        # Add gravity
        grav = cmds.gravity(
            name="{}_gravity".format(base_name),
            pos=[0, 0, 0],
            m=100,
            att=0,
            dx=0,
            dy=-1,
            dz=0,
            mxd=-1,
        )[
            0
        ]  # , vsh=none -vex 0 -vof 0 0 0 -vsw 360 -tsr 0.5 ;
        cmds.connectDynamic(part, f=grav)

        # Add attrs: isDynamic=on, conserve=1.0, goalWeight[0]=1.0, goalSmoothness=3, gravity=9.8
        cmds.addAttr(jiggle_output, ln="JIGGLE", at="enum", en="__:")
        cmds.setAttr("{}.JIGGLE".format(jiggle_output), cb=True)

        # Enabled
        cmds.addAttr(jiggle_output, ln="enabled", at="bool")
        cmds.setAttr("{}.enabled".format(jiggle_output), k=True, l=False)
        cmds.setAttr("{}.enabled".format(jiggle_output), 1)
        cmds.connectAttr(
            "{}.enabled".format(jiggle_output), "{}.isDynamic".format(part[1])
        )

        # Dynamics Weight
        """
        cmds.addAttr(jiggle_output, ln="dynamicsWeight", at="double", min=0, max=1, dv=1)
        cmds.setAttr('{}.dynamicsWeight'.format(jiggle_output), k=True, l=False)
        cmds.connectAttr('{}.dynamicsWeight'.format(jiggle_output), '{}.dynamicsWeight'.format(part[1]))
        """
        # Conserve
        cmds.addAttr(jiggle_output, ln="conserve", at="double", min=0, max=1, dv=1)
        cmds.setAttr("{}.conserve".format(jiggle_output), k=True, l=False)
        cmds.connectAttr(
            "{}.conserve".format(jiggle_output), "{}.conserve".format(part[1])
        )

        # Goal Smoothness
        cmds.addAttr(jiggle_output, ln="goalSmoothness", at="double", min=0, dv=3)
        cmds.setAttr("{}.goalSmoothness".format(jiggle_output), k=True, l=False)
        cmds.connectAttr(
            "{}.goalSmoothness".format(jiggle_output),
            "{}.goalSmoothness".format(part[1]),
        )

        # Goal Weight
        cmds.addAttr(
            jiggle_output, ln="goalWeight", at="double", min=0, max=1.0, dv=0.5
        )
        cmds.setAttr("{}.goalWeight".format(jiggle_output), k=True, l=False)
        cmds.connectAttr(
            "{}.goalWeight".format(jiggle_output), "{}.goalWeight[0]".format(part[1])
        )

        cmds.addAttr(jiggle_output, ln="GRAVITY", at="enum", en="__:")
        cmds.setAttr("{}.GRAVITY".format(jiggle_output), cb=True)

        # Gravity
        cmds.addAttr(jiggle_output, ln="gravityMagnitude", at="double", min=0, dv=100)
        cmds.setAttr("{}.gravityMagnitude".format(jiggle_output), k=True, l=False)
        cmds.connectAttr(
            "{}.gravityMagnitude".format(jiggle_output), "{}.magnitude".format(grav)
        )

        # Gravity Direction
        cmds.addAttr(jiggle_output, ln="gravityDirection", at="double3")
        cmds.addAttr(
            jiggle_output,
            ln="gravityDirectionX",
            at="double",
            p="gravityDirection",
            dv=0,
        )
        cmds.addAttr(
            jiggle_output,
            ln="gravityDirectionY",
            at="double",
            p="gravityDirection",
            dv=-1,
        )
        cmds.addAttr(
            jiggle_output,
            ln="gravityDirectionZ",
            at="double",
            p="gravityDirection",
            dv=0,
        )

        cmds.setAttr("{}.gravityDirection".format(jiggle_output), k=True, l=False)
        cmds.setAttr("{}.gravityDirectionX".format(jiggle_output), k=True, l=False)
        cmds.setAttr("{}.gravityDirectionY".format(jiggle_output), k=True, l=False)
        cmds.setAttr("{}.gravityDirectionZ".format(jiggle_output), k=True, l=False)

        cmds.connectAttr(
            "{}.gravityDirectionX".format(jiggle_output), "{}.directionX".format(grav)
        )
        cmds.connectAttr(
            "{}.gravityDirectionY".format(jiggle_output), "{}.directionY".format(grav)
        )
        cmds.connectAttr(
            "{}.gravityDirectionZ".format(jiggle_output), "{}.directionZ".format(grav)
        )

        # Cleanup
        jiggle_group = cmds.group(empty=True, name="{}All_grp".format(base_name))
        cmds.parent(part[0], jiggle_output, grav, jiggle_group)

        cmds.select(jiggle_output)
        return jiggle_output
