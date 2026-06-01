"""
Setup script for py2app — macOS App 打包
"""
import sys
import os
from setuptools import setup

APP = ["main.py"]
APP_NAME = "PDF工具箱"

os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib")

DATA_FILES = []

OPTIONS = {
    "argv_emulation": False,
    "packages": [
        "PySide6", "fitz", "weasyprint", "docx",
        "ui", "core", "utils",
    ],
    "includes": [
        "PySide6.QtCore", "PySide6.QtWidgets", "PySide6.QtGui",
        "fitz", "weasyprint", "docx",
    ],
    "excludes": [
        "PyQt5", "PyQt6", "tkinter", "matplotlib", "numpy",
        "notebook", "jupyter", "pandas", "openpyxl",
    ],
    "plist": {
        "CFBundleName": APP_NAME,
        "CFBundleDisplayName": APP_NAME,
        "CFBundleIdentifier": "com.pdf-toolbox.app",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "NSHighResolutionCapable": True,
        "LSMinimumSystemVersion": "12.0",
    },
    "iconfile": None,
    "site_packages": True,
}

setup(
    name=APP_NAME,
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)