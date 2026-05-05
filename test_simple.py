#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import traceback

def main():
    print("测试1: 基础导入")
    try:
        import pandas
        print("✓ pandas OK")
    except Exception as e:
        print(f"✗ pandas failed: {e}")
    
    print("\n测试2: PyQt6导入")
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget
        print("✓ PyQt6.QtWidgets OK")
    except Exception as e:
        print(f"✗ PyQt6.QtWidgets failed: {e}")
        traceback.print_exc()
    
    print("\n测试3: QtWebEngineWidgets导入")
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        print("✓ PyQt6.QtWebEngineWidgets OK")
    except Exception as e:
        print(f"✗ PyQt6.QtWebEngineWidgets failed: {e}")
        traceback.print_exc()
    
    print("\n测试4: 启动简单窗口")
    try:
        app = QApplication(sys.argv)
        win = QMainWindow()
        win.setWindowTitle("测试窗口")
        win.setGeometry(100, 100, 800, 600)
        win.show()
        print("✓ 窗口启动成功")
        sys.exit(app.exec())
    except Exception as e:
        print(f"✗ 窗口启动失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
