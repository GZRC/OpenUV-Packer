# SPDX-License-Identifier: GPL-3.0-or-later
"""Read UV bounds from a supplied blend file; never save or change its UVs.
blender --background --disable-autoexec scene.blend --python this.py -- output.json
Exports counts/dimensions only; mesh assets remain local.
"""
import json
import pathlib
import sys
import bmesh
import bpy
import struct
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from addon.operators.pack import islands
output=pathlib.Path(sys.argv[sys.argv.index('--')+1])
datasets=[]
for obj in bpy.data.objects:
    if obj.type!='MESH' or not obj.data.uv_layers:
        continue
    bm=bmesh.new()
    try:
        bm.from_mesh(obj.data)
        uv=bm.loops.layers.uv.active
        boxes=[]
        for group in islands(bm,uv):
            points=[l[uv].uv for f in group for l in f.loops]
            w=max(p.x for p in points)-min(p.x for p in points)
            h=max(p.y for p in points)-min(p.y for p in points)
            if w>0 and h>0:
                boxes.append((w,h))
        if boxes:
            datasets.append({'name':obj.name,'boxes':boxes,'faces':len(bm.faces),
                             'margin':struct.unpack('<f',struct.pack('<f',.002))[0],
                             'vertices':len(bm.verts)})
    finally:
        bm.free()
output.write_text(json.dumps(datasets),encoding='utf-8')
print('OPENUV_EXTRACT_OK',len(datasets),'meshes; source blend not saved')
