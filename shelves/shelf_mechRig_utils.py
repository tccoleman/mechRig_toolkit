"""
    Creates mechRig_utils Maya shelf

    To use, run these Python commands in Maya:

        from mechRig_toolkit.shelves import shelf_mechRig_utils
        reload(shelf_mechRig_utils)
        shelf_mechRig_utils.load(name="MechRig_utils")

"""
SHELF_NAME = 'MechRig_utils'
VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_PATCH = 0

version_info = (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)
version = '{}.{}.{}'.format(*version_info)
__version__ = version

__all__ = ['version', 'version_info', '__version__']

import logging
LOG = logging.getLogger(__name__)

import os
import sys
import subprocess

import shelf_base
reload(shelf_base)

from maya import cmds

from mechRig_toolkit.utils import locator
reload(locator)
cmds.selectPref(trackSelectionOrder=True)

from mechRig_toolkit.utils import utility
reload(utility)

from mechRig_toolkit.utils import week6
reload(week6)

from mechRig_toolkit.control_shapes import functions as ctl_func
reload(ctl_func)

from mechRig_toolkit.control_shapes import core as ctl_core
reload(ctl_core)

from mechRig_toolkit.control_shapes import color as ctl_color
reload(ctl_color)

from mechRig_toolkit.control_shapes import transform as ctl_trans
reload(ctl_trans)

ICON_DIR = os.path.join(os.path.dirname(__file__), 'shelf_mechRig_utils_icons')
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), 'shelf_mechRig_utils_scripts')
PLATFORM = sys.platform

sys.path.append(SCRIPTS_DIR)


def explore_maya_project():
    """Opens explorer window to current Maya project location"""
    proj_dir = cmds.workspace(rd=True, q=True)
    subprocess.Popen(r'explorer /select,"{}scenes"'.format(proj_dir.replace("/", "\\")))
    LOG.info('Exploring to %s'.format(proj_dir))


def reload_shelf(shelf_name=SHELF_NAME):
    """Reloads shelf"""
    try:
        import shelf_base
        reload(shelf_base)

        from mechRig_toolkit.shelves import shelf_mechRig_utils
        reload(shelf_mechRig_utils)

        shelf_mechRig_utils.load(name=shelf_name)
        LOG.info("Successfully reloaded {} shelf".format(SHELF_NAME))
        return True
    except:
        LOG.error("Error reloading shelf")
        return


def setup_mech_rig_marking_menu():

    from mechRig_toolkit.marking_menu import mechRig_marking_menu
    reload(mechRig_marking_menu)
    mechRig_marking_menu.markingMenu()

    LOG.info("Setup Mech Rig Marking Menu")


class load(shelf_base._shelf):

    def build(self):

        # Reload shelf button
        self.addButton(label="", icon=ICON_DIR + "/reloadShelf.png",
                      command="from mechRig_toolkit.shelves import shelf_mechRig_utils; "
                              "maya.utils.executeDeferred('shelf_mechRig_utils.reload_shelf()')")

        # Separator
        self.addButton(label="", icon=ICON_DIR + "/sep.png", command='')

        # General Tools
        self.addButton(label="", icon=ICON_DIR + "/generalTools.png")
        general_tools_menu = cmds.popupMenu(b=1)

        self.addMenuItemDivider(general_tools_menu, divider=True, dividerLabel='PROJECT...')

        self.addMenuItem(general_tools_menu, "Explore to Project Directory", command="from mechRig_toolkit.shelves "
                                                                           "import shelf_mechRig_utils;"
                                                                           "reload(shelf_mechRig_utils);"
                                                                           "shelf_mechRig_utils.explore_maya_project()")

        self.addMenuItemDivider(general_tools_menu, divider=True, dividerLabel='SETUP...')

        self.addMenuItem(general_tools_menu, "Setup Marking Menu", command="from mechRig_toolkit.shelves "
                                                                           "import shelf_mechRig_utils;"
                                                                           "reload(shelf_mechRig_utils);"
                                                                           "shelf_mechRig_utils.setup_mech_rig_marking_menu()")

        self.addMenuItemDivider(general_tools_menu, divider=True, dividerLabel='DISPLAY...')

        self.addMenuItem(general_tools_menu, "Toggle anti-alias viewport display", command="from mechRig_toolkit.utils import general; "
                                                                                    "reload(general);"
                                                                                    "general.toggle_antialias_viewport_display()")

        self.addMenuItem(general_tools_menu, "Set near clip plane", command="from mechRig_toolkit.utils import general; "
                                                                            "reload(general);"
                                                                            "general.set_near_clip()")

        # Snap Tools
        self.addButton(label="", icon=ICON_DIR + "/snapTools.png")
        snap_tools_menu = cmds.popupMenu(b=1)

        self.addMenuItemDivider(snap_tools_menu, divider=True, dividerLabel='CREATE LOCATORS...')

        self.addMenuItem(snap_tools_menu, "Locator at selected position",command="from mechRig_toolkit.utils import locator; "
                                                                        "reload(locator);"
                                                                        "locator.selected_points()")

        self.addMenuItem(snap_tools_menu, "Locator at selected position/rotation", command="from mechRig_toolkit.utils import locator; "
                                                                                           "reload(locator);"
                                                                                           "locator.create_locator_snap()")

        self.addMenuItem(snap_tools_menu, "Locator at center of selected", command="from mechRig_toolkit.utils "
                                                                                     "import locator;"
                                                                                     "reload(locator);"
                                                                                     "locator.center_selection()")

        self.addMenuItem(snap_tools_menu, "Locator aimed at selected", command="from mechRig_toolkit.utils "
                                                                               "import locator;"
                                                                               "reload(locator);"
                                                                               "locator.aim_selection()")

        self.addMenuItemDivider(snap_tools_menu, divider=True, dividerLabel='MATCHING TRANSFORMS...')

        self.addMenuItem(snap_tools_menu, "Snap first items to last", command="from mechRig_toolkit.utils "
                                                                               "import locator;"
                                                                               "reload(locator);"
                                                                               "locator.snap_object()")


        # Joint Tools
        self.addButton(label="", icon=ICON_DIR + "/jointTools.png")
        joint_tools_menu = cmds.popupMenu(b=1)

        self.addMenuItemDivider(joint_tools_menu, divider=True, dividerLabel='CREATE...')

        self.addMenuItem(joint_tools_menu, "Create follicles/joints on selected surface...",
                         command="from mechRig_toolkit.utils import follicles; reload(follicles); follicles.create_follicles_along_selected_surface();")

        self.addMenuItemDivider(joint_tools_menu, divider=True, dividerLabel='UTILITIES...')

        self.addMenuItem(joint_tools_menu, "Toggle LRA", command="from maya import cmds; cmds.toggle(localAxis=True)")

        self.addMenuItem(joint_tools_menu, "Freeze Joint Rotations", command="from maya import cmds;"
                                                                             "cmds.makeIdentity(apply=True, t=False, r=True, s=False, n=False, pn=False)")

        self.addMenuItem(joint_tools_menu, "Orient To", command="from mechRig_toolkit.utils import joints; joints.orientTo();")


        # Skin Tools
        self.addButton(label="", icon=ICON_DIR + "/skinTools.png")
        skin_tools_menu = cmds.popupMenu(b=1)

        self.addMenuItemDivider(skin_tools_menu, divider=True, dividerLabel='UTILITIES...')

        self.addMenuItem(skin_tools_menu, "Transfer Skin: Source -> Target",
                         command="from mechRig_toolkit.utils import skin; reload(skin); skin.do_transfer_skin();")

        self.addMenuItem(skin_tools_menu, "Rename Shape Deformed nodes on selected...",
                         command="from mechRig_toolkit.utils import skin; reload(skin); skin.rename_shape_deformed_nodes();")

        self.addMenuItem(skin_tools_menu, "Print skinCluster command from selected...",
                         command="from mechRig_toolkit.utils import skin; reload(skin); skin.return_skin_command();")

        self.addMenuItemDivider(skin_tools_menu, divider=True, dividerLabel='IMPORT/EXPORT...')

        self.addMenuItem(skin_tools_menu, "Import skin weight file onto selected (if it exists)...",
                         command="from mechRig_toolkit.utils import skin; reload(skin); skin.import_skin_weights_selected();")

        self.addMenuItem(skin_tools_menu, "Export skin weight file from selected...",
                         command="from mechRig_toolkit.utils import skin; reload(skin); skin.export_skin_weights_selected();")


        # Anim Control Tools
        self.addButton(label="", icon=ICON_DIR + "/controlTools.png")
        ctl_tools_menu = cmds.popupMenu(b=1)

        cmds.menuItem(p=ctl_tools_menu, divider=True, dividerLabel='SHAPE...')
        cmds.menuItem(p=ctl_tools_menu, l="Save Shape...", command=ctl_func.save_ctl_shape_to_lib)

        sub = cmds.menuItem(p=ctl_tools_menu, l="Assign Shape to selected...", subMenu=1)

        for each in ctl_func.get_available_control_shapes():
            self.addMenuItem(sub, each[0], command=each[1])

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


        # Utilities
        self.addButton(label="", icon=ICON_DIR + "/utils.png")
        utils_menu = cmds.popupMenu(b=1)
        cmds.menuItem(p=utils_menu, l="Lock All Channels on selected...",
                      command=lambda *args: utility.lock_unlock_channels(lock=True))
        cmds.menuItem(p=utils_menu, l="Unlock All Channels on selected...",
                      command=lambda *args: utility.lock_unlock_channels(lock=False))

        # Separator
        self.addButton(label="", icon=ICON_DIR + "/sep.png", command='')


        # Week 6 Tools
        self.addButton(label="", icon=ICON_DIR + "/week6Tools.png")
        week6_tools_menu = cmds.popupMenu(b=1)

        cmds.menuItem(p=week6_tools_menu, l="Duplicate (Parent Only)", command=lambda *args: cmds.duplicate(parentOnly=True))
        cmds.menuItem(p=week6_tools_menu, l="Snap first object(s) to last", command=lambda *args: week6.match_selection())
        cmds.menuItem(p=week6_tools_menu, l="Create Pole Vector (select PV control then IK handle)", command=lambda *args: week6.create_pole_vector_from_selection())
        cmds.menuItem(p=week6_tools_menu, l="Create Category Switch (select rig top node)", command=lambda *args: week6.create_category_ui())
        cmds.menuItem(p=week6_tools_menu, l="Add offset and group transforms above selected control", command=lambda *args: week6.add_transforms_selected())

