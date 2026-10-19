# SPDX-License-Identifier: GPL-3.0-or-later
"""Run with Blender after scripts/package.ps1; tests the delivered ZIP."""
import pathlib
import sys
import tempfile
import zipfile
import bpy
import addon_utils

archive = pathlib.Path(__file__).resolve().parents[2]/'OpenUV-Packer-addon.zip'
scratch = pathlib.Path(__file__).resolve().parents[1]/'build'/'package-tests'
scratch.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='openuv-package-', dir=scratch) as temp:
    with zipfile.ZipFile(archive) as z:
        assert all(name.startswith('openuv_packer/') and '..' not in pathlib.PurePosixPath(name).parts for name in z.namelist())
        z.extractall(temp)
    sys.path.insert(0,temp)
    addon_utils.enable('openuv_packer', default_set=False)
    assert addon_utils.check('openuv_packer')[1], 'Packaged add-on failed to enable'
    bpy.ops.mesh.primitive_cube_add()
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.scene.tool_settings.use_uv_select_sync = True
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.context.scene.openuv_backend = 'NATIVE'
    assert bpy.ops.uv.openuv_pack() == {'FINISHED'}
    bpy.ops.object.mode_set(mode='OBJECT')
    addon_utils.disable('openuv_packer', default_set=False)
print('OPENUV_PACKAGE_OK')
