"""
skin.py

Various skinning functions.

    from mechRig_toolkit.utils import skin

"""
import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

from maya import cmds, mel

def do_transfer_skin():
    """Transfer skin of first selected object to second selected object"""

    selection = cmds.ls(selection=True)

    if len(selection) == 2:
        transfer_skin(selection[0], selection[1])
    else:
        LOG.error('Please select source and target object to transfer skin')
        return


def transfer_skin(source, target):
    """Transfer the skinning from source object to target object"""
    src_geom = source
    src_skin = mel.eval('findRelatedSkinCluster("{}")'.format(src_geom))

    if src_skin:
        src_infs = cmds.skinCluster(src_skin, query=True, influence=True)

        tgt_geom = target
        tgt_skin = mel.eval('findRelatedSkinCluster("{}")'.format(tgt_geom))
        if tgt_skin:
            cmds.delete(tgt_skin)
        tgt_skin = cmds.skinCluster(src_infs, tgt_geom, name=tgt_geom + '_skinCluster', toSelectedBones=True)[0]
        cmds.copySkinWeights(sourceSkin=src_skin, destinationSkin=tgt_skin, surfaceAssociation='closestPoint', influenceAssociation='oneToOne', noMirror=True, smooth=False)

        LOG.info('Successfully transferred skinning from {} to {}'.format(source, target))

    else:
        LOG.error('No skinCluster found on {}'.format(source))
        return


def rename_shape_deformed_nodes():
    """Select geo transforms with ShapeDeformed named shapes and run
    ShapeDeformed nodes will be renamed to "Shape" and "Shape" intermediate
    nodes will be suffixed with "Orig"

    Note:  When referenced geometry is deformed, Maya will make the original
    shape node the "intermediate" node, and create a new "ShapeDeformed" node.
    This can be problematic for things like Alembic caching that use node names
    for node matching.  "ShapeDeformed" nodes would cause a mismatch with the original
    model and break that caching workflow.  This script should resolve this issue.
    """
    selection = cmds.ls(selection=True)

    if selection:
        for geo_tfm in selection:
            geo_shps = cmds.listRelatives(geo_tfm, shapes=True)
            if geo_shps:
                # Done in two passes so we're sure to rename the original
                # Shape node FIRST, then rename the ShapeDeformed node

                # Pass 1 - rename Shape node to ShapeOrig
                for geo_shp in geo_shps:
                    if geo_shp.endswith('Shape'):
                        cmds.rename(geo_shp, '{}Orig'.format(geo_shp))
                        LOG.info('Renamed {} to {}'.format(geo_shp, '{}Orig'.format(geo_shp)))

                # Pass 2 - rename ShapeDeformed node to Shape
                for geo_shp in geo_shps:
                    if geo_shp.endswith('ShapeDeformed'):
                        cmds.rename(geo_shp, geo_shp.replace('Deformed', ''))
                        LOG.info('Renamed {} to {}'.format(geo_shp, geo_shp.replace('Deformed', '')))

    else:
        LOG.error('Nothing selected, select geometry transforms and try again')
        return
