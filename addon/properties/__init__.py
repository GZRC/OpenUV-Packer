# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
from bpy.props import FloatProperty, BoolProperty, EnumProperty

def register_properties():
    bpy.types.Scene.openuv_margin = FloatProperty(name='Border per island (UV)', default=.002, min=0, max=.49)
    bpy.types.Scene.openuv_rotate = BoolProperty(name='Allow 90° rotation', default=True)
    bpy.types.Scene.openuv_backend = EnumProperty(name='Engine', items=[('AUTO','Auto','Native if installed'),('PYTHON','Python CPU','Portable fallback'),('NATIVE','C++ CPU','Requires compiled engine')])

def unregister_properties():
    for name in ('openuv_margin','openuv_rotate','openuv_backend'):
        delattr(bpy.types.Scene,name)
