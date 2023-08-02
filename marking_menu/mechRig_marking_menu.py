"""A simple example of a custom marking menu in Maya. The benefits of doing it this way with Python are that
it is very flexible and easily maintainable. Additionally, you can keep it in a version control system.


This file is used for demonstration purposes, to be followed along with in this blog post
http://bindpose.com/custom-marking-menu-maya-python/


from mechRig_toolkit.marking_menu import mechRig_marking_menu
mechRig_marking_menu.markingMenu()


*Use RMB + CTL + ALT to invoke marking menu
"""
import logging
from mechRig_toolkit.utils import locator

from maya import cmds, mel
import pymel.core as pm

log = logging.getLogger(__name__)

MENU_NAME = "MechRig_markingMenu"


class MarkingMenu:
    """The main class, which encapsulates everything we need to build and rebuild our marking menu. All
    that is done in the constructor, so all we need to do in order to build/update our marking menu is
    to initialize this class."""

    def __init__(self):
        self._removeOld()
        self._build()

    def _build(self):
        """Creates the marking menu context and calls the _buildMarkingMenu() method to populate it with all items."""
        menu = cmds.popupMenu(
            MENU_NAME,
            mm=1,
            b=3,
            aob=1,
            ctl=1,
            alt=1,
            sh=0,
            p="viewPanes",
            pmo=1,
            pmc=self._buildMarkingMenu,
        )

    def _removeOld(self):
        """Checks if there is a marking menu with the given name and if so deletes it to prepare for creating a new one.
        We do this in order to be able to easily update our marking menus."""
        if cmds.popupMenu(MENU_NAME, ex=1):
            cmds.deleteUI(MENU_NAME)

    def _buildMarkingMenu(self, menu, parent):
        """This is where all the elements of the marking menu our built."""
        cmds.popupMenu(MENU_NAME, e=True, dai=True)

        # Tool Launch Menu
        script_editor = lambda *args: mel.eval("ScriptEditor;")
        cmds.menuItem(p=menu, l="Script Editor", c=script_editor)

        node_editor = lambda *args: mel.eval("NodeEditorWindow;")
        cmds.menuItem(p=menu, l="Node Editor", c=node_editor)

        connection_editor = lambda *args: mel.eval("ConnectionEditor;")
        cmds.menuItem(
            p=menu,
            l="Connection Editor",
            c=connection_editor,
        )

        outliner = lambda *args: mel.eval("OutlinerWindow;")
        cmds.menuItem(p=menu, l="Outliner", c=outliner)

        cmds.menuItem(p=menu, d=True)

        paint_skin = lambda *args : mel.eval("ArtPaintSkinWeightsToolOptions;")
        cmds.menuItem(
            p=menu,
            l="Paint Weights",
            c=paint_skin,
        )

        cmds.menuItem(p=menu, d=True)

        # Rebuild
        cmds.menuItem(p=menu, l="Rebuild Marking Menu", c=rebuildMarkingMenu)

        # Build Sub-Radial Menus
        self._buildJointMenu(menu, parent)
        self._buildLocatorMenu(menu, parent)

    # W
    def _buildLocatorMenu(self, menu, parent):
        locMenu = cmds.menuItem(p=menu, l="Locators", rp="W", subMenu=1)

        cmds.menuItem(
            p=locMenu,
            l="Locator(s) at selected",
            c=locator.selected_points
        )
        cmds.menuItem(
            p=locMenu,
            l="Locator(s) at center of selected",
            c=locator.center_selection
        )

    # E
    def _buildJointMenu(self, menu, parent):
        jntMenu = cmds.menuItem(p=menu, l="Joints", rp="E", subMenu=1)

        cmds.menuItem(p=jntMenu, l="Show Joint Axis", c=self.showPivot)
        cmds.menuItem(
            p=jntMenu, l="Disable Segment Scale Compensate", c=self.setSSC
        )
        cmds.menuItem(
            p=jntMenu, l="Show/Hide Joint Orient", c=self.showJointOrient
        )

        create_joint = lambda *args: mel.eval("JointTool;")
        cmds.menuItem(
            p=jntMenu,
            l="Create Joint Tool",
            rp="N",
            c=create_joint,
        )
        cmds.menuItem(
            p=jntMenu,
            l="Edit Joint Pivot Tool",
            rp="NE",
            c=self.editJointPivotTool,
        )

        rotationMenu = cmds.menuItem(p=jntMenu, l="Rotations", rp="E", subMenu=1)
        cmds.menuItem(
            p=rotationMenu,
            l="Freeze Rotations",
            rp="E",
            c=self.freezeRotation,
        )
        cmds.menuItem(
            p=rotationMenu,
            l="Restore Rotations",
            rp="N",
            c=self.restoreRotation,
        )
        cmds.menuItem(
            p=rotationMenu,
            l="Rotations to Joint Orient",
            rp="NW",
            c=self.rotateToJointOrient,
        )
        cmds.menuItem(
            p=rotationMenu,
            l="Zero Joint Rotations",
            rp="S",
            c=self.zeroJointRotate,
        )
        cmds.menuItem(
            p=rotationMenu,
            l="Zero Joint Orient",
            rp="SE",
            c=self.zeroJointOrient,
        )
        cmds.menuItem(
            p=rotationMenu,
            l="Zero Joint Axis",
            rp="SW",
            c=self.zeroJointAxis,
        )

    def showPivot(self):
        objs = cmds.ls(selection=True)
        for obj in objs:
            obj.displayLocalAxis.set(not (obj.displayLocalAxis.get()))

    def rotateToJointOrient(self):
        objs = cmds.ls(selection=True)
        for obj in objs:
            if cmds.nodeType(obj) == "joint":
                cmds.makeIdentity(obj, rotate=True, apply=True)

    def zeroJointRotate(self):
        objs = cmds.ls(selection=True)
        for obj in objs:
            if cmds.nodeType(obj) == "joint":
                cmds.setAttr("{}.rotate".format(obj), 0, 0, 0, type="double3")

    def zeroJointOrient(self):
        objs = cmds.ls(selection=True)
        for obj in objs:
            if cmds.nodeType(obj) == "joint":
                cmds.setAttr("{}.jointOrient".format(obj), 0, 0, 0, type="double3")

    def zeroJointAxis(self):
        objs = cmds.ls(selection=True)
        for obj in objs:
            if cmds.nodeType(obj) == "joint":
                cmds.setAttr("{}.rotateAxis".format(obj), 0, 0, 0, type="double3")

    def editJointPivotTool(self):
        objs = cmds.ls(selection=True)
        cmds.selectMode(co=True)
        cmds.selectType(ra=True)
        cmds.select(objs[0], r=True)
        exit_context = lambda *args: self.editJointPivotExit(objs)
        rotateCtx = cmds.manipRotateContext(
            pod=exit_context
        )
        cmds.setToolTo(rotateCtx)

    def editJointPivotExit(self, objects):
        cmds.select(objects, r=True)
        cmds.selectMode(o=True)

    def showJointOrient(self):
        objs = cmds.ls(selection=True)
        for obj in objs:
            if cmds.nodeType(obj) == "joint":
                obj.jox.showInChannelBox(not (obj.jox.isInChannelBox()))
                obj.joy.showInChannelBox(not (obj.joy.isInChannelBox()))
                obj.joz.showInChannelBox(not (obj.joz.isInChannelBox()))

    def setSSC(self):
        objs = cmds.ls(selection=True)
        for obj in objs:
            if cmds.nodeType(obj) == "joint":
                obj.ssc.set(False)

    def restoreRotation(self):
        objs = cmds.ls(selection=True)
        for obj in objs:
            if cmds.nodeType(obj) == "joint":
                rot = obj.rotate.get()
                ra = obj.rotateAxis.get()
                jo = obj.jointOrient.get()

                rotMatrix = pm.dt.EulerRotation(rot, unit="degrees").asMatrix()
                raMatrix = pm.dt.EulerRotation(ra, unit="degrees").asMatrix()
                joMatrix = pm.dt.EulerRotation(jo, unit="degrees").asMatrix()

                rotationMatrix = raMatrix * rotMatrix * joMatrix
                tmat = pm.dt.TransformationMatrix(rotationMatrix)
                newRotation = tmat.eulerRotation()
                newRotation = [pm.dt.degrees(x) for x in newRotation.asVector()]

                obj.jointOrient.set(0, 0, 0)
                obj.rotateAxis.set(0, 0, 0)
                obj.rotate.set(newRotation)

    def freezeRotation(self):
        objs = cmds.ls(selection=True)
        for obj in objs:
            if cmds.nodeType(obj) == "joint":
                rot = obj.rotate.get()
                ra = obj.rotateAxis.get()
                jo = obj.jointOrient.get()

                rotMatrix = pm.dt.EulerRotation(rot, unit="degrees").asMatrix()
                raMatrix = pm.dt.EulerRotation(ra, unit="degrees").asMatrix()
                joMatrix = pm.dt.EulerRotation(jo, unit="degrees").asMatrix()

                rotationMatrix = rotMatrix * raMatrix * joMatrix
                tmat = pm.dt.TransformationMatrix(rotationMatrix)
                newRotation = tmat.eulerRotation()
                newRotation = [pm.dt.degrees(x) for x in newRotation.asVector()]

                obj.rotate.set(0, 0, 0)
                obj.rotateAxis.set(0, 0, 0)
                obj.jointOrient.set(newRotation)


def rebuildMarkingMenu(*args):
    """This function assumes that this file has been imported in the userSetup.py
    and all it does is reload the module and initialize the markingMenu class which
    rebuilds our marking menu"""
    cmds.evalDeferred(
        """from mechRig_toolkit.marking_menu import mechRig_marking_menu;mechRig_marking_menu.markingMenu()"""
    )
    log.info("Mech Rig Marking Menu loaded successfully!")


MarkingMenu()
