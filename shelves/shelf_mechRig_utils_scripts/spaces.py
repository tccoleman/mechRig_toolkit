import logging
import os

# Import Maya modules
import maya.cmds as cmds
import maya.OpenMaya as api

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

SPACEATTR = "spaces"

# Load plug-in dependencies
if not cmds.pluginInfo("matrixNodes", q=True, loaded=True):
    cmds.loadPlugin("matrixNodes", quiet=True)


def set_space_network_name(ctl, space_name, key=True, keyPrevious=True):
    """Select any control in space network and run to set all spaces in that space_network to the same space

    set_space_network_name("lf_tentAEnd_ctl", "parent", key=False, keyPrevious=False)
    """
    main_ctl = ""
    if cmds.objExists(ctl):
        ctl_list = list()
        # Tip control is selected
        if cmds.attributeQuery("space_network", node=ctl, exists=True):
            main_ctl = ctl
        # Network child control is selected
        else:
            cxns = cmds.listConnections("{}.message".format(ctl), s=False, d=True)
            if cxns:
                for cxn in cxns:
                    if cmds.attributeQuery("space_network", node=cxn, exists=True):
                        main_ctl = cxn
        if main_ctl:
            ctl_list_all = cmds.listConnections("{}.space_network".format(main_ctl))
            ctl_list = list(set(ctl_list_all))

        if ctl_list:
            for ctlNode in ctl_list:
                if cmds.attributeQuery(SPACEATTR, node=ctlNode, exists=True):
                    set_space_name(
                        ctlNode, space_name, key=key, keyPrevious=keyPrevious
                    )


def set_space_name(node, space_name, space_attr="spaces", key=True, keyPrevious=True):
    """Set a node's space by name

    set_space_name("lf_tentAEnd_ctl", "master")
    """
    enumStr = cmds.attributeQuery(space_attr, node=node, listEnum=True)[0]
    enumList = enumStr.split(":")
    index = enumList.index(space_name)

    curFrame = cmds.currentTime(q=True)
    curSpace = cmds.getAttr("{}.{}".format(node, space_attr))

    # Get current transform of ctrl
    wsPos = cmds.xform(node, query=True, ws=True, t=True)
    wsOri = cmds.xform(node, query=True, ws=True, ro=True)
    valT = cmds.getAttr(node + ".translate")[0]
    valR = cmds.getAttr(node + ".rotate")[0]

    # Key previous frame
    if key and keyPrevious:
        prevKey = cmds.findKeyframe(
            node + "." + space_attr, time=(curFrame, curFrame), which="previous"
        )
        if prevKey != curFrame - 1:
            cmds.setKeyframe(
                node + "." + space_attr,
                time=curFrame - 1,
                value=curSpace,
                itt="clamped",
                ott="step",
            )
        for i, attr in enumerate(["tx", "ty", "tz"]):
            cmds.setKeyframe(
                node + "." + attr,
                time=curFrame - 1,
                value=valT[i],
                itt="clamped",
                ott="step",
            )
        for i, attr in enumerate(["rx", "ry", "rz"]):
            cmds.setKeyframe(
                node + "." + attr,
                time=curFrame - 1,
                value=valR[i],
                itt="clamped",
                ott="step",
            )

    cmds.setAttr("%s.%s" % (node, space_attr), index)

    # Now that we're in the next space, set the transform back to the previous pos/ori
    cmds.xform(node, ws=True, a=True, t=[wsPos[0], wsPos[1], wsPos[2]])
    cmds.xform(node, ws=True, a=True, ro=[wsOri[0], wsOri[1], wsOri[2]])

    # Key current frame
    if key:
        for i, attr in enumerate([space_attr, "tx", "ty", "tz", "rx", "ry", "rz"]):
            cmds.setKeyframe(node + "." + attr, itt="clamped", ott="step")

    log.info('Set space for "%s" to "%s"...' % (node, space_name))


def cycleSpaceUI():
    sel = cmds.ls(selection=True)

    if sel:
        for item in sel:
            if cmds.attributeQuery("spaces", node=item, exists=True):
                result = cmds.confirmDialog(
                    title="Confirm",
                    message="Key current and previous frames?",
                    button=["Yes", "No"],
                    defaultButton="Yes",
                    cancelButton="No",
                    dismissString="No",
                )
                if "Yes" in result:
                    cycleControlSpace(key=True, keyPrevious=True)

                elif "No" in result:
                    cycleControlSpace(key=False, keyPrevious=False)

                else:
                    pass
            else:
                log.warning("No spaces attribute on {}, skipping...".format(item))


def cycleControlSpace(key=True, keyPrevious=True):
    """Cycles through a control's space while maintaining offsets between spaces

    Select animation control with "space" attribute and run:

    # To change space AND keyframe previous and current frames
    cycleControlSpace(key=True, keyPrevious=True)

    # To change space without setting keyframes
    cycleControlSpace(key=False, keyPrevious=False)
    """
    selection = cmds.ls(selection=True)

    if selection:
        for ctrl in selection:
            # Get the proper space attr name as some rigs use "Space" and others use "space"
            spaceAttrName = ""
            if cmds.attributeQuery("spaces", exists=True, node=ctrl):
                spaceAttrName = "spaces"

            elif cmds.attributeQuery("Space", exists=True, node=ctrl):
                spaceAttrName = "Space"

            else:
                log.error("Cannot find spaces attribute on selected control!")
                return

            curFrame = cmds.currentTime(q=True)
            curSpace = cmds.getAttr(ctrl + "." + spaceAttrName)

            # Get current space ctrl info
            curPos = cmds.xform(ctrl, q=True, ws=True, rp=True)
            curRot = cmds.xform(ctrl, q=True, ws=True, ro=True)
            valT = cmds.getAttr(ctrl + ".translate")[0]
            valR = cmds.getAttr(ctrl + ".rotate")[0]

            # key previous frame
            if key and keyPrevious:
                prevKey = cmds.findKeyframe(
                    ctrl + "." + spaceAttrName,
                    time=(curFrame, curFrame),
                    which="previous",
                )
                if prevKey != curFrame - 1:
                    cmds.setKeyframe(
                        ctrl + "." + spaceAttrName,
                        time=curFrame - 1,
                        value=curSpace,
                        itt="clamped",
                        ott="step",
                    )
                for i, attr in enumerate(["tx", "ty", "tz"]):
                    cmds.setKeyframe(
                        ctrl + "." + attr,
                        time=curFrame - 1,
                        value=valT[i],
                        itt="clamped",
                        ott="step",
                    )
                for i, attr in enumerate(["rx", "ry", "rz"]):
                    cmds.setKeyframe(
                        ctrl + "." + attr,
                        time=curFrame - 1,
                        value=valR[i],
                        itt="clamped",
                        ott="step",
                    )

            # Get current transform of ctrl
            wsPos = cmds.xform(ctrl, query=True, ws=True, t=True)
            wsOri = cmds.xform(ctrl, query=True, ws=True, ro=True)

            # Query the space attr and find the next space to cycle to
            spaceEnum = cmds.attributeQuery(spaceAttrName, listEnum=True, node=ctrl)[0]
            spaceEnumList = spaceEnum.split(":")
            currentSpace = cmds.getAttr("%s.%s" % (ctrl, spaceAttrName), asString=True)
            spaceIndex = spaceEnumList.index(currentSpace)
            nextSpaceIndex = spaceIndex + 1
            if nextSpaceIndex > len(spaceEnumList) - 1:
                nextSpaceIndex = 0

            cmds.setAttr("%s.%s" % (ctrl, spaceAttrName), nextSpaceIndex)

            # Now that we're in the next space, set the transform back to the previous pos/ori
            cmds.xform(ctrl, ws=True, a=True, t=[wsPos[0], wsPos[1], wsPos[2]])
            cmds.xform(ctrl, ws=True, a=True, ro=[wsOri[0], wsOri[1], wsOri[2]])

            # key current frame
            if key:
                for i, attr in enumerate(
                    [spaceAttrName, "tx", "ty", "tz", "rx", "ry", "rz"]
                ):
                    cmds.setKeyframe(ctrl + "." + attr, itt="clamped", ott="step")

            log.info(
                "Cycled space for %s to %s..." % (ctrl, spaceEnumList[nextSpaceIndex])
            )

    else:
        log.error("Nothing selected, a control with a spaces attribute and try again!")


def create(
    spaceNode,
    spaceSwitch=None,
    parent=None,
    mode="parent",
    master_node="Main",
    verbose=False,
):
    """
    other modes: 'orient', 'point'
    nodes in the network:
    spaceGrp:        node to group the space targets (usually parented to the noXform_grp) 'Lf_arm_ikh_zeroSpaces'
    spaceSwitch:     node used to mamage switch (usually a control) 'Lf_arm_ikh_ctrl'
    spaceNode:       node that gets constrained to the various space targets (usually a parent of the control node) 'Lf_arm_ikh_zero'
    spaceConstraint: constraint node used to switch spaces 'Lf_arm_ikh_zero_parentConstraint1'
    """

    if verbose == True:
        log.info("creating space node for %s" % spaceNode)

    if not spaceSwitch:
        spaceSwitch = spaceNode

    if not cmds.objExists(spaceNode + ".spaceGrp"):
        # Space Group
        grp = cmds.createNode("transform", n=spaceNode + "Spaces", parent=parent)
        cmds.setAttr(grp + ".inheritsTransform", False)
        decomposeMatrix = cmds.createNode("decomposeMatrix")
        cmds.connectAttr(spaceNode + ".parentMatrix", decomposeMatrix + ".inputMatrix")
        cmds.connectAttr(decomposeMatrix + ".outputTranslate", grp + ".translate")
        cmds.connectAttr(decomposeMatrix + ".outputRotate", grp + ".rotate")
        cmds.connectAttr(decomposeMatrix + ".outputScale", grp + ".scale")

        # Initial Space = MasterOffset
        cmds.addAttr(
            spaceSwitch,
            ln=SPACEATTR,
            attributeType="enum",
            enumName="master",
            keyable=True,
        )
        masterSpace = cmds.createNode("transform", name=grp + "_master", parent=grp)
        matchPose(spaceNode, masterSpace)

        if not cmds.objExists(master_node):
            cmds.createNode("transform", name=master_node)
        cmds.parentConstraint(master_node, masterSpace, mo=True)
        # cmds.parentConstraint("Main", masterSpace, mo=True)
        lockAndHide(["t", "r", "s", "v"], masterSpace)

        # Space Constraint
        if mode == "point":
            constraint = cmds.pointConstraint(masterSpace, spaceNode, mo=True)[0]
        if mode == "orient":
            constraint = cmds.orientConstraint(masterSpace, spaceNode, mo=True)[0]
        else:
            constraint = cmds.parentConstraint(masterSpace, spaceNode, mo=True)[0]

        # Message Attrs (for tracing network)
        cmds.addAttr(spaceNode, ln="spaceGrp", at="message", keyable=True)
        cmds.connectAttr(grp + ".message", spaceNode + ".spaceGrp")

        cmds.addAttr(spaceSwitch, ln="spaceNode", at="message", keyable=True)
        cmds.connectAttr(spaceNode + ".message", spaceSwitch + ".spaceNode")

        cmds.addAttr(spaceNode, ln="spaceConstraint", at="message", keyable=True)
        cmds.connectAttr(constraint + ".message", spaceNode + ".spaceConstraint")

        cmds.addAttr(spaceNode, ln="spaceSwitch", at="message", keyable=True)
        cmds.connectAttr(spaceSwitch + "." + SPACEATTR, spaceNode + ".spaceSwitch")

        return spaceNode

    else:
        log.info("spaces.create: " + spaceNode + "already exists. Use spaces.add")
        return None


def matchPose(src, dst, poseType="pose"):
    """
    Match dst transform to src transform (follows maya constraint argument order: src, dst)
    """

    if poseType == "position":
        position = cmds.xform(src, query=True, worldSpace=True, rotatePivot=True)
        cmds.xform(dst, worldSpace=True, translation=position)

    elif poseType == "rotation":
        rotation = cmds.xform(src, query=True, worldSpace=True, rotation=True)
        cmds.xform(dst, worldSpace=True, rotation=rotation)

    elif poseType == "scale":
        scale = cmds.xform(src, query=True, worldSpace=True, scale=True)
        cmds.xform(dst, worldSpace=True, scale=scale)

    elif poseType == "pose":
        pivot = cmds.xform(src, query=True, worldSpace=True, rotatePivot=True)
        matrix = cmds.xform(src, query=True, worldSpace=True, matrix=True)
        matrix[12] = pivot[0]
        matrix[13] = pivot[1]
        matrix[14] = pivot[2]
        cmds.xform(dst, worldSpace=True, matrix=matrix)


def getNodes(spaceNode):
    """ """

    if not cmds.objExists(spaceNode):
        log.info(
            "spaces.getNodes: "
            + spaceNode
            + " does not exist, please create use spaces.create"
        )
        return None

    if (
        cmds.objExists(spaceNode + ".spaceGrp")
        and cmds.objExists(spaceNode + ".spaceSwitch")
        and cmds.objExists(spaceNode + ".spaceConstraint")
    ):
        spaceGrp = cmds.listConnections(spaceNode + ".spaceGrp")[0]
        spaceSwitch = cmds.listConnections(spaceNode + ".spaceSwitch")[0]
        spaceConstraint = cmds.listConnections(spaceNode + ".spaceConstraint")[0]

        return spaceGrp, spaceSwitch, spaceConstraint

    else:
        log.info(
            "spaces.getNodes: no space attrs exist on "
            + spaceNode
            + ", please create use spaces.create"
        )
        return None


def getSpaceNode(ctrl):
    if cmds.objExists(ctrl + ".spaceNode"):
        spaceNode = cmds.listConnections(ctrl + ".spaceNode")[0]
        return spaceNode
    else:
        cmds.warning("spaces.getSpaceNode: could not find spaceNetwork for " + ctrl)
        return None


def connect(constraint, spaceSwitch):
    """ """

    # get info from constraint
    conType = cmds.objectType(constraint)
    if conType == "pointConstraint":
        aliasList = cmds.pointConstraint(constraint, q=True, weightAliasList=True)
        targetList = cmds.pointConstraint(constraint, q=True, targetList=True)
    if conType == "orientConstraint":
        aliasList = cmds.orientConstraint(constraint, q=True, weightAliasList=True)
        targetList = cmds.orientConstraint(constraint, q=True, targetList=True)
    else:
        aliasList = cmds.parentConstraint(constraint, q=True, weightAliasList=True)
        targetList = cmds.parentConstraint(constraint, q=True, targetList=True)

    for i in range(len(aliasList)):
        # Create conditionNode to map constraint weights
        condNode = targetList[i] + "_condition"
        if cmds.objExists(condNode):
            # recreate if it exists
            cmds.delete(condNode)
        cmds.createNode("condition", n=condNode)

        cmds.setAttr(condNode + ".operation", 0)
        cmds.setAttr(condNode + ".secondTerm", i)
        cmds.connectAttr(spaceSwitch + "." + SPACEATTR, condNode + ".firstTerm", f=True)
        cmds.setAttr(condNode + ".colorIfTrueR", 1)
        cmds.setAttr(condNode + ".colorIfFalseR", 0)
        cmds.connectAttr(
            condNode + ".outColorR", constraint + "." + aliasList[i], f=True
        )


def add(spaceNode, target, name=None, mode="parent"):
    """ """

    if not name:
        space = target
    else:
        space = name

    # Get space node network
    spaceGrp, spaceSwitch, spaceConstraint = getNodes(spaceNode)

    # See if mode is compatible
    conType = cmds.objectType(spaceConstraint)
    if not conType.__contains__(mode):
        cmds.warning(
            "spaces.add: cannot add " + mode + "Constraint target to a " + conType
        )
        return None

    # Check current spaces
    curSpaces = cmds.attributeQuery(SPACEATTR, node=spaceSwitch, listEnum=True)[
        0
    ].split(":")
    if space in curSpaces or target in curSpaces:
        log.info(
            'spaces.add: "'
            + spaceSwitch
            + '" already has a "'
            + space
            + '" space, skipping...'
        )
        return None

    # Add enum space
    cmds.addAttr(
        spaceSwitch + "." + SPACEATTR, e=True, enumName=":".join(curSpaces + [space])
    )

    # Add spaceTarget in space of target object
    spaceTarget = cmds.createNode(
        "transform", name=spaceGrp + "_" + space, parent=spaceGrp
    )
    matchPose(spaceNode, spaceTarget)

    cmds.parentConstraint(target, spaceTarget, mo=True)
    lockAndHide(["t", "r", "s", "v"], spaceTarget)

    # Add target to spaceNode constraint
    if mode == "orient":
        spaceConstraint = cmds.orientConstraint(spaceTarget, spaceNode, mo=True)[0]
    elif mode == "point":
        spaceConstraint = cmds.pointConstraint(spaceTarget, spaceNode, mo=True)[0]
    else:
        spaceConstraint = cmds.parentConstraint(spaceTarget, spaceNode, mo=True)[0]

    # Update weight connections
    connect(spaceConstraint, spaceSwitch)

    return spaceTarget


def remove(spaceNode, space):
    """ """

    # Get space node network
    spaceGrp, spaceSwitch, spaceConstraint = getNodes(spaceNode)

    # If space is string, get the int
    spaceInt = space
    if isinstance(space, basestring):
        enumNames = cmds.attributeQuery(SPACEATTR, node=spaceSwitch, listEnum=True)[0]
        enumNameList = enumNames.split(":")
        if space in enumNameList:
            spaceInt = enumNameList.index(space)
    if not isinstance(space, int):
        log.info(
            'spaces.remove: "'
            + space
            + '" does not appear to belong to "'
            + spaceNode
            + '", skipping...'
        )
        return

    # Get currently set space and current space names
    curSpace = cmds.getAttr(spaceSwitch + "." + SPACEATTR)
    curSpaces = cmds.attributeQuery(SPACEATTR, node=spaceSwitch, listEnum=True)[
        0
    ].split(":")
    if spaceInt >= len(curSpaces):
        log.info(
            'spaces.remove: "'
            + space
            + '" does not have a space at this index '
            + str(spaceInt)
        )
        return
    newSpaces = [curSpaces[i] for i in range(len(curSpaces)) if i != space]

    # Update enum attr
    cmds.addAttr(spaceSwitch + "." + SPACEATTR, e=True, enumName=":".join(newSpaces))

    # Delete dead spaceTarget node
    spaceTargets = cmds.listRelatives(spaceGrp, c=True, type="transform")
    cmds.delete(spaceTargets[spaceInt])

    # Delete entire network if only one space
    if len(curSpaces) == 1:
        cmds.deleteAttr(spaceSwitch + "." + SPACEATTR)
        cmds.deleteAttr(spaceSwitch + ".spaceSwitch")
        cmds.deleteAttr(spaceSwitch + ".spaceNode")
        cmds.deleteAttr(spaceSwitch + ".spaceGrp")
        cmds.deleteAttr(spaceSwitch + ".spaceConstraint")
        cmds.delete(spaceGrp)
        return

    # Update weight connections
    connect(spaceConstraint, spaceSwitch)

    if space == curSpace:
        cmds.dgdirty(a=True)

    return spaceTarget


def snapAndKey(ctrl, space, key=True, keyPrevious=True):
    if isinstance(space, basestring):
        space = attribute.getEnumIndex(ctrl + "." + SPACEATTR, space)

    spaceNode = getSpaceNode(ctrl)

    # Get space node network
    spaceGrp, spaceSwitch, spaceConstraint = getNodes(spaceNode)

    curFrame = cmds.currentTime(q=True)
    curSpace = cmds.getAttr(spaceSwitch + "." + SPACEATTR)

    # Get current space ctrl info
    curPos = cmds.xform(spaceSwitch, q=True, ws=True, rp=True)
    curRot = cmds.xform(spaceSwitch, q=True, ws=True, ro=True)
    valT = cmds.getAttr(spaceSwitch + ".translate")[0]
    valR = cmds.getAttr(spaceSwitch + ".rotate")[0]

    # key previous frame
    keyMsg = ""
    if key and keyPrevious:
        prevKey = cmds.findKeyframe(
            spaceSwitch + "." + SPACEATTR, time=(curFrame, curFrame), which="previous"
        )
        if prevKey != curFrame - 1:
            cmds.setKeyframe(
                spaceSwitch + "." + SPACEATTR,
                time=curFrame - 1,
                value=curSpace,
                itt="clamped",
                ott="step",
            )
        for i, attr in enumerate(["tx", "ty", "tz"]):
            cmds.setKeyframe(
                spaceSwitch + "." + attr,
                time=curFrame - 1,
                value=valT[i],
                itt="clamped",
                ott="step",
            )
        for i, attr in enumerate(["rx", "ry", "rz"]):
            cmds.setKeyframe(
                spaceSwitch + "." + attr,
                time=curFrame - 1,
                value=valR[i],
                itt="clamped",
                ott="step",
            )

    # switch to new space
    cmds.setAttr(spaceSwitch + "." + SPACEATTR, space)
    cmds.xform(spaceSwitch, ws=True, t=curPos)
    cmds.xform(spaceSwitch, ws=True, ro=curRot)

    # key current frame
    if key:
        keyMsg = " & key"
        for i, attr in enumerate([SPACEATTR, "tx", "ty", "tz", "rx", "ry", "rz"]):
            cmds.setKeyframe(spaceSwitch + "." + attr, itt="clamped", ott="step")

    # log.info message
    msg = "spaces: snap" + keyMsg + ": "
    oldSpace = cmds.attributeQuery(SPACEATTR, node=spaceSwitch, listEnum=True)[0].split(
        ":"
    )[curSpace]
    newSpace = cmds.attributeQuery(SPACEATTR, node=spaceSwitch, listEnum=True)[0].split(
        ":"
    )[space]
    msg += oldSpace + " -> " + newSpace
    log.info(msg)


def lockAndHide(attrPath, node=None):
    """
    Wrapper for lock and hide functions
    Lock and Hide attribute or a list of attributes

    Example:
        from rigging.utils import attribute
        attribute.lock(['tx','ty'], 'transform1')
        # or
        attribute.lock('transform1.translateX')
    Args:
        attrPath (str): either a list of attr names ['tx','ty'] or a complete path 'transform1.translateY'
        node (str): name of the maya node. not needed if a full attr path is given in attrPath
    """
    hide(attrPath, node)
    lock(attrPath, node)


def hide(attrPath, node=None):
    """
    Hide attribute in the channel box and make it not keyable

    Example:
        from rigging.utils import attribute
        # to hide an attr
        attribute.hide('transform1.translateZ')
        # or
        attribute.hide('translateZ', 'transform1')
    Args:
        attrPath (str): either 'object.attr' or just 'attr'
        node (str): if just the 'attr' is provided in attrPath then you need to specify the node name here
    Returns:
    """
    attrPaths = getAttrPaths(attrPath, node=node, recursive=True)
    for ap in attrPaths:
        cmds.setAttr(ap, keyable=False, channelBox=False)


def lock(attrPath, node=None):
    """
    Lock and attribute or a list of attributes

    Example:
        from rigging.utils import attribute
        attribute.lock(['tx','ty'], 'transform1')
        # or
        attribute.lock('transform1.translateX')
    Args:
        attrPath (str): either a list of attr names ['tx','ty'] or a complete path 'transform1.translateY'
        node (str): name of the maya node. not needed if a full attr path is given in attrPath
    """
    attrPaths = getAttrPaths(attrPath, node)
    for ap in attrPaths:
        cmds.setAttr(ap, lock=True)


def getAttrPaths(attrPath, node=None, recursive=False):
    """
    Gets a list of attribute paths. A wrapper for getAttrRelatives
    If recursive it will add the relative attributes as well

    Example:
        from rigging.utils import attribute
        import maya.cmds as cmds
        grp = cmds.createNode('transform')
        attribute.getAttrPaths('translate', node=grp, recursive=True)
        # Result: [u'transform1.translateZ',
                 'transform1.translate',
                 u'transform1.translateX',
                 u'transform1.translateY'] #

    Args:
        attrPath (str): either a full path or just an attr 'transform1.translate' or 'translate'
        node (str): if just an attr is provided for attrPath then you need to use this to define the maya node 'transform1'
        recursive (bool): wether or not to return the attribute relatives if it is a compound attr
    Returns:
        List of attr paths [u'transform1.translateZ','transform1.translate',u'transform1.translateX',u'transform1.translateY']
    """
    attrPathList = list()

    if node:
        attrPaths = createAttrPaths(attrPath, node)
    else:
        attrPaths = toList(attrPath)

    attrPathList = attrPaths

    if recursive:
        relAttrPathList = list()
        for ap in attrPaths:
            relatives = getAttrRelatives(ap)
            for rel in relatives:
                relAttrPathList.append(rel)

        attrPathList = list(set(attrPathList + relAttrPathList))

    return attrPathList


def toList(input):
    """
    takes input and returns it as a list
    """
    if isinstance(input, list):
        return input

    elif isinstance(input, tuple):
        return list(input)

    return [input]


def getAttrRelatives(attrPath):
    """
    Returns a list of relative attributes

    Example:
        from rigging.utils import attribute
        import maya.cmds as cmds
        grp = cmds.createNode('transform')
        attribute.getAttrRelatives('%s.translateX' %grp)
        # result: [u'transform1.translate']
        attribute.getAttrRelatives('%s.translate' %grp)
        # result: [u'transform1.translateX', u'transform1.translateY', u'transform1.translateZ']

    Args:
        attrPath (str): The attribute path you want to find relatives for i.e 'transform1.translate'
    Returns:
        List of relative attrs
    """
    attrPathList = list()

    # Find any parent or children to the list
    if cmds.objExists(attrPath):
        nodeName = attrPath.partition(".")[0]
        attrName = attrPath.partition(".")[-1]

        # Get attribute parent
        attrParent = cmds.attributeQuery(attrName, node=nodeName, listParent=True)
        if attrParent:
            for attr in attrParent:
                attrPathList.append(nodeName + "." + attr)

        # Get attribute children
        attrChildren = cmds.attributeQuery(attrName, node=nodeName, listChildren=True)
        if attrChildren:
            for attr in attrChildren:
                attrPathList.append(nodeName + "." + attr)
    else:
        log.info("attribute.getAttrPaths: " + attrPath + " does NOT exist, skipping...")

    return attrPathList


def createAttrPaths(attrs, nodes):
    """
    Takes a list of attrs and a list nodes and returns a list of attr paths

    Example:
        from rigging.utils import attribute
        cmds.polyCube()
        cmds.polyCube()
        attribute.createAttrPaths(['tx','ty'], ['pCube1', 'pCube2'])
        # Result: ['pCube1.tx', 'pCube1.ty', 'pCube2.tx', 'pCube2.ty'] #

    Args:
        attrs (list): A list of attributes i.e - ['tx','ry','v']
        nodes (list): A list of maya nodes
    Returns:
        A list of attribute paths i.e - ['pCube1.tx', 'pCube1.ty', 'pCube2.tx', 'pCube2.ty']
    """
    attrList = toList(attrs)
    nodeList = toList(nodes)
    attrPathList = list()

    for node in nodeList:
        for attr in attrList:
            attrPath = "%s.%s" % (node, attr)
            attrPathList.append(attrPath)

    return attrPathList
