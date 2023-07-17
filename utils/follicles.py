"""
    follicles.py

    Various follicle creation functions

    from mechRig_toolkit.utils import follicles

    # User prompted follicle creation on selected NURBS surface
    follicles.create_follicles_along_selected_surface()

"""
import logging
import re

from maya import cmds

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def create_follicles_along_selected_surface():
    """User-prompted follicle creation along surface

    Usage:
        Select a NURBS surface and run, specify number of follicles create and hit OK
    """
    selection = cmds.ls(selection=True)

    if selection:
        try:
            # Check that selection is a nurbs surface
            surf_shp = cmds.listRelatives(selection[0], shapes=True)[0]

            if "nurbsSurface" in cmds.nodeType(surf_shp):
                # Auto-determine direction
                direction = "u"
                spans_u = cmds.getAttr("{}.spansU".format(surf_shp))
                spans_v = cmds.getAttr("{}.spansV".format(surf_shp))
                if spans_v > spans_u:
                    direction = "v"

                # Get user input number of follicles
                result = cmds.promptDialog(
                    title="Number of follicles",
                    message="Enter number of follicles:",
                    button=["OK", "Cancel"],
                    defaultButton="OK",
                    cancelButton="Cancel",
                    dismissString="Cancel",
                )

                if result == "OK":
                    num_follicles = cmds.promptDialog(query=True, text=True)
                    create_follicles_along_surface(
                        selection[0],
                        int(num_follicles),
                        direction=direction,
                        create_joints=True,
                    )
                    log.info(
                        "Successfully created {} follicles on {} in {} direction.".format(
                            selection[0], num_follicles, direction
                        )
                    )
        except:
            log.error("Unable to create follicles along surface")
            raise


def create_follicle_at_surface_points():
    """Select surface point on NURBS surface, a follicle node will be created at that location

    Usage:
        RMB click over NURBS surface and select "Surface Point".  Select point on surface and run
        create_follicle_at_surface_points()
    """
    selection = cmds.ls(selection=True, flatten=True)
    if selection:
        fol_return = list()
        for sp in selection:
            if ".uv" in sp:
                log.info("Working on {}".format(sp))
                # Get surface and uv values
                surf = sp.split(".")[0]
                surf_shp = cmds.listRelatives(surf, shapes=True)[0]
                uv_val = re.findall(r"\[[^\]]*\]", sp)
                u_val = float(uv_val[0][1:-1])
                v_val = float(uv_val[1][1:-1])

                # Create follicle node
                fol = cmds.createNode("follicle")
                fol_tfm = cmds.listRelatives(fol, parent=True)[0]

                # Make connections
                cmds.connectAttr(
                    "{}.worldMatrix[0]".format(surf_shp),
                    "{}.inputWorldMatrix".format(fol),
                )
                cmds.connectAttr(
                    "{}.local".format(surf_shp), "{}.inputSurface".format(fol)
                )

                # Set paramU/V value on follicle shape
                cmds.setAttr("{}.parameterU".format(fol), u_val)
                cmds.setAttr("{}.parameterV".format(fol), v_val)

                # Connect follicle output to follicle transform
                cmds.connectAttr(
                    "{}.outTranslate".format(fol), "{}.translate".format(fol_tfm)
                )
                cmds.connectAttr(
                    "{}.outRotate".format(fol), "{}.rotate".format(fol_tfm)
                )

                fol_return.append(fol_tfm)

            else:
                log.error("{} is not a surface point".format(sp))
                return
        return fol_return


def create_follicles_along_surface(
    surface_name, number_of_follicles, direction="u", create_joints=True
):
    """Utility to create specified number follicles evenly spaced along one direction of surface

    create_follicles_along_surface('cn_cable_srf1', 35, direction="u", create_joints=True)
    """
    if cmds.objExists(surface_name):
        surf_shp = cmds.listRelatives(surface_name, shapes=True)[0]

        counter = 0.0
        param_val = 0.0
        spacing_val = 1.0 / float(number_of_follicles - 1)
        fol_tfms = list()

        while counter < number_of_follicles:
            # Create follicles
            fol = cmds.createNode("follicle")
            fol_tfm = cmds.listRelatives(fol, parent=True)[0]
            fol_tfms.append(fol_tfm)
            if create_joints:
                fol_jnt = cmds.joint()

            # Connect surface and follicle
            cmds.connectAttr(
                "{}.worldMatrix[0]".format(surf_shp), "{}.inputWorldMatrix".format(fol)
            )
            cmds.connectAttr("{}.local".format(surf_shp), "{}.inputSurface".format(fol))

            # Connect follicle output to follicle transform
            cmds.connectAttr(
                "{}.outTranslate".format(fol), "{}.translate".format(fol_tfm)
            )
            cmds.connectAttr("{}.outRotate".format(fol), "{}.rotate".format(fol_tfm))

            # Set paramU/V value on follicle shape
            if direction is "u":
                cmds.setAttr("{}.parameterU".format(fol), param_val)
                cmds.setAttr("{}.parameterV".format(fol), 0.5)
            else:
                cmds.setAttr("{}.parameterU".format(fol), 0.5)
                cmds.setAttr("{}.parameterV".format(fol), param_val)

            # Increment values for next follicle
            param_val = param_val + spacing_val
            counter = counter + 1

        fol_grp = cmds.createNode(
            "transform", name="{}_follicle_grp".format(surface_name)
        )
        cmds.parent(fol_tfms, fol_grp)

        return True
    else:
        log.error("{} does not exist, cannot create follicles")
        return
