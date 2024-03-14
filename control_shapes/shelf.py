"""

    Adds a "Control Shapes Tool" button to the currently active shelf.

    import control_shapes.shelf
    reload(control_shapes.shelf)
    control_shapes.shelf.load()


"""
import logging
import os

from maya import cmds, mel

from mechRig_toolkit.control_shapes import functions as ctl_func
from mechRig_toolkit.control_shapes import core as ctl_core
from mechRig_toolkit.control_shapes import color as ctl_color
from mechRig_toolkit.control_shapes import transform as ctl_trans


logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# SHELF_NAME = "Custom"
CURRENT_DIRECTORY = os.path.dirname(__file__)
ICON_PATH = os.path.abspath("{}\\icons".format(CURRENT_DIRECTORY))


def load():
    # Query currently active shelf tab
    tab_layout = mel.eval("$pytmp=$gShelfTopLevel")
    current_shelf = cmds.tabLayout(tab_layout, query=True, selectTab=True)

    shelf_exists = cmds.shelfLayout(current_shelf, exists=True)

    if shelf_exists:
        result = cmds.confirmDialog(
            title="Confirm",
            message="Add Control Shape Tool to current shelf?",
            button=["Yes", "No"],
            defaultButton="Yes",
            cancelButton="No",
            dismissString="No",
        )

        if result == "Yes":
            log.info(
                "Adding Control Shape Tools button to {} shelf".format(current_shelf)
            )

            SHELF_NAME = current_shelf

            if SHELF_NAME and cmds.shelfLayout(SHELF_NAME, ex=1):
                children = cmds.shelfLayout(SHELF_NAME, q=1, ca=1) or []
                for each in children:
                    try:
                        label = cmds.shelfButton(each, q=1, l=1)
                    except:
                        continue
                    if label == "Control_Shapes":
                        cmds.deleteUI(each)

                cmds.setParent(SHELF_NAME)
                cmds.shelfButton(
                    i="{}/controlShapeTools.png".format(ICON_PATH),
                    width=37,
                    height=37,
                    iol="",
                )

                ctl_tools_menu = cmds.popupMenu(b=1)

                cmds.menuItem(p=ctl_tools_menu, divider=True, dividerLabel="SHAPE...")
                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Save Shape...",
                    command=ctl_func.save_ctl_shape_to_lib,
                )

                sub = cmds.menuItem(
                    p=ctl_tools_menu, l="Assign Shape to selected...", subMenu=1
                )

                for each in ctl_func.get_available_control_shapes():
                    cmds.menuItem(p=sub, l=each[0], command=each[1])

                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Open Shape directory...",
                    c=lambda *args: ctl_core.open_control_shape_directory(),
                )

                cmds.menuItem(p=ctl_tools_menu, divider=True, dividerLabel="COLOR...")
                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Color Shapes",
                    command=lambda *args: ctl_color.set_override_color_UI(),
                )

                cmds.menuItem(
                    p=ctl_tools_menu, divider=True, dividerLabel="COPY/PASTE..."
                )
                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Copy Shape",
                    command=lambda *args: ctl_func.copy_ctl_shape(),
                )
                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Paste Shape",
                    command=lambda *args: ctl_func.paste_ctl_shape(),
                )
                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Delete Shapes",
                    command=lambda *args: ctl_func.delete_shapes(),
                )

                cmds.menuItem(
                    p=ctl_tools_menu, divider=True, dividerLabel="TRANSFORM..."
                )
                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Mirror Shape",
                    command=lambda *args: ctl_trans.mirror_ctl_shapes(),
                )

                cmds.menuItem(p=ctl_tools_menu, divider=True)

                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Rotate X 90",
                    command=lambda *args: ctl_trans.rotate_shape([90, 0, 0]),
                )
                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Rotate Y 90",
                    command=lambda *args: ctl_trans.rotate_shape([0, 90, 0]),
                )
                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Rotate Z 90",
                    command=lambda *args: ctl_trans.rotate_shape([0, 0, 90]),
                )

                cmds.menuItem(p=ctl_tools_menu, divider=True)

                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Rotate X -90",
                    command=lambda *args: ctl_trans.rotate_shape([-90, 0, 0]),
                )
                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Rotate Y -90",
                    command=lambda *args: ctl_trans.rotate_shape([0, -90, 0]),
                )
                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Rotate Z -90",
                    command=lambda *args: ctl_trans.rotate_shape([0, 0, -90]),
                )

                cmds.menuItem(p=ctl_tools_menu, divider=True)

                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Scale Up Shape",
                    command=lambda *args: ctl_trans.scale_up_selected(),
                )
                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Scale Down Shape",
                    command=lambda *args: ctl_trans.scale_down_selected(),
                )

                cmds.menuItem(p=ctl_tools_menu, divider=True)

                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Flip Shape",
                    command=lambda *args: ctl_trans.flip_shape_callback(),
                )
                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Flip Shape X",
                    command=lambda *args: ctl_trans.flip_shape_X(),
                )
                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Flip Shape Y",
                    command=lambda *args: ctl_trans.flip_shape_Y(),
                )
                cmds.menuItem(
                    p=ctl_tools_menu,
                    l="Flip Shape Z",
                    command=lambda *args: ctl_trans.flip_shape_Z(),
                )

        else:
            log.error(
                "Error adding Control Shape Tools button to {} shelf".format(
                    current_shelf
                )
            )
            return
    """
    if SHELF_NAME and cmds.shelfLayout(SHELF_NAME, ex=1):
        children = cmds.shelfLayout(SHELF_NAME, q=1, ca=1) or []
        for each in children:
            try:
                label = cmds.shelfButton(each, q=1, l=1)
            except:
                continue
            if label == "Control_Shapes":
                cmds.deleteUI(each)

        cmds.setParent(SHELF_NAME)
        cmds.shelfButton(i="{}/controlShapeTools.png".format(ICON_PATH), width=37, height=37, iol="")

        ctl_tools_menu = cmds.popupMenu(b=1)

        cmds.menuItem(p=ctl_tools_menu, divider=True, dividerLabel='SHAPE...')
        cmds.menuItem(p=ctl_tools_menu, l="Save Shape...", command=ctl_func.save_ctl_shape_to_lib)

        sub = cmds.menuItem(p=ctl_tools_menu, l="Assign Shape to selected...", subMenu=1)

        for each in ctl_func.get_available_control_shapes():
            cmds.menuItem(p=sub, l=each[0], command=each[1])

        cmds.menuItem(p=ctl_tools_menu, l="Open Shape directory...",
                      c=lambda *args: ctl_core.open_control_shape_directory())

        cmds.menuItem(p=ctl_tools_menu, divider=True, dividerLabel='COLOR...')
        cmds.menuItem(p=ctl_tools_menu, l="Color Shapes", command=lambda *args: ctl_color.set_override_color_UI())

        cmds.menuItem(p=ctl_tools_menu, divider=True, dividerLabel='COPY/PASTE...')
        cmds.menuItem(p=ctl_tools_menu, l="Copy Shape", command=lambda *args: ctl_func.copy_ctl_shape())
        cmds.menuItem(p=ctl_tools_menu, l="Paste Shape", command=lambda *args: ctl_func.paste_ctl_shape())
        cmds.menuItem(p=ctl_tools_menu, l="Delete Shapes", command=lambda *args: ctl_func.delete_shapes())

        cmds.menuItem(p=ctl_tools_menu, divider=True, dividerLabel='TRANSFORM...')
        cmds.menuItem(p=ctl_tools_menu, l="Mirror Shape", command=lambda *args: ctl_trans.mirror_ctl_shapes())

        cmds.menuItem(p=ctl_tools_menu, divider=True)

        cmds.menuItem(p=ctl_tools_menu, l="Rotate X 90", command=lambda *args: ctl_trans.rotate_shape([90, 0, 0]))
        cmds.menuItem(p=ctl_tools_menu, l="Rotate Y 90", command=lambda *args: ctl_trans.rotate_shape([0, 90, 0]))
        cmds.menuItem(p=ctl_tools_menu, l="Rotate Z 90", command=lambda *args: ctl_trans.rotate_shape([0, 0, 90]))

        cmds.menuItem(p=ctl_tools_menu, divider=True)

        cmds.menuItem(p=ctl_tools_menu, l="Rotate X -90", command=lambda *args: ctl_trans.rotate_shape([-90, 0, 0]))
        cmds.menuItem(p=ctl_tools_menu, l="Rotate Y -90", command=lambda *args: ctl_trans.rotate_shape([0, -90, 0]))
        cmds.menuItem(p=ctl_tools_menu, l="Rotate Z -90", command=lambda *args: ctl_trans.rotate_shape([0, 0, -90]))

        cmds.menuItem(p=ctl_tools_menu, divider=True)

        cmds.menuItem(p=ctl_tools_menu, l="Scale Up Shape", command=lambda *args: ctl_trans.scale_up_selected())
        cmds.menuItem(p=ctl_tools_menu, l="Scale Down Shape", command=lambda *args: ctl_trans.scale_down_selected())

        cmds.menuItem(p=ctl_tools_menu, divider=True)

        cmds.menuItem(p=ctl_tools_menu, l="Flip Shape", command=lambda *args: ctl_trans.flip_shape_callback())
        cmds.menuItem(p=ctl_tools_menu, l="Flip Shape X", command=lambda *args: ctl_trans.flip_shape_X())
        cmds.menuItem(p=ctl_tools_menu, l="Flip Shape Y", command=lambda *args: ctl_trans.flip_shape_Y())
        cmds.menuItem(p=ctl_tools_menu, l="Flip Shape Z", command=lambda *args: ctl_trans.flip_shape_Z())
    """
