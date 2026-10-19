# SPDX-License-Identifier: GPL-3.0-or-later
import bpy
class OPENUV_PT_panel(bpy.types.Panel):
    bl_label = 'OpenUV Packer 0.2.0'
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'OpenUV'
    def draw(self, context):
        col = self.layout.column()
        col.prop(context.scene, 'openuv_margin')
        col.prop(context.scene, 'openuv_rotate')
        col.prop(context.scene, 'openuv_backend')
        if context.scene.openuv_backend != 'PYTHON':
            col.prop(context.scene, 'openuv_quality')
        col.operator('uv.openuv_pack')
        col.label(text='Selected islands -> tile 1001')
        col.label(text='Unselected UVs are not obstacles')
        if context.scene.openuv_stats:
            box = col.box()
            box.label(text=context.scene.openuv_stats)
            box.label(text=context.scene.openuv_stats_detail)
            box.label(text=context.scene.openuv_stats_engine)
            box.label(text='Area = bounding rectangles, not polygons')


