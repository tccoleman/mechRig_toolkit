"""A simple example of a custom marking menu in Maya. The benefits of doing it this way with Python are that
it is very flexible and easily maintainable. Additionally, you can keep it in a version control system.


This file is used for demonstration purposes, to be followed along with in this blog post
http://bindpose.com/custom-marking-menu-maya-python/


from mechRig_toolkit.marking_menu import mechRig_marking_menu
mechRig_marking_menu.markingMenu()


*Use RMB + CTL + ALT to invoke marking menu
"""
import logging

from maya import cmds
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
        pm.popupMenu(MENU_NAME, e=True, dai=True)

        # Tool Launch Menu
        # TODO : replace every instance of this kind of stuff with a call to a lambda to remove pymel dependency
        pm.menuItem(
            p=menu, l="Script Editor", c=pm.Callback(pm.mel.eval, "ScriptEditor;")
        )
        pm.menuItem(
            p=menu, l="Node Editor", c=pm.Callback(pm.mel.eval, "NodeEditorWindow;")
        )
        pm.menuItem(
            p=menu,
            l="Connection Editor",
            c=pm.Callback(pm.mel.eval, "ConnectionEditor;"),
        )
        pm.menuItem(p=menu, l="Outliner", c=pm.Callback(pm.mel.eval, "OutlinerWindow;"))
        pm.menuItem(p=menu, d=True)
        pm.menuItem(
            p=menu,
            l="Paint Weights",
            c=pm.Callback(pm.mel.eval, "ArtPaintSkinWeightsToolOptions;"),
        )
        pm.menuItem(p=menu, d=True)

        # Rebuild
        cmds.menuItem(p=menu, l="Rebuild Marking Menu", c=rebuildMarkingMenu)

        # Build Sub-Radial Menus
        self._buildJointMenu(menu, parent)
        self._buildLocatorMenu(menu, parent)

    # W
    def _buildLocatorMenu(self, menu, parent):
        locMenu = pm.menuItem(p=menu, l="Locators", rp="W", subMenu=1)

        pm.menuItem(
            p=locMenu,
            l="Locator(s) at selected",
            c=pm.Callback(
                pm.python,
                "from mechRig_toolkit.utils "
                "import locator; locator.selected_points();",
            ),
        )
        pm.menuItem(
            p=locMenu,
            l="Locator(s) at center of selected",
            c=pm.Callback(
                pm.python,
                "from mechRig_toolkit.utils "
                "import locator; locator.center_selection();",
            ),
        )

    # E
    def _buildJointMenu(self, menu, parent):
        jntMenu = pm.menuItem(p=menu, l="Joints", rp="E", subMenu=1)

        pm.menuItem(p=jntMenu, l="Show Joint Axis", c=pm.Callback(self.showPivot))
        pm.menuItem(
            p=jntMenu, l="Disable Segment Scale Compensate", c=pm.Callback(self.setSSC)
        )
        pm.menuItem(
            p=jntMenu, l="Show/Hide Joint Orient", c=pm.Callback(self.showJointOrient)
        )

        pm.menuItem(
            p=jntMenu,
            l="Create Joint Tool",
            rp="N",
            c=pm.Callback(pm.mel.eval, "JointTool;"),
        )
        pm.menuItem(
            p=jntMenu,
            l="Edit Joint Pivot Tool",
            rp="NE",
            c=pm.Callback(self.editJointPivotTool),
        )

        rotationMenu = pm.menuItem(p=jntMenu, l="Rotations", rp="E", subMenu=1)
        pm.menuItem(
            p=rotationMenu,
            l="Freeze Rotations",
            rp="E",
            c=pm.Callback(self.freezeRotation),
        )
        pm.menuItem(
            p=rotationMenu,
            l="Restore Rotations",
            rp="N",
            c=pm.Callback(self.restoreRotation),
        )
        pm.menuItem(
            p=rotationMenu,
            l="Rotations to Joint Orient",
            rp="NW",
            c=pm.Callback(self.rotateToJointOrient),
        )
        pm.menuItem(
            p=rotationMenu,
            l="Zero Joint Rotations",
            rp="S",
            c=pm.Callback(self.zeroJointRotate),
        )
        pm.menuItem(
            p=rotationMenu,
            l="Zero Joint Orient",
            rp="SE",
            c=pm.Callback(self.zeroJointOrient),
        )
        pm.menuItem(
            p=rotationMenu,
            l="Zero Joint Axis",
            rp="SW",
            c=pm.Callback(self.zeroJointAxis),
        )

    def showPivot(self):
        objs = pm.selected()
        for obj in objs:
            obj.displayLocalAxis.set(not (obj.displayLocalAxis.get()))

    def rotateToJointOrient(self):
        objs = pm.selected()
        for obj in objs:
            if isinstance(obj, pm.nt.Joint):
                rot = obj.rotate.get()
                obj.jointOrient.set(rot)
                obj.rotate.set(0, 0, 0)

    def zeroJointRotate(self):
        objs = pm.selected()
        for obj in objs:
            if isinstance(obj, pm.nt.Joint):
                obj.jointRotate.set(0, 0, 0)

    def zeroJointOrient(self):
        objs = pm.selected()
        for obj in objs:
            if isinstance(obj, pm.nt.Joint):
                obj.jointOrient.set(0, 0, 0)

    def zeroJointAxis(self):
        objs = pm.selected()
        for obj in objs:
            if isinstance(obj, pm.nt.Joint):
                obj.Axis.set(0, 0, 0)

    def editJointPivotTool(self):
        objs = pm.selected()
        pm.selectMode(co=True)
        pm.selectType(ra=True)
        pm.select(objs[0].rotateAxis, r=True)
        rotateCtx = pm.manipRotateContext(
            psc=pm.Callback(self.editJointPivotExit, objs)
        )
        pm.setToolTo(rotateCtx)

    def editJointPivotExit(self, objects):
        pm.select(objects, r=True)
        pm.selectMode(o=True)

    def showJointOrient(self):
        objs = pm.selected()
        for obj in objs:
            if isinstance(obj, pm.nt.Joint):
                obj.jox.showInChannelBox(not (obj.jox.isInChannelBox()))
                obj.joy.showInChannelBox(not (obj.joy.isInChannelBox()))
                obj.joz.showInChannelBox(not (obj.joz.isInChannelBox()))

    def setSSC(self):
        objs = pm.selected()
        for obj in objs:
            if isinstance(obj, pm.nt.Joint):
                obj.ssc.set(False)

    def checkIfPlanar(self):
        raise NotImplementedError

    def restoreRotation(self):
        objs = pm.selected()
        for obj in objs:
            if isinstance(obj, pm.nt.Joint):
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
        objs = pm.selected()
        for obj in objs:
            if isinstance(obj, pm.nt.Joint):
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
