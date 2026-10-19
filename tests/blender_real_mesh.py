# SPDX-License-Identifier: GPL-3.0-or-later
"""Optional regression on a user's local scene, in memory only; never saves.
blender --background --disable-autoexec scene.blend --python this.py -- pied
"""
import pathlib
import sys
import bpy
import bmesh
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import addon
addon.register()
name=sys.argv[sys.argv.index('--')+1]
if bpy.context.object and bpy.context.object.mode!='OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')
obj=bpy.data.objects[name]
obj.select_set(True)
bpy.context.view_layer.objects.active=obj
original_geometry=[tuple(v.co) for v in obj.data.vertices]
bpy.ops.object.mode_set(mode='EDIT')
bm=bmesh.from_edit_mesh(obj.data)
uv=bm.loops.layers.uv.active
original_uv=[tuple(l[uv].uv) for f in bm.faces for l in f.loops]
bpy.context.scene.tool_settings.use_uv_select_sync=True
bpy.ops.mesh.select_all(action='SELECT')
bpy.context.scene.openuv_backend='NATIVE'
bpy.context.scene.openuv_quality='BALANCED'
bpy.context.scene.openuv_margin=.002
bpy.ops.ed.undo_push(message='Before real mesh test')
assert bpy.ops.uv.openuv_pack()=={'FINISHED'}
groups=addon.islands(bm,uv)
rects=[]
eps=1e-6  # Blender UV storage is float32, unlike native double arithmetic.
for group in groups:
    coords=[l[uv].uv for f in group for l in f.loops]
    rect=(min(p.x for p in coords),min(p.y for p in coords),max(p.x for p in coords),max(p.y for p in coords))
    assert rect[0]>=.002-eps and rect[1]>=.002-eps and rect[2]<=.998+eps and rect[3]<=.998+eps
    for a,b,c,d in rects:
        assert rect[2]+.004<=a+eps or c+.004<=rect[0]+eps or rect[3]+.004<=b+eps or d+.004<=rect[1]+eps
    rects.append(rect)
assert [tuple(v.co) for v in bm.verts]==original_geometry
print('REAL_MESH_STATS',bpy.context.scene.openuv_stats,bpy.context.scene.openuv_stats_detail,bpy.context.scene.openuv_stats_engine)
bpy.ops.ed.undo_push(message='After real mesh test')
assert bpy.ops.ed.undo()=={'FINISHED'}
restored=bmesh.from_edit_mesh(bpy.context.edit_object.data)
uv_restored=restored.loops.layers.uv.active
assert [tuple(l[uv_restored].uv) for f in restored.faces for l in f.loops]==original_uv
addon.unregister()
print('OPENUV_REAL_MESH_OK; source file not saved')
