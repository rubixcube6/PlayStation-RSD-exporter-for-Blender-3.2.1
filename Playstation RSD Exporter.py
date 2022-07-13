
bl_info = {
    "name": "PlayStation RSD exporter",
    "author": "MB Games",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > RSD (PlayStation) Export",
    "description": "Exports your model in PlayStation RSD format",
    "warning": "",
    "doc_url": "https://github.com/rubixcube6/PlayStation-RSD-exporter-for-Blender-3.2.1",
    "category": "Export Plugin",
}

import bpy
import mathutils
import bmesh

ply_filepath = ""
mat_filepath = ""
rsd_filepath = ""

def materialFlag (transparencyRate:str, enableTransparency:int, renderBackface:int, unlit:int):
    flagString = "00" + transparencyRate + str(enableTransparency) + str(renderBackface) + str(unlit)
    flag = int(flagString, 2)
    # print(flagString)
    # print(flag)
    return str(flag)

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

    # How to use:

    # #Shows a message box with a specific message 
    # ShowMessageBox("This is a message") 

    # #Shows a message box with a message and custom title
    # ShowMessageBox("This is a message", "This is a custom title")

    # #Shows a message box with a message, custom title, and a specific icon
    # ShowMessageBox("This is a message", "This is a custom title", 'ERROR')

def mesh_triangulate(me):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.tris_convert_to_quads()
    bpy.ops.object.editmode_toggle()


    

def write_some_data(filepath, data):
    print("Writing data...")
    f = open(filepath, 'w', encoding='utf-8')
    f.write(data)
    f.close()

    return {'FINISHED'}


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportSomeData(Operator, ExportHelper):
    """Export your model in the PlayStation RSD format (compatible with the PsyQ SDK)"""
    bl_idname = "export_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export RSD"

    # ExportHelper mixin class uses this
    filename_ext = ".rsd"

    filter_glob: StringProperty(
        default="*.rsd;.ply;.mat",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    # use_setting: BoolProperty(
    #     name="Transparency Enabled",
    #     description="Toggle On/Off",
    #     default=False,
    # )

    # type: EnumProperty(
    #     name="Transparency Mode",
    #     description="Choose one",
    #     items=(
    #         ('OPT_A', "Default: 50% back + 50% polygon", "Mode 000"),
    #         ('OPT_B', "100% back + 100% polygon", "Mode 001"),
    #         ('OPT_C', "100% back - 100% polygon", "Mode 010"),
    #         ('OPT_D', "100% back + 25% polygon", "Mode 011"),
    #     ),
    #     default='OPT_A',
    # )

    def execute(self, context):
        filepath = self.filepath.replace(self.filename_ext, "")
        ply_filepath = bpy.path.ensure_ext(filepath, '.ply')
        mat_filepath = bpy.path.ensure_ext(filepath, '.mat')
        rsd_filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        #==================================================
        #              Conversion Begins Here
        #==================================================

        me = bpy.context.object.data

        for poly in me.polygons:
            if len(poly.vertices) > 4:
                mesh_triangulate(me)
                ShowMessageBox("The RSD model format does not support faces with more than 4 vertices. The model has been optimized to fix the issue.")
        
        polyCount = 0

        #======================
        #      PLY File
        #======================

        fileContentPLY = "#Playstation RSD Exporter for blender 3.2 by MB Games\n"
        fileContentPLY = "#PLY Mesh Data\n"

        fileContentPLY += "@PLY940102 \n"
        fileContentPLY += "#number of Verticies, Normals, and faces\n"
        fileContentPLY += str(len(me.vertices)) + " " + str(len(me.vertices) + len(me.polygons)) + " " + str(len(me.polygons)) + "\n"

        fileContentPLY += "#--------  Vertices  --------\n"
        for vert in me.vertices:

            fileContentPLY += str(vert.co.x) + " "
            fileContentPLY += str(-vert.co.z) + " "
            fileContentPLY += str(vert.co.y) + " "
            fileContentPLY += "\n"
                
        fileContentPLY += "#---------  normals  ---------\n"
        #Smooth Normals first (vertex normals)
        for vert in me.vertices:
            fileContentPLY += str(vert.normal.x) + " "
            fileContentPLY += str(-vert.normal.z) + " "
            fileContentPLY += str(vert.normal.y) + " "
            fileContentPLY += "\n"
        #Flat Normals Last (face normals)
        for poly in me.polygons:
            fileContentPLY += str(poly.normal.x) + " "
            fileContentPLY += str(-poly.normal.z) + " "
            fileContentPLY += str(poly.normal.y) + " "
            fileContentPLY += "\n"
        #store the start index of the flat normals
        flatNormStart = len(me.vertices)

        fileContentPLY += "#----------  Faces  ----------\n"
        i = 0
        for poly in me.polygons:

            polyCount += 1
            if len(poly.vertices) == 3:
                #This is a triangle.
                #0 for triangle
                fileContentPLY +=  str(0) + " "
                fileContentPLY += str(me.loops[poly.loop_start].vertex_index) + " "
                fileContentPLY += str(me.loops[poly.loop_start + 2].vertex_index) + " "
                fileContentPLY += str(me.loops[poly.loop_start + 1].vertex_index) + " "
                fileContentPLY += str(0)  + " "

                if poly.use_smooth:
                    fileContentPLY += str(me.loops[poly.loop_start].vertex_index) + " "
                    fileContentPLY += str(me.loops[poly.loop_start + 2].vertex_index) + " "
                    fileContentPLY += str(me.loops[poly.loop_start + 1].vertex_index) + " "
                    fileContentPLY += str(0)
                else:
                    # the starting index of flat normals + the current face index
                    fileContentPLY += str(i + flatNormStart) + " "
                    fileContentPLY += str(i + flatNormStart) + " "
                    fileContentPLY += str(i + flatNormStart) + " "
                    fileContentPLY += str(0)

            elif len(poly.vertices) == 4:
                #This is a quad
                #1 for quad
                fileContentPLY +=  str(1) + " "
                fileContentPLY += str(me.loops[poly.loop_start + 3].vertex_index) + " "
                fileContentPLY += str(me.loops[poly.loop_start + 2].vertex_index) + " "
                fileContentPLY += str(me.loops[poly.loop_start].vertex_index) + " "
                fileContentPLY += str(me.loops[poly.loop_start + 1].vertex_index) + " "

                if poly.use_smooth:
                    fileContentPLY += str(me.loops[poly.loop_start + 3].vertex_index) + " "
                    fileContentPLY += str(me.loops[poly.loop_start + 2].vertex_index) + " "
                    fileContentPLY += str(me.loops[poly.loop_start].vertex_index) + " "
                    fileContentPLY += str(me.loops[poly.loop_start + 1].vertex_index) + " "
                else:
                    # the starting index of flat normals + the current face index
                    fileContentPLY += str(i + flatNormStart) + " "
                    fileContentPLY += str(i + flatNormStart) + " "
                    fileContentPLY += str(i + flatNormStart) + " "
                    fileContentPLY += str(i + flatNormStart) + " "
            
            elif len(poly.vertices) > 4:
                print("This model should have been triangulated via the code above and something must have prevented it from happening. \nPlease triangulate your mesh manually.")
            
            fileContentPLY += "\n"
            i += 1

        #======================
        #      MAT File
        #======================

        uv_layer = me.uv_layers.active.data

        print("\n\n\n\n\n\n\n")

        totalTextures = 0
        textureNames = []

        i = 0
        for mat in me.materials:
            if mat.node_tree:
                for n in mat.node_tree.nodes:
                    if n.type=='TEX_IMAGE' or n.type=='ShaderNodeTexImage':
                        if n.image:
                            textureNames.append(str(n.image.name))
                            totalTextures += 1
            i += 1

        hasVertColors = False
        vertColors = []
        tempCol = mathutils.Color((0.0, 0.0, 0.0))
        i = 0
        if me.attributes:
            for atr in me.attributes:
                if atr.name == "Col":
                    hasVertColors = True
                    for d in atr.data:
                        tempCol = mathutils.Color((d.color[0], d.color[1], d.color[2]))
                        vertColors.append(tempCol)

        fileContentMAT = "#Playstation RSD Exporter for blender 3.2 by MB Games\n"
        fileContentMAT = "#MAT Material data\n"

        fileContentMAT += "@MAT940801 \n"
        fileContentMAT += str(polyCount) + "\n"

        i = 0
        for poly in me.polygons:
            
            unlit = 0
            
            texX = 0
            texY = 0
            textured = False
            texIndex = 0
            matIndex = 0
            for m in me.materials:
                if m.node_tree:
                    for n in m.node_tree.nodes:
                        if n.type=='TEX_IMAGE' or n.type=='ShaderNodeTexImage':
                            if n.image:
                                #this material has a texture
                                texIndex = poly.material_index
                                if matIndex == texIndex:
                                    #this material matches this polygon's material index
                                    textured = True
                                    texX = n.image.size[0] - 0.85
                                    texY = n.image.size[1] - 0.85
                matIndex += 1

            r = 0
            g = 0
            b = 0

            r1 = 0
            g1 = 0
            b1 = 0

            r2 = 0
            g2 = 0
            b2 = 0

            r3 = 0
            g3 = 0
            b3 = 0

            #check if this polygon has smooth colored vertices
            colorMultiplier = 255
            colorsAreFlat = False
            if hasVertColors:
                if len(poly.vertices) == 3:
                    #This is a triangle
                    r = int(vertColors[poly.loop_start].r * colorMultiplier)
                    g = int(vertColors[poly.loop_start].g * colorMultiplier)
                    b = int(vertColors[poly.loop_start].b * colorMultiplier)

                    r1 = int(vertColors[poly.loop_start + 2].r * colorMultiplier)
                    g1 = int(vertColors[poly.loop_start + 2].g * colorMultiplier)
                    b1 = int(vertColors[poly.loop_start + 2].b * colorMultiplier)

                    r2 = int(vertColors[poly.loop_start + 1].r * colorMultiplier)
                    g2 = int(vertColors[poly.loop_start + 1].g * colorMultiplier)
                    b2 = int(vertColors[poly.loop_start + 1].b * colorMultiplier)

                    if r == r1 and r1 == r2 and r2 == r1:
                        if g == g1 and g1 == g2 and g2 == g1:
                            if b == b1 and b1 == b2 and b2 == b1:
                                #flat colored poly
                                colorsAreFlat = True

                elif len(poly.vertices) == 4:

                    r = str( int(vertColors[poly.loop_start + 3].r * colorMultiplier) ) + " "
                    g = str( int(vertColors[poly.loop_start + 3].g * colorMultiplier) ) + " "
                    b = str( int(vertColors[poly.loop_start + 3].b * colorMultiplier) ) + " "

                    r1 = str( int(vertColors[poly.loop_start + 2].r * colorMultiplier) ) + " "
                    g1 = str( int(vertColors[poly.loop_start + 2].g * colorMultiplier) ) + " "
                    b1 = str( int(vertColors[poly.loop_start + 2].b * colorMultiplier) ) + " "

                    r2 = str( int(vertColors[poly.loop_start].r * colorMultiplier) ) + " "
                    g2 = str( int(vertColors[poly.loop_start].g * colorMultiplier) ) + " "
                    b2 = str( int(vertColors[poly.loop_start].b * colorMultiplier) ) + " "

                    r3 = str( int(vertColors[poly.loop_start + 1].r * colorMultiplier) ) + " "
                    g3 = str( int(vertColors[poly.loop_start + 1].g * colorMultiplier) ) + " "
                    b3 = str( int(vertColors[poly.loop_start + 1].b * colorMultiplier) ) + " "

                    if r == r1 and r1 == r2 and r2 == r3 and r3 == r:
                        if g == g1 and g1 == g2 and g2 == g3 and g3 == g:
                            if b == b1 and b1 == b2 and b2 == b3 and b3 == b:
                                #Flat colored Quad
                                colorsAreFlat = True
            
            #Conditions
            if textured:
                if hasVertColors:
                    # Disable lighting so we can set our own colors
                    unlit = 1
                else:
                    #enable lighting
                    unlit = 0
            else:
                if hasVertColors:
                    unlit = 1
                else:
                    unlit = 0
            
            fileContentMAT += str(i) + "    " + materialFlag("000", 0, 0, unlit) + " "

            if poly.use_smooth:
                fileContentMAT += "G "
            else:
                fileContentMAT += "F "

            colorMultiplier = 255
            
            #Conditions
            if textured:

                colorMultiplier = 128

                if hasVertColors:
                    if colorsAreFlat:
                        # Textured Flat Color
                        fileContentMAT += "D "
                    else:
                        # Textured Smooth Color
                        fileContentMAT += "H "
                    
                else:
                    # Textured No color
                    fileContentMAT += "T "
            else:
                if hasVertColors:
                    if colorsAreFlat:
                        # Not Textured Flat Color
                        fileContentMAT += "C "
                    else:
                        # Not Textured Smooth Color
                        fileContentMAT += "G "
                else:
                    # Not Textured No Vertex Colors
                    fileContentMAT += "C 255 255 255"
            
            #UVs
            if textured:

                colorMultiplier = 128
                fileContentMAT += str(texIndex) + " "

                #Set Texture UVs
                if len(poly.vertices) == 3:
                    #This is a triangle
                    fileContentMAT += str(int(uv_layer[poly.loop_start].uv.x * texX)) + " "
                    fileContentMAT += str(int(texY - (uv_layer[poly.loop_start].uv.y * texY))) + " "

                    fileContentMAT += str(int(uv_layer[poly.loop_start + 2].uv.x * texX)) + " "
                    fileContentMAT += str(int(texY - (uv_layer[poly.loop_start + 2].uv.y * texY))) + " "

                    fileContentMAT += str(int(uv_layer[poly.loop_start + 1].uv.x * texX)) + " "
                    fileContentMAT += str(int(texY - (uv_layer[poly.loop_start + 1].uv.y * texY))) + " "

                    fileContentMAT += "0 0 "
                elif len(poly.vertices) == 4:
                    #This is a quad
                    fileContentMAT += str(int(uv_layer[poly.loop_start + 3].uv.x * texX)) + " "
                    fileContentMAT += str(int(texY - (uv_layer[poly.loop_start + 3].uv.y * texY))) + " "

                    fileContentMAT += str(int(uv_layer[poly.loop_start + 2].uv.x * texX)) + " "
                    fileContentMAT += str(int(texY - (uv_layer[poly.loop_start + 2].uv.y * texY))) + " "

                    fileContentMAT += str(int(uv_layer[poly.loop_start].uv.x * texX)) + " "
                    fileContentMAT += str(int(texY - (uv_layer[poly.loop_start].uv.y * texY))) + " "

                    fileContentMAT += str(int(uv_layer[poly.loop_start + 1].uv.x * texX)) + " "
                    fileContentMAT += str(int(texY - (uv_layer[poly.loop_start + 1].uv.y * texY))) + " "
            
            else:
                # print("Not textured so no UVs")
                print(" ")
            
            #Vertex Colors
            if hasVertColors:
                if len(poly.vertices) == 3:
                    #This is a triangle

                    if colorsAreFlat:
                        fileContentMAT += str( int(vertColors[poly.loop_start].r * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start].g * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start].b * colorMultiplier) ) + " "
                    else:
                        fileContentMAT += str( int(vertColors[poly.loop_start].r * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start].g * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start].b * colorMultiplier) ) + " "

                        fileContentMAT += str( int(vertColors[poly.loop_start + 2].r * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start + 2].g * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start + 2].b * colorMultiplier) ) + " "

                        fileContentMAT += str( int(vertColors[poly.loop_start + 1].r * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start + 1].g * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start + 1].b * colorMultiplier) ) + " "

                        fileContentMAT += "0 "
                        fileContentMAT += "0 "
                        fileContentMAT += "0 "

                elif len(poly.vertices) == 4:

                    if colorsAreFlat:
                        fileContentMAT += str( int(vertColors[poly.loop_start].r * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start].g * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start].b * colorMultiplier) ) + " "
                    else:
                        fileContentMAT += str( int(vertColors[poly.loop_start + 3].r * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start + 3].g * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start + 3].b * colorMultiplier) ) + " "

                        fileContentMAT += str( int(vertColors[poly.loop_start + 2].r * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start + 2].g * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start + 2].b * colorMultiplier) ) + " "

                        fileContentMAT += str( int(vertColors[poly.loop_start].r * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start].g * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start].b * colorMultiplier) ) + " "

                        fileContentMAT += str( int(vertColors[poly.loop_start + 1].r * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start + 1].g * colorMultiplier) ) + " "
                        fileContentMAT += str( int(vertColors[poly.loop_start + 1].b * colorMultiplier) ) + " "
            elif textured == False:
                print("Not textured or colored")
            else:
                #Not colored so make it solid white
                fileContentMAT += "255 255 255"

            #this is the end of this polygon's material info
            fileContentMAT += "\n"
            i += 1

        #======================
        #      RSD File
        #======================

        fileContentRSD = "#Playstation RSD Exporter for blender 3.2 by MB Games\n"
        fileContentRSD = "#RSD data describing the relationships to the PLY, MAT, and texture files\n"

        fileContentRSD += "@RSD940102 \n"
        fileContentRSD += "PLY=" + bpy.path.basename(ply_filepath) + "\n"
        fileContentRSD += "MAT=" + bpy.path.basename(mat_filepath) + "\n"
        fileContentRSD += "NTEX=" + str(totalTextures) + "\n"
        if totalTextures > 0:
            texIndex = 0
            i = 0
            for tn in textureNames:
                fileContentRSD += "TEX[" + str(texIndex) + "]=" + (tn)[0:len(tn)-4] + ".tim\n"
                texIndex += 1
                i += 1
        
        # print("=================================================================================")        
        # print(fileContentPLY)
        print("=================================================================================")
        print(fileContentMAT)
        print("=================================================================================")
        # print(fileContentRSD)
        # print("=================================================================================")
        
        write_some_data(ply_filepath, fileContentPLY)
        write_some_data(mat_filepath, fileContentMAT)
        return write_some_data(rsd_filepath, fileContentRSD)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportSomeData.bl_idname, text="RSD (PlayStation) Export")

# Register and add to the "file selector" menu (required to use F3 search "Text Export Operator" for quick access)
def register():
    bpy.utils.register_class(ExportSomeData)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSomeData)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_test.some_data('INVOKE_DEFAULT')

def resizeList (lst:any, size:int) :#set the length of the list to the same length as materials
    i = 0
    while i < size - 1:
        lst.append(lst[0])
        i += 1


