# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
import bmesh
import subprocess
from ..bridge.packing import pack, check

def islands(bm, uv):
    """Full visible islands; shared mesh edge AND UV endpoints must match."""
    faces = {f for f in bm.faces if not f.hide}
    result = []
    while faces:
        seed = faces.pop()
        group, stack = [seed], [seed]
        while stack:
            face = stack.pop()
            for loop in face.loops:
                edge = loop.edge
                if len(edge.link_faces) != 2:
                    continue
                other = next(f for f in edge.link_faces if f != face)
                if other not in faces:
                    continue
                def endpoint(f, vertex):
                    return next(l[uv].uv for l in f.loops if l.vert == vertex)
                if all((endpoint(face,v)-endpoint(other,v)).length <= 1e-7 for v in edge.verts):
                    faces.remove(other)
                    group.append(other)
                    stack.append(other)
        result.append(group)
    return result


class OPENUV_OT_pack(bpy.types.Operator):
    bl_idname = 'uv.openuv_pack'
    bl_label = 'Pack OpenUV'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.edit_object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, 'Select a mesh in Edit Mode')
            return {'CANCELLED'}
        if len(context.objects_in_mode_unique_data) != 1:
            self.report({'ERROR'}, 'MVP supports one mesh at a time')
            return {'CANCELLED'}
        bm = bmesh.from_edit_mesh(obj.data)
        uv = bm.loops.layers.uv.active
        if uv is None:
            self.report({'ERROR'}, 'Create a UV map first')
            return {'CANCELLED'}
        groups = islands(bm, uv)
        # Face selection in sync mode, UV vertex selection otherwise; expand to complete island.
        sync = context.scene.tool_settings.use_uv_select_sync
        def selected(loop):
            return loop.uv_select_vert if hasattr(loop, 'uv_select_vert') else loop[uv].select
        groups = [g for g in groups if any(f.select if sync else (f.select and any(selected(l) for l in f.loops)) for f in g)]
        if not groups:
            self.report({'ERROR'}, 'Select UV islands first')
            return {'CANCELLED'}
        if any(l[uv].pin_uv for g in groups for f in g for l in f.loops):
            self.report({'ERROR'}, 'Pinned UVs are unsupported; unpin selected islands')
            return {'CANCELLED'}
        loops = [[l for f in g for l in f.loops] for g in groups]
        bounds = [(min(l[uv].uv.x for l in ls), min(l[uv].uv.y for l in ls),
                   max(l[uv].uv.x for l in ls), max(l[uv].uv.y for l in ls)) for ls in loops]
        boxes = [(c-a,d-b) for a,b,c,d in bounds]
        scene = context.scene
        try:
            scale, places, backend = pack(boxes, scene.openuv_margin, scene.openuv_rotate, scene.openuv_backend)
            check(boxes, scene.openuv_margin, scale, places)
            changes = []
            for ls,(a,b,c,d),(x,y,r) in zip(loops,bounds,places):
                for l in ls:
                    u,v = l[uv].uv.x-a, l[uv].uv.y-b
                    if r:
                        u,v = d-b-v,u
                    changes.append((l,(x+u*scale,y+v*scale)))
            for l,position in changes:
                l[uv].uv = position
            bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)
        except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, f'{len(groups)} islands; {backend}; scale {scale:.5f}')
        return {'FINISHED'}


