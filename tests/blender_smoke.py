# SPDX-License-Identifier: GPL-3.0-or-later
import pathlib
import sys
import bpy
import bmesh
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import addon
addon.register()
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
mesh = bpy.data.meshes.new('TestMesh')
mesh.from_pydata([(0,0,0),(1,0,0),(2,0,0),(0,1,0),(1,1,0),(2,1,0)],[],[(0,1,4,3),(1,2,5,4)])
obj = bpy.data.objects.new('Test',mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
uv = mesh.uv_layers.new()
for poly in mesh.polygons:
    for i in poly.loop_indices:
        vertex = mesh.vertices[mesh.loops[i].vertex_index].co
        uv.data[i].uv = vertex.xy
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(mesh)
layer = bm.loops.layers.uv.active
assert len(addon.islands(bm,layer)) == 1, 'continuous UV detection'
bm.faces.ensure_lookup_table()
for l in bm.faces[1].loops:
    l[layer].uv.x += 3
assert len(addon.islands(bm,layer)) == 2, 'seam detection'
for f in bm.faces:
    f.select = True
    for l in f.loops:
        if hasattr(l, 'uv_select_vert_set'):
            l.uv_select_vert_set(True)
        else:
            l[layer].select = True
bpy.context.scene.tool_settings.use_uv_select_sync = True
before = [tuple(l[layer].uv) for f in bm.faces for l in f.loops]
first = bm.faces[0].loops[0]
first[layer].pin_uv = True
try:
    bpy.ops.uv.openuv_pack()
except RuntimeError:
    pass
assert before == [tuple(l[layer].uv) for f in bm.faces for l in f.loops]
first[layer].pin_uv = False
for backend,sync in (('PYTHON',True),('AUTO',False)):
    bpy.context.scene.tool_settings.use_uv_select_sync = sync
    bpy.context.scene.openuv_backend = backend
    assert bpy.ops.uv.openuv_pack() == {'FINISHED'}
    boxes = []
    for group in addon.islands(bm,layer):
        coords = [l[layer].uv for f in group for l in f.loops]
        boxes.append((min(v.x for v in coords),min(v.y for v in coords),max(v.x for v in coords),max(v.y for v in coords)))
    for x,y,X,Y in boxes:
        assert x >= 0 and y >= 0 and X <= 1 and Y <= 1
    a,b = boxes
    assert min(a[2],b[2])-max(a[0],b[0]) <= 1e-6 or min(a[3],b[3])-max(a[1],b[1]) <= 1e-6
def snapshot():
    current = bpy.context.edit_object
    edit = bmesh.from_edit_mesh(current.data)
    layer_now = edit.loops.layers.uv.active
    return [tuple(l[layer_now].uv) for f in edit.faces for l in f.loops]

bpy.ops.ed.undo_push(message='OpenUV before')
old_uv = snapshot()
bpy.context.scene.openuv_margin = .03
assert bpy.ops.uv.openuv_pack() == {'FINISHED'}
new_uv = snapshot()
assert old_uv != new_uv
bpy.ops.ed.undo_push(message='OpenUV after')
assert bpy.ops.ed.undo() == {'FINISHED'}
assert snapshot() == old_uv, 'Undo must restore UV coordinates'
assert bpy.ops.ed.redo() == {'FINISHED'}
assert snapshot() == new_uv, 'Redo must restore packed UV coordinates'
assert len(bpy.context.edit_object.data.vertices) == 6
edit = bmesh.from_edit_mesh(bpy.context.edit_object.data)
assert sorted(tuple(v.co) for v in edit.verts) == sorted([(0,0,0),(1,0,0),(2,0,0),(0,1,0),(1,1,0),(2,1,0)])
addon.unregister()
print('OPENUV_BLENDER_SMOKE_OK')
