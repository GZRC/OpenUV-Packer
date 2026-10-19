# SPDX-License-Identifier: GPL-3.0-or-later
bl_info = {'name': 'OpenUV Packer', 'author': 'OpenUV Packer contributors',
           'version': (0,1,1), 'blender': (4,5,0), 'location': 'UV Editor > Sidebar > OpenUV',
           'description': 'Independent conservative UV island packer', 'category': 'UV'}
import bpy
from .operators.pack import OPENUV_OT_pack, islands
from .panels.main import OPENUV_PT_panel
from .properties import register_properties, unregister_properties


def register():
    for cls in (OPENUV_OT_pack, OPENUV_PT_panel):
        bpy.utils.register_class(cls)
    register_properties()


def unregister():
    unregister_properties()
    for cls in (OPENUV_PT_panel, OPENUV_OT_pack):
        bpy.utils.unregister_class(cls)
