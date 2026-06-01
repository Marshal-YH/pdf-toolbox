# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec — Windows 打包配置
用法：pyinstaller build_windows.spec
"""
import sys
from pathlib import Path

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui',
        'fitz', 'weasyprint', 'docx',
        'ui', 'ui.page_merge', 'ui.page_split', 'ui.page_word2pdf',
        'core', 'core.pdf_merge', 'core.pdf_split', 'core.word_to_pdf',
        'core.html_renderer', 'utils', 'utils.file_utils', 'utils.settings',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt5', 'PyQt6', 'tkinter', 'matplotlib', 'numpy',
        'notebook', 'jupyter', 'pandas', 'openpyxl', 'PIL',
    ],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PDF工具箱',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
