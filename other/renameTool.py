"""

    Example of how to call renameTool.mel from renameTool.py

	from mechRig_toolkit.other import renameTool
	reload(renameTool)
	renameTool.call_mel()

"""
import logging
import os

from maya import cmds, mel

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

MEL_DIR = os.path.dirname(__file__)  # Gets full file path to this renameTool.py file
MEL_DIR = MEL_DIR.replace(
    "\\", "/"
)  # Replaces all double backslashes to python friendly slashes


def call_mel():
    log.info("Sourcing {}/renameTool.mel".format(MEL_DIR))
    mel.eval('source "{}/renameTool.mel"'.format(MEL_DIR))
    mel.eval("renameTool();")
