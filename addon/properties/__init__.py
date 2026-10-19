# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
from bpy.props import FloatProperty, BoolProperty, EnumProperty, StringProperty

def register_properties():
    bpy.types.Scene.openuv_margin = FloatProperty(
        name='Border per island (UV)', default=.002, min=0, max=.49,
        precision=4, step=.01,
        description='Border on each side of an island; island spacing is twice this value')
    bpy.types.Scene.openuv_rotate = BoolProperty(name='Allow 90° rotation', default=True)
    bpy.types.Scene.openuv_backend = EnumProperty(name='Engine', items=[('AUTO','Auto','Native if installed'),('PYTHON','Python CPU','Portable fallback'),('NATIVE','C++ CPU','Requires compiled engine')])
    bpy.types.Scene.openuv_quality = EnumProperty(name='Quality', default='BALANCED', items=[
        ('FAST','Fast','2 MaxRects searches, up to 128 islands'),
        ('BALANCED','Balanced','4 MaxRects searches, up to 256 islands'),
        ('HIGH','High','6 MaxRects searches, up to 512 islands')])
    bpy.types.Scene.openuv_stats = StringProperty(name='Last pack', default='', options={'SKIP_SAVE'})
    bpy.types.Scene.openuv_stats_detail = StringProperty(name='Last pack details', default='', options={'SKIP_SAVE'})
    bpy.types.Scene.openuv_stats_engine = StringProperty(name='Last pack engine', default='', options={'SKIP_SAVE'})

def unregister_properties():
    for name in ('openuv_margin','openuv_rotate','openuv_backend','openuv_quality','openuv_stats','openuv_stats_detail','openuv_stats_engine'):
        delattr(bpy.types.Scene,name)
