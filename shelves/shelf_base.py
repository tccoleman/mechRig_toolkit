"""
Credit to vshotarov
https://bindpose.com/scripting-custom-shelf-in-maya-python/
"""

from maya import cmds


def _null(*args):
    pass


class _shelf():
    """A simple class to build shelves in maya. Since the build method is empty,
    it should be extended by the derived class to build the necessary shelf elements.
    By default it creates an empty shelf called "customShelf"."""

    def __init__(self, name="customShelf", iconPath=""):
        self.name = name

        self.iconPath = iconPath

        self.labelBackground = (0, 0, 0, 0)
        self.labelColour = (.9, .9, .9)

        self._cleanOldShelf()
        cmds.setParent(self.name)
        self.build()

    def build(self):
        """This method should be overwritten in derived classes to actually build the shelf
        elements. Otherwise, nothing is added to the shelf."""
        pass

    def addButton(self, label, icon="commandButton.png", ann="", command=_null, doubleCommand=_null, overlayLabelColor=(.9, .9, .9)):
        """Adds a shelf button with the specified label, command, double click command and image."""
        cmds.setParent(self.name)
        if icon:
            icon = self.iconPath + icon
        cmds.shelfButton(width=37, height=37, ann=ann, image=icon, l=label, command=command, dcc=doubleCommand,
                         imageOverlayLabel=label, olb=self.labelBackground, olc=self.labelColour)

    def addMenuItem(self, parent, label, command=_null, icon=""):
        """Adds a shelf button with the specified label, command, double click command and image."""
        if icon:
            icon = self.iconPath + icon
        return cmds.menuItem(p=parent, l=label, c=command, i="")

    def addMenuItemDivider(self, parent, divider=True, dividerLabel=""):
        """Adds a shelf button with the specified label, command, double click command and image."""
        return cmds.menuItem(p=parent, divider=divider, dividerLabel=dividerLabel)

    def addSubMenu(self, parent, label, icon=None):
        """Adds a sub menu item with the specified label and icon to the specified parent popup menu."""
        if icon:
            icon = self.iconPath + icon
        return cmds.menuItem(p=parent, l=label, i=icon, subMenu=1)

    def _cleanOldShelf(self):
        """Checks if the shelf exists and empties it if it does or creates it if it does not."""
        if cmds.shelfLayout(self.name, ex=1):
            if cmds.shelfLayout(self.name, q=1, ca=1):
                for each in cmds.shelfLayout(self.name, q=1, ca=1):
                    cmds.deleteUI(each)
        else:
            cmds.shelfLayout(self.name, p="ShelfLayout")
