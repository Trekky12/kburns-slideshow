# -*- mode: python ; coding: utf-8 -*-

import shutil

block_cipher = None


a = Analysis(['kbvs.py'],
             pathex=[HOMEPATH],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='kbvs',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
          
          
shutil.copyfile('config.json', '%s/config.json' %(DISTPATH))
shutil.copytree('transitions', '%s/transitions' %(DISTPATH))
