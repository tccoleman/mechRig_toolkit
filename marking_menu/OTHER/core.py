"""Common rigging operations in a Marking Menu.

Ops currently are:t LA
- Transforms
- Joints
- Controllers
- Colors

Install:
1. Put riggingMenus.py in your Maya scripts directory or PYTHONPATH

Usage:
- Put it in your userSetup.py or just run from script editor

import riggingMenus
riggingMenus.RiggingMenu()

"""
import os
import json

import pymel.core as pm
import pymel.api as api

try:
    from PySide import QtGui
except ImportError as e:
    from PySide2 import QtGui


from utils import controls, transforms
reload(controls)


class RiggingMenu(object):
    menuName = 'RiggingMenu'

    def __init__(self):
        self.maintain_shape = True
        self.maintain_children = True
        self.rotate_axis = [1, 0, 0]
        self.negative_rotate = False

        self.cleanup()
        self.build()

    def cleanup(self):
        if pm.popupMenu(self.menuName, ex=True):
            pm.deleteUI(self.menuName)

    def build(self):
        menu = pm.popupMenu(self.menuName, mm=1, b=1, aob=1, ctl=1, alt=1, sh=0, p="viewPanes", pmc=self._buildMenu)

        return menu

    def _buildMenu(self, menu, parent):
        pm.popupMenu(self.menuName, e=True, dai=True)

        pm.menuItem(p=menu, l='Script Editor', c=pm.Callback(pm.mel.eval, 'ScriptEditor;'))
        pm.menuItem(p=menu, l='Node Editor', c=pm.Callback(pm.mel.eval, 'NodeEditorWindow;'))
        pm.menuItem(p=menu, l='Connection Editor', c=pm.Callback(pm.mel.eval, 'ConnectionEditor;'))
        pm.menuItem(p=menu, l='Outliner', c=pm.Callback(pm.mel.eval, 'OutlinerWindow;'))
        pm.menuItem(p=menu, d=True)
        pm.menuItem(p=menu, l='Paint Weights', c=pm.Callback(pm.mel.eval, 'ArtPaintSkinWeightsToolOptions;'))
        pm.menuItem(p=menu, d=True)

        for recentFile in pm.optionVar['RecentFilesList'][-3:]:
            pm.menuItem(p=menu, l=recentFile.split(os.sep)[-1], c=pm.Callback(pm.openFile, recentFile, force=True))

        self._buildControlMenu(menu, parent)
        self._buildJointMenu(menu, parent)
        self._buildColorMenu(menu, parent)
        self._buildTransformMenu(menu, parent)
        self._buildSkinningMenu(menu, parent)
        self._buildDisplayMenu(menu, parent)
        self._buildProjectMenu(menu, parent)
        self._buildTargetMenu(menu, parent)

    # S
    def set_maintain_shape(self, *args, **kwargs):
        self.maintain_shape = pm.menuItem(self.maintainShape, q=True, cb=True)

    def set_maintain_children(self, *args, **kwargs):
        self.maintain_children = pm.menuItem(self.maintainChildren, q=True, cb=True)

    def set_rotate_axis(self, *args, **kwargs):
        self.rotate_axis = [pm.menuItem(x, q=True, rb=True) for x in [self.rotateX, self.rotateY, self.rotateZ]]

    def set_negative_rotate(self, *args, **kwargs):
        self.negative_rotate = pm.menuItem(self.negativeRotate, q=True, cb=True)

    def _buildTransformMenu(self, menu, parent):
        transformMenu = pm.menuItem(p=menu, l='Transform', rp='S', subMenu=1)

        rotateAxis = pm.radioMenuItemCollection(p=transformMenu)
        self.rotateX = pm.menuItem(p=transformMenu, l='Rotate Around X', rb=self.rotate_axis[0], cl=rotateAxis, c=self.set_rotate_axis)
        self.rotateY = pm.menuItem(p=transformMenu, l='Rotate Around Y', rb=self.rotate_axis[1], cl=rotateAxis, c=self.set_rotate_axis)
        self.rotateZ = pm.menuItem(p=transformMenu, l='Rotate Around Z', rb=self.rotate_axis[2], cl=rotateAxis, c=self.set_rotate_axis)
        self.negativeRotate = pm.menuItem(p=transformMenu, l='Negative Rotate', cb=self.negative_rotate, c=self.set_negative_rotate)
        self.maintainChildren = pm.menuItem(p=transformMenu, l='Maintain Children Transforms', cb=self.maintain_children, c=self.set_maintain_children)
        self.maintainShape = pm.menuItem(p=transformMenu, l='Maintain Shape', cb=self.maintain_shape, c=self.set_maintain_shape)

        pm.menuItem(p=transformMenu, d=True)
        pm.menuItem(p=transformMenu, l='Show/Hide Pivot', c=pm.Callback(self.showPivot))
        pm.menuItem(p=transformMenu, l='Show/Hide Transform Attributes', c=pm.Callback(self.showTransformAttributes))
        pm.menuItem(p=transformMenu, l='Freeze Scale', c=pm.Callback(self.freezeScale))
        pm.menuItem(p=transformMenu, l='Locate Center Point', c=pm.Callback(self.locateCenterPoint))

        pm.menuItem(p=transformMenu, l='Match Transforms', rp='E', c=pm.Callback(self.matchTransform))
        pm.menuItem(p=transformMenu, l='Match Position', rp='NE', c=pm.Callback(self.matchTransform, rotate=False))
        pm.menuItem(p=transformMenu, l='Match Rotation', rp='SE', c=pm.Callback(self.matchTransform, translate=False))

        pm.menuItem(p=transformMenu, l='Zero Transforms', rp='W', c=pm.Callback(self.zeroTransform))
        pm.menuItem(p=transformMenu, l='Zero Position', rp='NW', c=pm.Callback(self.zeroTransform, rotate=False))
        pm.menuItem(p=transformMenu, l='Zero Rotation', rp='SW', c=pm.Callback(self.zeroTransform, translate=False))

        pm.menuItem(p=transformMenu, l='Rotate Transform 90', rp='N', c=pm.Callback(self.rotateNinety))

    # E
    def _buildColorMenu(self, menu, parent):
        colorMenu = pm.menuItem(p=menu, l='Colors', rp='E', subMenu=1)

        pm.menuItem(p=colorMenu, l='Red', rp='N', c=pm.Callback(self.colorSelected, [0.642, 0.108, 0.090]))
        pm.menuItem(p=colorMenu, l='Pink', rp='NE', c=pm.Callback(self.colorSelected, [1.000, 0.700, 0.700]))
        pm.menuItem(p=colorMenu, l='Purple', rp='E', c=pm.Callback(self.colorSelected, [0.429, 0.000, 0.800]))
        pm.menuItem(p=colorMenu, l='Blue', rp='SE', c=pm.Callback(self.colorSelected, [0.050, 0.050, 1.000]))
        pm.menuItem(p=colorMenu, l='Yellow', rp='S', c=pm.Callback(self.colorSelected, [0.900, 0.850, 0.000]))
        pm.menuItem(p=colorMenu, l='Green', rp='SW', c=pm.Callback(self.colorSelected, [0.000, 0.242, 0.000]))
        pm.menuItem(p=colorMenu, l='Orange', rp='NW', c=pm.Callback(self.colorSelected, [1.000, 0.400, 0.000]))

        pm.menuItem(p=colorMenu, l='Custom Color', c=pm.Callback(self.colorSelectedCustom))
        pm.menuItem(p=colorMenu, l='Copy/Paste Color', c=pm.Callback(self.copyPasteColor))

    # W
    def _buildJointMenu(self, menu, parent):
        jntMenu = pm.menuItem(p=menu, l='Joints', rp='W', subMenu=1)

        pm.menuItem(p=jntMenu, l='Disable Segment Scale Compensate', c=pm.Callback(self.setSSC))
        pm.menuItem(p=jntMenu, l='Check If Planar', c=pm.Callback(self.checkIfPlanar))
        pm.menuItem(p=jntMenu, l='Show/Hide Joint Orient', c=pm.Callback(self.showJointOrient))

        pm.menuItem(p=jntMenu, l='Create Joint Tool', rp='N', c=pm.Callback(pm.mel.eval, 'JointTool;'))
        pm.menuItem(p=jntMenu, l='Edit Joint Pivot Tool', rp='NE', c=pm.Callback(self.editJointPivotTool))

        rotationMenu = pm.menuItem(p=jntMenu, l='Rotations', rp='E', subMenu=1)
        pm.menuItem(p=rotationMenu, l='Freeze Rotations', rp='E', c=pm.Callback(self.freezeRotation))
        pm.menuItem(p=rotationMenu, l='Restore Rotations', rp='W', c=pm.Callback(self.restoreRotation))
        pm.menuItem(p=rotationMenu, l='Zero Joint Orient', rp='S', c=pm.Callback(self.zeroJointOrient))

    # SW
    def _buildSkinningMenu(self, menu, parent):
        skinMenu = pm.menuItem(p=menu, l='Skinning', rp='SW', subMenu=1)

        pm.menuItem(p=skinMenu, l='Rigid Paint', rp='W', c=pm.Callback(self.paintWeights))
        pm.menuItem(p=skinMenu, l='Export All Weights', rp='NE', c=pm.Callback(self.exportAllWeights))
        pm.menuItem(p=skinMenu, l='Export Selected Weights', rp='SE', c=pm.Callback(self.exportSelectedWeights))

    # N
    def _buildControlMenu(self, menu, parent):
        ctlMenu = pm.menuItem(p=menu, l='Controllers', rp='N', subMenu=1)

        pm.menuItem(p=ctlMenu, l='Square', rp='N', c=pm.Callback(controls.createControlsFromSelection, 'square'))
        pm.menuItem(p=ctlMenu, l='Circle', rp='E', c=pm.Callback(controls.createControlsFromSelection, 'circle'))
        pm.menuItem(p=ctlMenu, l='Hexagon', rp='S', c=pm.Callback(controls.createControlsFromSelection, 'hexagon'))
        pm.menuItem(p=ctlMenu, l='Dial', rp='W', c=pm.Callback(controls.createControlsFromSelection, 'dial'))
        pm.menuItem(p=ctlMenu, l='Cube', rp='SE', c=pm.Callback(controls.createControlsFromSelection, 'cube'))
        pm.menuItem(p=ctlMenu, l='Sphere', rp='SW', c=pm.Callback(controls.createControlsFromSelection, 'sphere'))
        pm.menuItem(p=ctlMenu, l='Triangle', rp='NE', c=pm.Callback(controls.createControlsFromSelection, 'triangle'))
        pm.menuItem(p=ctlMenu, l='Pyramid', rp='NW', c=pm.Callback(controls.createControlsFromSelection, 'pyramid'))

        pm.menuItem(p=ctlMenu, l='Select CVs', c=pm.Callback(controls.selectControlCVs))
        pm.menuItem(p=ctlMenu, l='Center CVs to Pivot', c=pm.Callback(controls.centerCVsToPivot))
        pm.menuItem(p=ctlMenu, l='Center Pivot to CVs', c=pm.Callback(controls.centerPivotToCVs))
        pm.menuItem(p=ctlMenu, d=True)
        pm.menuItem(p=ctlMenu, l='Rotate X 90', c=pm.Callback(transforms.rotateSelectedNodeComponents, [90, 0, 0]))
        pm.menuItem(p=ctlMenu, l='Rotate Y 90', c=pm.Callback(transforms.rotateSelectedNodeComponents, [0, 90, 0]))
        pm.menuItem(p=ctlMenu, l='Rotate Z 90', c=pm.Callback(transforms.rotateSelectedNodeComponents, [0, 0, 90]))
        pm.menuItem(p=ctlMenu, d=True)
        pm.menuItem(p=ctlMenu, l='Rotate X -90', c=pm.Callback(transforms.rotateSelectedNodeComponents, [-90, 0, 0]))
        pm.menuItem(p=ctlMenu, l='Rotate Y -90', c=pm.Callback(transforms.rotateSelectedNodeComponents, [0, -90, 0]))
        pm.menuItem(p=ctlMenu, l='Rotate Z -90', c=pm.Callback(transforms.rotateSelectedNodeComponents, [0, 0, -90]))
        pm.menuItem(p=ctlMenu, d=True)
        pm.menuItem(p=ctlMenu, l='Scale Up', c=pm.Callback(controls.scaleUpSelected) )
        pm.menuItem(p=ctlMenu, l='Scale Down', c=pm.Callback(controls.scaleDownSelected) )

    # SE
    def _buildDisplayMenu(self, menu, parent):
        displayMenu = pm.menuItem(p=menu, l='Display', rp='SE', subMenu=1)
        pm.menuItem(p=displayMenu, l='Polygons', rp='N', c="import pymel.core as pm;pm.modelEditor('modelPanel1', e=True, polymeshes=not(pm.modelEditor('modelPanel1', q=True, polymeshes=True)))")
        pm.menuItem(p=displayMenu, l='Nurbs CVs', rp='E', c="import pymel.core as pm;pm.toggle(cv=True)")
        pm.menuItem(p=displayMenu, l='Nurbs Curves', rp='S', c="import pymel.core as pm;pm.modelEditor('modelPanel1', e=True, nurbsCurves=not(pm.modelEditor('modelPanel1', q=True, nurbsCurves=True)))")

    # NE
    def _buildProjectMenu(self, menu, parent):
        projectMenu = pm.menuItem(p=menu, l='Project', rp='NE', subMenu=1)

    # NW
    def _buildTargetMenu(self, menu, parent):
        targetMenu = pm.menuItem(p=menu, l='Targets', rp='NW', subMenu=1)
        pm.menuItem(p=targetMenu, l='Apply Transform Target', rp='N')
        pm.menuItem(p=targetMenu, l='Apply Pole Vector Target', rp='E')
        pm.menuItem(p=targetMenu, l='Update Selected Targets')
        pm.menuItem(p=targetMenu, l='Update All Targets')

    def rotateComponents(self, rotation):
        for node in pm.selected():
            for shape in node.getShapes():
                if isinstance(shape, pm.nt.Mesh):
                    pm.rotate(shape.vtx, rotation, os=1)
                elif isinstance(shape, pm.nt.NurbsCurve):
                    pm.rotate(shape.cv, rotation, os=1)

    def locateCenterPoint(self):
        objs = pm.selected(fl=True)
        length = len(objs)

        sumOfPositions = pm.dt.Vector()

        for obj in objs:
            if isinstance(obj, pm.nt.Transform):
                pos = obj.getTranslation('world')
                sumOfPositions += pos
            elif isinstance(obj, pm.MeshVertex):
                pos = obj.getPosition('world')
                sumOfPositions += pos
            elif isinstance(obj, pm.MeshEdge):
                point0Pos = obj.getPoint(0, 'world')
                point1Pos = obj.getPoint(1, 'world')
                pos = pm.dt.Vector([(point0Pos.x+point1Pos.x)/2, (point0Pos.y+point1Pos.y)/2, (point0Pos.z+point1Pos.z)/2])
                sumOfPositions += pos
            elif isinstance(obj, pm.MeshFace):
                vertPositions = obj.getPoints('world')
                pos = pm.dt.Vector(vertPositions[0].center(*vertPositions[1:]))
                sumOfPositions += pos
            elif isinstance(obj, pm.NurbsCurveCV):
                pos = obj.getPosition('world')
                sumOfPositions += pos
            else:
                length -= 1

        centerPoint = sumOfPositions / length

        centerLocator = pm.spaceLocator()
        centerLocator.translate.set(centerPoint)

    def freezeScale(self):
        objs = pm.selected()

        hierarchy = {}
        for obj in objs:
            hierarchy[obj] = obj.getParent()
            children = obj.listRelatives(ad=True, type=pm.nt.Transform)
            for child in children:
                hierarchy[child] = child.getParent()

        for node in hierarchy.keys():
            node.setParent(None)
            pm.makeIdentity(node, t=0, r=0, s=1, n=0, apply=True)

        for k, v in hierarchy.iteritems():
            k.setParent(v)

    def rotateNinety(self):
        mirrorAxis = self.rotate_axis
        maintainChildren = self.maintain_children
        maintainShape = self.maintain_shape
        sign = self.negative_rotate

        rotVector = pm.dt.Vector(mirrorAxis) * 90.0
        if not sign:
            rotVector *= -1.0
        newRotation = pm.dt.EulerRotation(rotVector, unit='degrees').asQuaternion()

        objs = pm.selected()
        for obj in objs:
            children = []
            if maintainChildren:
                for child in obj.getChildren(type=pm.nt.Transform):
                    child.setParent(None)
                    children.append(child)
            obj.rotateBy(newRotation, 'preTransform')
            if children and maintainChildren:
                for child in children:
                    child.setParent(obj)
            if maintainShape:
                for shape in obj.getShapes():
                    if isinstance(shape, pm.nt.Mesh):
                        pm.rotate(shape.vtx, rotVector * -1.0, os=1)
                    elif isinstance(shape, pm.nt.NurbsCurve):
                        pm.rotate(shape.cv, rotVector * -1.0, os=1)

        pm.select(objs, r=True)

    def zeroTransform(self, translate=True, rotate=True):
        maintainChildren = self.maintain_children

        targets = pm.selected()

        if translate:
            for target in targets:
                children = []
                if maintainChildren:
                    for child in target.getChildren(type=pm.nt.Transform):
                        child.setParent(None)
                        children.append(child)

                target.translate.set(0, 0, 0)

                if children and maintainChildren:
                    for child in children:
                        child.setParent(target)

        if rotate:
            for target in targets:
                children = []
                if maintainChildren:
                    for child in target.getChildren(type=pm.nt.Transform):
                        child.setParent(None)
                        children.append(child)

                target.rotate.set(0, 0, 0)

                if children and maintainChildren:
                    for child in children:
                        child.setParent(target)

    def matchTransform(self, translate=True, rotate=True):
        maintainChildren = self.maintain_children

        source = pm.selected()[0]
        targets = pm.selected()[1:]

        if translate:
            if isinstance(source, pm.nt.Transform):
                pos = source.getTranslation('world')
            elif isinstance(source, pm.MeshVertex):
                pos = source.getPosition('world')
            elif isinstance(source, pm.MeshEdge):
                point0Pos = source.getPoint(0, 'world')
                point1Pos = source.getPoint(1, 'world')
                pos = pm.dt.Vector([(point0Pos.x+point1Pos.x)/2, (point0Pos.y+point1Pos.y)/2, (point0Pos.z+point1Pos.z)/2])
            elif isinstance(source, pm.MeshFace):
                vertPositions = source.getPoints('world')
                pos = pm.dt.Vector(vertPositions[0].center(*vertPositions[1:]))
            elif isinstance(source, pm.NurbsCurveCV):
                pos = source.getPosition('world')
            else:
                pos = None

            for target in targets:
                if pos is None:
                    if isinstance(source, pm.nt.NurbsCurve):
                        pos = source.closestPoint(target.getTranslation('world'), space='world')
                    if isinstance(source, pm.nt.Mesh):
                        pos = source.getClosestPoint(target.getTranslation('world'), space='world')[0]

                if isinstance(target, pm.nt.Transform):
                    children = []
                    if maintainChildren:
                        for child in target.getChildren(type=pm.nt.Transform):
                            child.setParent(None)
                            children.append(child)

                    target.setTranslation(pos, 'world')
                    pos = None

                    if children and maintainChildren:
                        for child in children:
                            child.setParent(target)

        if rotate:
            if isinstance(source, pm.nt.Transform):
                rot = source.getRotation('world')
            elif isinstance(source, pm.MeshVertex):
                u, v = source.getUV()
                follicle = pm.createNode('follicle')
                source.node().outMesh >> follicle.inputMesh
                follicle.parameterU.set(u)
                follicle.parameterV.set(v)
                rot = follicle.outRotate.get()
                pm.delete(follicle.getParent())
            elif isinstance(source, pm.MeshEdge):
                point0Pos = source.getPoint(0, 'world')
                point1Pos = source.getPoint(1, 'world')
                pos = pm.dt.Vector([(point0Pos.x+point1Pos.x)/2, (point0Pos.y+point1Pos.y)/2, (point0Pos.z+point1Pos.z)/2])
                print source.node().getUVAtPoint(pos, space='world')
                u, v = source.node().getUVAtPoint(pos, space='world')
                follicle = pm.createNode('follicle')
                source.node().outMesh >> follicle.inputMesh
                follicle.parameterU.set(u)
                follicle.parameterV.set(v)
                rot = follicle.outRotate.get()
                pm.delete(follicle.getParent())
            elif isinstance(source, pm.MeshFace):
                vertPositions = source.getPoints('world')
                pos = pm.dt.Vector(vertPositions[0].center(*vertPositions[1:]))
                u, v = source.node().getUVAtPoint(pos, space='world')[0]
                follicle = pm.createNode('follicle')
                source.node().outMesh >> follicle.inputMesh
                follicle.parameterU.set(u)
                follicle.parameterV.set(v)
                rot = follicle.outRotate.get()
                pm.delete(follicle.getParent())
            else:
                rot = None

            for target in targets:
                if rot is None:
                    if isinstance(source, pm.NurbsCurveCV):
                        pos = source.getPosition(space='world')
                        param = source.node().getParamAtPoint(pos, 'world')
                        normal = source.node().normal(param, 'world')
                        tangent = source.node().tangent(param, 'world')
                        binormal = (normal ^ tangent).normal()
                        rotMat = pm.dt.Matrix()
                        rotMat[0] = normal
                        rotMat[1] = binormal
                        rotMat[2] = tangent
                        rot = pm.dt.TransformationMatrix(rotMat).eulerRotation()
                        rot = [pm.dt.degrees(x) for x in rot]
                    if isinstance(source, pm.nt.NurbsCurve):
                        pos = source.closestPoint(target.getTranslation('world'), space='world')
                        param = source.getParamAtPoint(pos, 'world')
                        normal = source.normal(param, 'world')
                        tangent = source.tangent(param, 'world')
                        binormal = (normal ^ tangent).normal()
                        rotMat = pm.dt.Matrix()
                        rotMat[0] = normal
                        rotMat[1] = binormal
                        rotMat[2] = tangent
                        rot = pm.dt.TransformationMatrix(rotMat).eulerRotation()
                        rot = [pm.dt.degrees(x) for x in rot]
                    if isinstance(source, pm.nt.Mesh):
                        pos = source.getClosestPoint(target.getTranslation('world'), space='world')[0]
                        u, v = source.node().getUVAtPoint(pos, space='world')
                        follicle = pm.createNode('follicle')
                        source.node().outMesh >> follicle.inputMesh
                        follicle.parameterU.set(u)
                        follicle.parameterV.set(v)
                        rot = follicle.outRotate.get()
                        pm.delete(follicle.getParent())

                if isinstance(target, pm.nt.Transform):
                    children = []
                    if maintainChildren:
                        for child in target.getChildren(type=pm.nt.Transform):
                            child.setParent(None)
                            children.append(child)

                    target.setRotation(rot, 'world')
                    rot = None

                    if children and maintainChildren:
                        for child in children:
                            child.setParent(target)

    def showPivot(self):
        objs = pm.selected()
        for obj in objs:
            obj.displayLocalAxis.set(not(obj.displayLocalAxis.get()))

    def showTransformAttributes(self):
        objs = pm.selected()
        attrs = ['rotateAxis', 'rotatePivotTranslate', 'rotatePivot', 'scalePivotTranslate', 'scalePivot']
        axes = ['X', 'Y', 'Z']
        for obj in objs:
            for attr in attrs:
                for axis in axes:
                    a = '{}{}'.format(attr, axis)
                    a = obj.attr(a)
                    a.showInChannelBox(not(a.isInChannelBox()))

    def colorSelected(self, color):
        objs = pm.selected()
        for obj in objs:
            print "obj---" + obj
            for shape in obj.getShapes():
                print "shape---" + shape
                shape.overrideEnabled.set(True)
                shape.overrideRGBColors.set(True)
                shape.overrideColorRGB.set(*color)


    def colorSelectedCustom(self):
        pos = QtGui.QCursor.pos()
        colors = pm.colorEditor(position=[pos.x(), pos.y()])
        values = str(colors).split(' ')
        r, g, b, result = [x for x in values if x != '']
        if result:
            rgb = [float(x) for x in [r, g, b]]
            self.colorSelected(rgb)

    def copyPasteColor(self):
        objs = pm.selected()
        source = objs[0]
        color = source.overrideColorRGB.get()
        targets = objs[1:]
        for obj in targets:
            obj.overrideEnabled.set(True)
            obj.overrideRGBColors.set(True)
            obj.overrideColorRGB.set(*color)

    def zeroJointOrient(self):
        objs = pm.selected()
        for obj in objs:
            if isinstance(obj, pm.nt.Joint):
                obj.jointOrient.set(0, 0, 0)

    def editJointPivotTool(self):
        objs = pm.selected()
        pm.selectMode(co=True)
        pm.selectType(ra=True)
        pm.select(objs[0].rotateAxis, r=True)

        rotateCtx = pm.manipRotateContext(psc=pm.Callback(self.editJointPivotExit, objs))
        pm.setToolTo(rotateCtx)

    def editJointPivotExit(self, objects):
        pm.select(objects, r=True)
        # self.freezeRotation()
        pm.selectMode(o=True)

    def clearMirrorData(self):
        objs = pm.selected()
        for obj in objs:
            if obj.hasAttr('mirrorNode'):
                obj.deleteAttr('mirrorNode')

    def clearLiveMirror(self):
        objs = pm.selected()

        for obj in objs:
            outputNodes = obj.translate.outputs()
            for x in outputNodes:
                if isinstance(x, pm.nt.SymmetryConstraint):
                    pm.delete(x)

            inputNodes = obj.translate.inputs()
            for x in inputNodes:
                if isinstance(x, pm.nt.SymmetryConstraint):
                    pm.delete(x)

    def createMirrorConstraint(self, source, target, axis='X'):
        cnt = pm.createNode('symmetryConstraint')

        axisAttr = '{}Axis'.format(axis.lower())
        axisChildAttr = '{}ChildAxis'.format(axis.lower())

        cnt.attr(axisAttr).set(True)
        cnt.attr(axisChildAttr).set(True)

        source.jointOrient >> cnt.targetJointOrient
        source.rotate >> cnt.targetRotate
        source.translate >> cnt.targetTranslate
        source.scale >> cnt.targetScale
        source.parentMatrix >> cnt.targetParentMatrix
        source.worldMatrix >> cnt.targetWorldMatrix
        source.rotateOrder >> cnt.targetRotateOrder

        target.parentInverseMatrix >> cnt.constraintInverseParentWorldMatrix

        cnt.constraintTranslate >> target.translate
        cnt.constraintRotate >> target.rotate
        cnt.constraintScale >> target.scale
        cnt.constraintRotateOrder >> target.rotateOrder
        cnt.constraintJointOrient >> target.jointOrient

        cnt.setParent(target)
        cnt.translate.set(0, 0, 0)
        cnt.rotate.set(0, 0, 0)
        cnt.visibility.set(False)

        return cnt

    def mirrorJoint(self, mirrorAxis, mirrorType, liveConnect=True):
        xAxis = [1, 0, 0]
        yAxis = [0, 1, 0]
        zAxis = [0, 0, 1]

        mirrorAxis = [pm.menuItem(axis, q=True, rb=True) for axis in mirrorAxis]
        mirrorType = [pm.menuItem(axis, q=True, rb=True) for axis in mirrorType]

        objs = pm.selected()
        mirrorObjs = []

        # mirror nodes
        for obj in objs:
            if obj.hasAttr('mirrorNode') and obj.mirrorNode.get() is not None:
                mirrorObjs.append(obj.mirrorNode.get())
                continue

            mirrorObj = pm.duplicate(obj)[0]
            mirrorObjs.append(mirrorObj)

            if not obj.hasAttr('mirrorNode'):
                mirrorObj.addAttr('mirrorNode', at='message')
                obj.addAttr('mirrorNode', at='message')

            obj.message >> mirrorObj.mirrorNode
            mirrorObj.message >> obj.mirrorNode

            children = mirrorObj.getChildren(type=pm.nt.Transform)
            if children:
                pm.delete(children)

        # mirror parenting
        for mirrorObj in mirrorObjs:
            parent = mirrorObj.mirrorNode.get().getParent()
            if parent is not None:
                if parent.hasAttr('mirrorNode') and parent.mirrorNode.get() is not None:
                    mirrorParent = parent.mirrorNode.get()
                    mirrorObj.setParent(mirrorParent)

        # mirror transforms
        for mirrorObj in mirrorObjs:

            if mirrorAxis == zAxis:
                mirrorAxis = 'Z'
            elif mirrorAxis == yAxis:
                mirrorAxis = 'Y'
            else:
                mirrorAxis = 'X'

            constraintNode = self.createMirrorConstraint(mirrorObj.mirrorNode.get(), mirrorObj, mirrorAxis)
            if mirrorType == [0, 1]:
                mirrorObj.mirrorNode.get().jointOrient // constraintNode.targetJointOrient
                constraintNode.targetJointOrient.set(180, 0, 0)

            if not liveConnect:
                pos = mirrorObj.getTranslation('world')
                rot = mirrorObj.getRotation('world')
                sca = mirrorObj.getScale()

                pm.delete(constraintNode)

                mirrorObj.setTranslation(pos, 'world')
                mirrorObj.setRotation(rot, 'world')
                mirrorObj.setScale(sca)

    def checkIfPlanar(self):
        raise NotImplementedError

    def restoreRotation(self):
        objs = pm.selected()
        for obj in objs:
            if isinstance(obj, pm.nt.Joint):
                rot = obj.rotate.get()
                ra = obj.rotateAxis.get()
                jo = obj.jointOrient.get()

                rotMatrix = pm.dt.EulerRotation(rot, unit='degrees').asMatrix()
                raMatrix = pm.dt.EulerRotation(ra, unit='degrees').asMatrix()
                joMatrix = pm.dt.EulerRotation(jo, unit='degrees').asMatrix()

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

                rotMatrix = pm.dt.EulerRotation(rot, unit='degrees').asMatrix()
                raMatrix = pm.dt.EulerRotation(ra, unit='degrees').asMatrix()
                joMatrix = pm.dt.EulerRotation(jo, unit='degrees').asMatrix()

                rotationMatrix = rotMatrix * raMatrix * joMatrix
                tmat = pm.dt.TransformationMatrix(rotationMatrix)
                newRotation = tmat.eulerRotation()
                newRotation = [pm.dt.degrees(x) for x in newRotation.asVector()]

                obj.rotate.set(0, 0, 0)
                obj.rotateAxis.set(0, 0, 0)
                obj.jointOrient.set(newRotation)

    def setSSC(self):
        objs = pm.selected()
        for obj in objs:
            if isinstance(obj, pm.nt.Joint):
                obj.ssc.set(False)

    def showJointOrient(self):
        objs = pm.selected()
        for obj in objs:
            if isinstance(obj, pm.nt.Joint):
                obj.jox.showInChannelBox(not(obj.jox.isInChannelBox()))
                obj.joy.showInChannelBox(not(obj.joy.isInChannelBox()))
                obj.joz.showInChannelBox(not(obj.joz.isInChannelBox()))

    def paintWeights(self):
        # ctx = pm.artAttrSkinPaintCtx(val=1.0, sao='absolute', stP='solid')
        # pm.setToolTo(ctx)
        pm.mel.eval('artSetToolAndSelectAttr("artAttrCtx", "skinCluster.mannequin_mod:mannequin_skcl.paintWeights");')
        pm.mel.eval('artUpdateStampProfile solid artAttrSkinPaintCtx;')
        pm.mel.eval('artSkinSetSelectionValue 1 false artAttrSkinPaintCtx artAttrSkin;')
        pm.mel.eval('artAttrPaintOperation artAttrSkinPaintCtx Replace;')

    def exportAllWeights(self):
        sceneName = pm.sceneName()
        if sceneName == '':
            raise ValueError('Scene not saved')

        try:
            meshes = [x for x in pm.ls(type=[pm.nt.Mesh, pm.nt.NurbsCurve, pm.nt.NurbsSurface])]
            meshesWithSkin = [x for x in meshes if self.getSkin(x)]
            weightsFilePath = os.path.join(sceneName.dirname(), sceneName.basename().replace(sceneName.ext, '.json'))
            self.saveSkinWeights(weightsFilePath, meshesWithSkin)
        except Exception as e:
            raise Exception('Unable to export weights: {0}'.format(e))

    def exportSelectedWeights(self):
        sceneName = pm.sceneName()
        if sceneName == '':
            raise ValueError('Scene not saved')

        try:
            meshes = [x.getShape() for x in pm.selected()]
            meshesWithSkin = [x for x in meshes if self.getSkin(x)]
            weightsFilePath = os.path.join(sceneName.dirname(), sceneName.basename().replace(sceneName.ext, '.json'))
            self.saveSkinWeights(weightsFilePath, meshesWithSkin)
        except Exception as e:
            raise Exception('Unable to export weights: {0}'.format(e))

    def getSkin(self, shape):
        result = []
        for s in shape.history(pdo=1, il=2):
            if isinstance(s, pm.nt.SkinCluster):
                result.append(s)

        return result

    def saveSkinWeights(self, filepath, meshes):
        data = {}
        for mesh in meshes:
            if not isinstance(object, pm.PyNode):
                mesh = pm.PyNode(mesh)
            k = mesh.longName()
            pm.displayInfo("Getting weights for {0}".format(mesh))
            # TODO: only supports a single skin cluster per shape
            skin = self.getSkin(mesh)[0]
            if skin:
                data[k] = self.getSkinWeights(skin)
            else:
                pm.displayInfo("Could not find skin cluster for {0}".format(mesh))

        with open(filepath, 'w') as f:
            json.dump(data, f)

        pm.displayInfo("Saved skin weights for {0} mesh(es) to file {1}".format(len(meshes), filepath))

    def getSkinWeights(self, skin, indices=None, influences=None):
        '''
        Get a list of all vertices and associated weights
        Returns:
            [(vert,weights)]
        '''
        data = []
        _influences = self.getSkinInfluences(skin)
        influences = _influences
        # getAttr is faster
        weightListPlug = skin.wl.__apiobject__()
        infIDs = api.MIntArray()
        weightListPlug.getExistingArrayAttributeIndices(infIDs)
        for vert in infIDs:
            if indices is not None and vert not in indices:
                continue
            weights = []
            weightsPlug = skin.wl[vert].weights.__apiobject__()
            # loop through all weights
            for i in xrange(weightsPlug.numElements()):
                # get the logical index, which will match the indices of influences list
                logical = weightsPlug[i].logicalIndex()
                if logical in influences:
                    weights.append((influences[logical], weightsPlug[i].asFloat()))
            data.append((vert, weights))
        return data

    def getSkinInfluences(self, skin):
        influences = {}
        fn = api.MFnSkinCluster(skin.__apiobject__())
        inflPaths = api.MDagPathArray()
        fn.influenceObjects(inflPaths)
        for i in xrange(inflPaths.length()):
            val = inflPaths[i].fullPathName()
            influences[fn.indexForInfluenceObject(inflPaths[i])] = val
        return influences
