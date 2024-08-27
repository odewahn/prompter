# -*- mode: python ; coding: utf-8 -*-

package_version = "0.4.1"

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('sql', 'sql')],
    hiddenimports=['prompt_toolkit'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='prompter',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True)


