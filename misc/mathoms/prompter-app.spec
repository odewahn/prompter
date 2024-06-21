
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='prompter',
)

app = BUNDLE(coll,
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