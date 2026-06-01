#!/usr/bin/env python3
"""
PDF 工具箱 — 入口

运行方式:
    export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
    python3 main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# WeasyPrint 需要系统库路径
os.environ.setdefault(
    "DYLD_FALLBACK_LIBRARY_PATH",
    "/opt/homebrew/lib"
)

from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PDF 工具箱")
    
    # 设置全局字体（避免 macOS 字体警告）
    from PySide6.QtGui import QFont
    font = QFont("Helvetica Neue", 13)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
