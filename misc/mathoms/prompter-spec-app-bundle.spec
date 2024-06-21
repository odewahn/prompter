# -*- mode: python ; coding: utf-8 -*-

package_version = "0.3.0"

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('sql', 'sql'),('resources', 'resources')],
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
          console=True )



app = BUNDLE(exe,
    name='prompter.app',
    icon='resources/prompter.icns',
    bundle_identifier='com.oreilly.prompter',
    info_plist={
      'CFBundleName': 'prompter',
      'CFBundleDisplayName': 'prompter',
      'CFBundleVersion': package_version,
      'CFBundleShortVersionString': package_version,
      'NSRequiresAquaSystemAppearance': 'No',
      'NSHighResolutionCapable': 'True',
    },
)