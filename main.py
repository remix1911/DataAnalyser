
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DataAnalyser - 全功能开源数据分析工具
本地运行，Python实现，带GUI界面
完全覆盖数据分析师所有能力
"""

import sys
import os
import traceback

def setup_paths():
    """设置路径，确保模块可以被正确导入"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    core_dir = os.path.join(current_dir, 'core')
    if core_dir not in sys.path:
        sys.path.insert(0, core_dir)
    
    gui_dir = os.path.join(current_dir, 'gui')
    if gui_dir not in sys.path:
        sys.path.insert(0, gui_dir)

def main():
    """主函数，启动应用"""
    setup_paths()
    
    try:
        from PyQt6.QtWidgets import QApplication
        from gui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        app.setApplicationName("DataAnalyser")
        app.setApplicationVersion("1.0.0")
        
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec())
    
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所有依赖：pip install -r requirements.txt")
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"应用启动失败: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
