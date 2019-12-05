"""

    Example of how to call renameTool.mel from renameTool.py

	from mechRig_toolkit.other import renameTool
	reload(renameTool)
	renameTool.call_mel()

"""


import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

from maya import cmds, mel

import os

MEL_DIR = os.path.dirname(__file__) # Gets full file path to this renameTool.py file
MEL_DIR = MEL_DIR.replace('\\', '/') # Replaces all back slashes to Maya friendly back slashes

def call_mel():

    LOG.info("Sourcing {}/renameTool.mel".format(MEL_DIR))
    mel.eval('source "{}/renameTool.mel"'.format(MEL_DIR))
    mel.eval("renameTool();")

