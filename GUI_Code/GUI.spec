# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['GUI.py'],
             pathex=['C:\\Users\\bravo\\Documents\\GitHub\\SeniorDesign\\GUI_Code'],
             binaries=[],
             datas=[('C:\\Users\\bravo\\Documents\\GitHub\\SeniorDesign\\GUI_Code\\lib\\opencv_videoio_ffmpeg411_64.dll', '.'), ('C:\\Users\\bravo\\Documents\\GitHub\\SeniorDesign\\GUI_Code\\lib\\shape_predictor_68_face_landmarks.dat', '.')],
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
          name='GUI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
