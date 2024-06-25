import logging

from maya import cmds

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def toggle_antialias_viewport_display():
    """Sets anti-alias viewport display"""
    if cmds.getAttr("hardwareRenderingGlobals.multiSampleEnable"):
        cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 0)
    else:
        cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)

    if cmds.getAttr("hardwareRenderingGlobals.lineAAEnable"):
        cmds.setAttr("hardwareRenderingGlobals.lineAAEnable", 0)
        log.info("Viewport display anti-aliasing DISABLED...")
    else:
        cmds.setAttr("hardwareRenderingGlobals.lineAAEnable", 1)
        log.info("Viewport display anti-aliasing ENABLED...")


def set_near_clip(camera="persp", near_clip_value=1.0):
    try:
        cmds.setAttr("{}.nearClipPlane".format(camera), near_clip_value)
        log.info(
            "Set near clipping plane for {} to {}".format(camera, str(near_clip_value))
        )
    except:
        log.error("Error setting near clip plane value for {} camera".format(camera))
        return
