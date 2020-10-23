# -*- mode: python -*-
import sys
import os.path
import simplejson as json

os_type = sys.platform
block_cipher = None
base_dir = os.path.dirname(os.path.realpath('__file__'))

# look for version string
version_str = ''
with open(os.path.join(base_dir, 'src', 'version.txt')) as version_file:
    version_data = json.load(version_file)
version_file.close()
version_str = version_data["number"] + version_data["tag"]

add_files = [('src/version.txt', '.'), ('img', 'img')]

if os_type == 'win32':
    import ctypes.util
    import win32con, win32file, pywintypes

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
          console=False,
          icon=os.path.join(base_dir, 'img', 'zkpm.%s' % ('icns' if os_type=='darwin' else 'ico')) )

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
app_path = os.path.join(dist_path, 'app')
os.chdir(dist_path)

if os_type == 'win32':
    os.chdir(base_dir)
    # Rename dist Dir
    dist_path_win = os.path.join(base_dir, 'ZkParamsWizard-v' + version_str + '-Win64')
    os.rename(dist_path, dist_path_win)
    # Create NSIS compressed installer
    print('Creating Windows installer (requires NSIS)')
    os.system('\"c:\\program files (x86)\\NSIS\\makensis.exe\" %s' % os.path.join(base_dir, 'setup.nsi'))

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

