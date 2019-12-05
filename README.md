# MECHANICAL RIG TOOLKIT v.1.0
*Tim Coleman - tim.coleman.3d@gmail.com*

Welcome to the Mechanical Rig Toolkit.  The top level "mechRig_toolkit" folder contains several sub-folders and script/tool files used in the Mechanical Rigging course.  This toolkit will be updated several times over the 8-week course to include scripts that are used at that point in the course.  The documentation below covers installation of the toolkit and its 3 core areas:  Utility Script Library, Custom Maya Shelf and the Custom Maya Marking Menu.


##
## Installation
- Download the `mechRig_toolkit.zip` file and unzip it.  
- Inside the `mechRig_toolkit` folder that was unzipped, there will be another `mechRig_toolkit` folder.  Copy and paste that folder into your `<USER>/Documents/maya/scripts/` directory.   
- Launch Maya. 
- Once in Maya, open the Script Editor and run the following code to see if the toolkit was installed correctly.
#

    import mechRig_toolkit
    mechRig_toolkit.run_test()
You should see a "True" or a installation successful message if it was successful.

##
## Utility Script Library
Contain various Python scripts with functions to aid in the creation of rigs.

You can test if your installation was successful by running the code below to create locators at the selected objects or points.  Select objects or components to create locators at and run the code below in the Maya Script Editor
#### Running utility functions example
    from mechRig_toolkit.utils import locator
    reload(locator)
    locator.selected_points()


##
## Custom Shelf
Custom Maya tool shelf for quick access to often used utility functions and tools.
#### To Load Custom Maya Tool shelf
    from mechRig_toolkit.shelves import shelf_mechRig_utils
    reload(shelf_mechRig_utils)
    shelf_mechRig_utils.load(name="MechRig_utils")


#### Automatically load shelf at Maya startup
Add these lines to your `<USER>/Documents/maya/scripts/userSetup.py` file

    import maya.utils
    
    # Load Mech Rig Custom Shelf at Maya startup
    from mechRig_toolkit.shelves import shelf_mechRig_utils
    
    def load_mechRig_shelf():
    	shelf_mechRig_utils.load(name="MechRig_utils")
    	
    maya.utils.executeDeferred("load_mechRig_shelf()")


##
## Custom Marking Menu
Custom Maya Marking Menu for quick access to often used utility functions and tools.  Use RMB + CTL + ALT to invoke marking menu in Maya.
#### To Load Custom Marking menu
    from mechRig_toolkit.marking_menu import mechRig_marking_menu
    reload(mechRig_marking_menu)
    mechRig_marking_menu.markingMenu()
##



