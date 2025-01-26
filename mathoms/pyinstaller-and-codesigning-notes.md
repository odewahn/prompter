To inspect the packaged contents, you can do this:

```
pyi-archive_viewer -l prompter > archive.csv
```

I found this helpful when trying to debug why the binary was so big.

## Various blind alleys and notes!

I went through a lot of steps to finally get a pkg built. The big insight was most of this stuff only works is you use pyinstaller's `onefile` option, rather than the diectory. The startup time there is slower, but it seems worth the hassle to make an installable binary.

First, be sure you're set up to run pyinstaller by reading [Build an executable with pyinstaller](http://www.gregreda.com/2023/05/18/notes-on-using-pyinstaller-poetry-and-pyenv/). This is another good [tutorial on pyinstaller](https://www.devdungeon.com/content/pyinstaller-tutorial). It took a bit of finagling to make this work, so YMMV.

From the root directory, run the following command:

```

pyinstaller \
 --name=prompter \
 --add-data="sql:sql" \
 --hidden-import=prompt_toolkit \
 --noconfirm \
 --clean \
 main.py

```

To view the sizes of the included files, cd into the `dist/_internal` directory and run:

```
du -hs *
```

Originally, I compiled this using `--onefile` but found that it became incredibly slow to start up. Ths seems to be a common complaint about pyinstaller. I think it also has to do with a virus scanner, which has to scan each file in the package as it's unzipped every time. So, I started just directibuting the dist folder. It's less convenient and clear, but gives an acceptable startup time.

### Codesigning

https://haim.dev/posts/2020-08-08-python-macos-app/

https://github.com/pyinstaller/pyinstaller/issues/5154

https://pyinstaller.org/en/v4.7/feature-notes.html#macos-binary-code-signing

https://github.com/pyinstaller/pyinstaller/issues/7320

https://gist.github.com/txoof/0636835d3cc65245c6288b2374799c43

https://www.linkedin.com/pulse/looking-distribute-your-python-script-mac-users-jai-goyal-aotsc/

https://forums.developer.apple.com/forums/thread/735581

https://apple.stackexchange.com/questions/395763/how-to-code-sign-my-python-script-package-packaged-for-mac-using-pyinstaller-w

https://stackoverflow.com/questions/21736367/signing-code-for-os-x-application-bundle

https://stackoverflow.com/questions/68884906/pyinstaller-error-systemerror-codesign-failure-on-macos

Then this:

codesign -s Developer -v --force --deep --timestamp --entitlements entitlements.plist -o runtime "dist/prompter.app"

### Using codesigning in pyinstaller

See https://pyinstaller.org/en/v4.7/feature-notes.html#macos-binary-code-signing

### Create the build

First, if you've not done so already, get the [codesign identity](https://github.com/pyinstaller/pyinstaller/issues/7320):

```
security find-identity -v -p codesigning
```

This is the value used in `codesign_identity` in the spec file. Then run the build:

```
pyinstaller --noconfirm --clean prompter.spec
```

#### Sign the app

Then sign the app. [Unlock the keychain before you use codesign](https://stackoverflow.com/questions/11712322/error-the-timestamp-service-is-not-available-when-using-codesign-on-mac-os-x):

```
security unlock-keychain login.keychain
```

Then:

```
codesign -s Developer -v -vvv --force --deep --timestamp --entitlements=entitlements.plist -o runtime "dist/prompter"
```

```
codesign --timestamp -s Developer --deep --force --options runtime "dist/prompter/_internal/Python.framework"


```

For debugging, see:

https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution/resolving_common_notarization_issues#3087735

```
codesign -vvv --deep --strict dist/prompter
```

### Notarizing

```
ditto -c -k --keepParent "dist/prompter" dist/prompter.zip
```

```
xcrun notarytool submit dist/prompter.zip \
 --apple-id andrew@odewahn.com \
 --password vmbz-ccnv-diov-xhsr \
 --team-id 8R36RY2J2J \
 --wait
```

If it gives you an "invalid" message, you can check why with

xcrun notarytool log d8948805-2088-4f1d-a660-69ae74573a99 --apple-id YOUR_APPLE_ID --team-id=YOUR_TEAM_ID

### With pycodesign

First, set up the keychain stuff:

xcrun notarytool store-credentials ODEWAHN \
 --apple-id andrew@odewahn.com \
 --team-id 8R36RY2J2J

Do a fresh build

Change into `dis/prompter` directory

Run

```
pycodesign.py pycodesign.ini
```

The run this:

codesign --timestamp -s Developer --deep --force --options runtime "dist/prompter/\_internal/Python.framework"

xcrun notarytool log \
 --apple-id=andrew@odewahn.com \
 --team-id=8R36RY2J2J \
 f5617b4f-f93c-4254-a364-cbca7a93fe6e
