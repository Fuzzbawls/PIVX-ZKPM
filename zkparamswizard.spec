# -*- mode: python -*-
import sys
import os.path

os_type = sys.platform
block_cipher = None
base_dir = os.path.dirname(os.path.realpath('__file__'))

version_str = "0.0.1"  # !TODO: version file
app_name = "ZkParamsWizard"

a = Analysis(['zkparamswizard.py'],
             pathex=[base_dir, 'src'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=app_name,
          debug=False,
          strip=False,
          upx=False,
          console=False)

if os_type == 'darwin':
    app = BUNDLE(exe,
                 name='%s.app' % app_name,
                 bundle_identifier=None,
                     info_plist={
                        'NSHighResolutionCapable': 'True'
                     }
                 )

# Prepare bundles
dist_path = os.path.join(base_dir, 'dist')
os.chdir(base_dir)

if os_type == 'win32':
    dist_path_win = os.path.join(base_dir, app_name + '-v' + version_str + '-Win64')
    os.rename(dist_path, dist_path_win)

elif os_type == 'linux':
    dist_name = app_name + '-v' + version_str + '-gnu_linux'
    dist_path_linux = os.path.join(base_dir, dist_name)
    os.rename(dist_path, dist_path_linux)
    # Compress dist Dir
    print('Compressing Linux App Folder')
    os.system('tar -zcvf %s -C %s %s' % (dist_name + '.tar.gz', base_dir, dist_name))

elif os_type == 'darwin':
    dist_name = app_name + '-v' + version_str + '-MacOSX'
    dist_path_mac = os.path.join(base_dir, dist_name)
    os.rename(dist_path, dist_path_mac)
    # Remove 'app' folder
    print("Removin 'app' folder")
    os.chdir(dist_path_mac)
    os.system('rm -rf app')
    os.chdir(base_dir)
    # Compress dist Dir
    print('Compressing Mac App Folder')
    os.system('tar -zcvf %s -C %s %s' % (dist_name + '.tar.gz', base_dir, dist_name))

