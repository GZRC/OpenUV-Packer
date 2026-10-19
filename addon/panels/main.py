# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
class OPENUV_PT_panel(bpy.types.Panel):
    bl_label = 'OpenUV Packer 0.1.1'
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'OpenUV'
    def draw(self, context):
        col = self.layout.column()
        col.prop(context.scene, 'openuv_margin')
        col.prop(context.scene, 'openuv_rotate')
        col.prop(context.scene, 'openuv_backend')
        col.operator('uv.openuv_pack')
        col.label(text='Selected islands -> tile 1001')
        col.label(text='Unselected UVs are not obstacles')


