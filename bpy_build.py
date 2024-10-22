import bpy
import bmesh
import os

def buildModel(name : str, 
               verts : list, 
               faces : list, 
               uvs=[], 
               bones=[], 
               weights=[], 
               colors=[],
               materials=[], #{key = {key=TextureType val=TextureName}, val = [] list of faces with key mat}
               verbose=False,
               folder_path="",
               offset_face_idxs = 0) -> bpy.types.Object:
    """build a model from given data"""

    m = bpy.data.meshes.new(name)
    
    

    if offset_face_idxs != 0:
        offset_faces = []
        for f in faces:
            new_f = []
            for fv in f:
                new_f.append(fv+offset_face_idxs)
            offset_faces.append(new_f)
        faces = offset_faces
    
    m.from_pydata(verts, [], faces)
    
    bm = bmesh.new()
    bm.from_mesh(m)

    for i,d3duv in enumerate(uvs):
        if d3duv is None or d3duv == []: continue
        new_uv = bm.loops.layers.uv.new(f"UVMap{i}")
        bm.faces.ensure_lookup_table()
        bm.verts.ensure_lookup_table()
        for face in bm.faces:
            for loop in face.loops:
                if loop.vert.index >= len(d3duv): continue
                loop[new_uv].uv = d3duv[loop.vert.index]
    
    bm.verts.ensure_lookup_table()
    # removing loose verts
    for v in bm.verts:
        if len(v.link_edges) == 0:
            bm.verts.remove(v)
    
    bm.to_mesh(m)
    m.update()

    if len(materials) == 1 and materials != [[]]:
        mat = buildMat(
            diffuse_tex_name=materials[0]["Diffuse"],
            folder_path=folder_path,
        )
        m.materials.append(mat)
    
    
    mo = bpy.data.objects.new(name,m)


    return mo

def buildSkeleton(name, bones) -> bpy.types.Object:
    pass

def buildMat(
        diffuse_tex_name : str,
        normal_tex_name = "",
        folder_path=""):
    if diffuse_tex_name in bpy.data.materials:
        return bpy.data.materials[diffuse_tex_name]

    new_mat = bpy.data.materials.new(diffuse_tex_name)
    new_mat.use_nodes = True
    tree = new_mat.node_tree
    bsdf_node = tree.nodes["Principled BSDF"]
    dif_node = bpy.types.ShaderNodeTexImage(tree.nodes.new(type='ShaderNodeTexImage'))
    dif_node.name = "Diffuse"
    path_to_diffuse_texture = os.path.join(folder_path,diffuse_tex_name + ".png")
    if os.path.isfile(path_to_diffuse_texture):
        dif_node.image = bpy.data.images.load(path_to_diffuse_texture, check_existing=True)
    tree.links.new(dif_node.outputs[0], bsdf_node.inputs[0])
    return new_mat