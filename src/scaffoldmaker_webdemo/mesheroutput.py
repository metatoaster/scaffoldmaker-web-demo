"""
Generates 3-D Left and Right ventricles mesh starting from modified sphere shell mesh.
"""

import os
import json
import math
from scaffoldmaker.scaffoldmaker import Scaffoldmaker
from opencmiss.zinc.context import Context

meshes = {
    meshtype.__name__[len('MeshType_'):]: meshtype
    for meshtype in Scaffoldmaker().getMeshTypes()
}


def createCylindeLineGraphics(context, region):
    '''create cylinders which outline the shapes of the heart'''
    scene = region.getScene()
    field_module = region.getFieldmodule()
    material_module = context.getMaterialmodule()
    material = material_module.findMaterialByName('copper')

    tm = context.getTessellationmodule()
    tessellation = tm.createTessellation()
    tessellation.setCircleDivisions(1)
    tessellation.setRefinementFactors([4])

    scene.beginChange()
    lines = scene.createGraphicsLines()
    finite_element_field = field_module.findFieldByName('coordinates')
    lines.setCoordinateField(finite_element_field)
    lines.setTessellation(tessellation)

    lineAttr = lines.getGraphicslineattributes()
    lineAttr.setShapeType(lineAttr.SHAPE_TYPE_CIRCLE_EXTRUSION)
    lineAttr.setBaseSize([0.007, 0.007])
    lines.setMaterial(material)
     # Let the scene render the scene.
    scene.endChange()


def createSurfaceGraphics(context, region):
    material_module = context.getMaterialmodule()
    scene = region.getScene()
    scene.beginChange()
    fieldmodule = region.getFieldmodule()
    tm = context.getTessellationmodule()
    tessellation = tm.createTessellation()
    tessellation.setMinimumDivisions([4,4,1])
    material_module.defineStandardMaterials()
    material = material_module.findMaterialByName('muscle')

    finite_element_field = fieldmodule.findFieldByName('coordinates')
    surface = scene.createGraphicsSurfaces()
    surface.setCoordinateField(finite_element_field)
    surface.setTessellation(tessellation)
    surface.setMaterial(material)
    scene.endChange()


def exportWebGLJson(region):
    '''
    Export graphics into JSON format, one json export represents one
    surface graphics.
    '''
    scene = region.getScene()
    sceneSR = scene.createStreaminformationScene()
    sceneSR.setIOFormat(sceneSR.IO_FORMAT_THREEJS)

    # Get the total number of graphics in a scene/region that can be exported
    number = sceneSR.getNumberOfResourcesRequired()
    resources = []
    # Write out each graphics into a json file which can be rendered with our
    # WebGL script
    for i in range(number):
        resources.append(sceneSR.createStreamresourceMemory())
    scene.write(sceneSR)
    # Write out each resource into their own file

    return [resources[i].getBuffer()[1] for i in range(number)]


def mergeOptions(options1, options2):
    for item in options2:
        options1[item] = options2[item]
    return options1


def meshGeneration(meshtype_cls, region, options):
    fieldmodule = region.getFieldmodule()
    fieldmodule.beginChange()
    myOptions = mergeOptions(meshtype_cls.getDefaultOptions(), options)
    meshtype_cls.generateMesh(region, myOptions)
    fieldmodule.defineAllFaces()
    fieldmodule.endChange()


def outputModel(meshtype, options):
    """
    Provided meshtype must exist as a key in the meshes dict in this
    module.
    """

    # Initialise a sceneviewer for viewing
    meshtype_cls = meshes.get(meshtype)
    context = Context('output')
    logger = context.getLogger()
    context.getGlyphmodule().defineStandardGlyphs()
    region = context.createRegion()
    #readTestRegion(region)
    meshGeneration(meshtype_cls, region, options)
    # Create surface graphics which will be viewed and exported
    createSurfaceGraphics(context, region)
    createCylindeLineGraphics(context, region)
    # Export graphics into JSON format
    return exportWebGLJson(region)


def getMeshTypeOptions(meshtype):
    """
    Provided meshtype must exist as a key in the meshes dict in this
    module, otherwise return value will be None.
    """

    meshtype_cls = meshes.get(meshtype)
    if not meshtype_cls:
        return None
    defaultOptions = meshtype_cls.getDefaultOptions()
    return defaultOptions
