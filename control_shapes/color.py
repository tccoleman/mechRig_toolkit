"""

    Simple Color Palette UI for setting color overrides on the shapes of selected objects

"""
from maya import cmds


def set_override_color_UI():
    """Simple UI for setting color override colors on selected objects"""

    overrideColor_win = cmds.window(title="Set Override Color Tool")
    cmds.columnLayout()
    cmds.gridLayout(numberOfColumns=8, cellWidthHeight=(45, 25))

    cmds.button(label="None", command=lambda *args: override_color(0))
    cmds.button(label="", bgc=(0, 0, 0), command=lambda *args: override_color(1))
    cmds.button(
        label="", bgc=(0.75, 0.75, 0.75), command=lambda *args: override_color(2)
    )
    cmds.button(label="", bgc=(0.5, 0.5, 0.5), command=lambda *args: override_color(3))
    cmds.button(label="", bgc=(0.8, 0, 0.2), command=lambda *args: override_color(4))
    cmds.button(label="", bgc=(0, 0, 0.4), command=lambda *args: override_color(5))
    cmds.button(label="", bgc=(0, 0, 1), command=lambda *args: override_color(6))
    cmds.button(label="", bgc=(0, 0.3, 0), command=lambda *args: override_color(7))
    cmds.button(label="", bgc=(0.2, 0, 0.3), command=lambda *args: override_color(8))
    cmds.button(label="", bgc=(0.8, 0, 0.8), command=lambda *args: override_color(9))
    cmds.button(label="", bgc=(0.6, 0.3, 0.2), command=lambda *args: override_color(10))
    cmds.button(
        label="", bgc=(0.25, 0.13, 0.13), command=lambda *args: override_color(11)
    )
    cmds.button(label="", bgc=(0.7, 0.2, 0), command=lambda *args: override_color(12))
    cmds.button(label="", bgc=(1, 0, 0), command=lambda *args: override_color(13))
    cmds.button(label="", bgc=(0, 1, 0), command=lambda *args: override_color(14))
    cmds.button(label="", bgc=(0, 0.3, 0.6), command=lambda *args: override_color(15))
    cmds.button(label="", bgc=(1, 1, 1), command=lambda *args: override_color(16))
    cmds.button(label="", bgc=(1, 1, 0), command=lambda *args: override_color(17))
    cmds.button(label="", bgc=(0, 1, 1), command=lambda *args: override_color(18))
    cmds.button(label="", bgc=(0, 1, 0.8), command=lambda *args: override_color(19))
    cmds.button(label="", bgc=(1, 0.7, 0.7), command=lambda *args: override_color(20))
    cmds.button(label="", bgc=(0.9, 0.7, 0.5), command=lambda *args: override_color(21))
    cmds.button(label="", bgc=(1, 1, 0.4), command=lambda *args: override_color(22))
    cmds.button(label="", bgc=(0, 0.7, 0.4), command=lambda *args: override_color(23))
    cmds.button(label="", bgc=(0.6, 0.4, 0.2), command=lambda *args: override_color(24))
    cmds.button(
        label="", bgc=(0.63, 0.63, 0.17), command=lambda *args: override_color(25)
    )
    cmds.button(label="", bgc=(0.4, 0.6, 0.2), command=lambda *args: override_color(26))
    cmds.button(
        label="", bgc=(0.2, 0.63, 0.35), command=lambda *args: override_color(27)
    )
    cmds.button(
        label="", bgc=(0.18, 0.63, 0.63), command=lambda *args: override_color(28)
    )
    cmds.button(
        label="", bgc=(0.18, 0.4, 0.63), command=lambda *args: override_color(29)
    )
    cmds.button(
        label="", bgc=(0.43, 0.18, 0.63), command=lambda *args: override_color(30)
    )
    cmds.button(
        label="", bgc=(0.63, 0.18, 0.4), command=lambda *args: override_color(31)
    )

    cmds.showWindow(overrideColor_win)
    cmds.window(overrideColor_win, edit=True, wh=[362, 126])


def override_disabled():
    """Sets overrides ooff"""
    sel = cmds.ls(selection=True)
    if sel:
        for item in sel:
            shps = cmds.listRelatives(item, shapes=True)
            for shp in shps:
                cmds.setAttr("{}.overrideEnabled".format(shp), 0)


def override_color(color_index):
    """Sets overrides on and set override color"""
    sel = cmds.ls(selection=True)
    if sel:
        for item in sel:
            shps = cmds.listRelatives(item, shapes=True)
            if shps:
                for shp in shps:
                    cmds.setAttr("{}.overrideEnabled".format(shp), 1)
                    cmds.setAttr("{}.overrideColor".format(shp), color_index)


if __name__ == "__main__":
    set_override_color_UI()
