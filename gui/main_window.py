
import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QTableView, QHeaderView, QMessageBox,
    QComboBox, QLabel, QLineEdit, QTextEdit, QGroupBox, QGridLayout,
    QProgressBar, QSplitter, QDialog, QSpinBox, QDoubleSpinBox, QInputDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings, QAbstractTableModel
from PyQt6.QtGui import QIcon, QFont
from core.data_loader import DataLoader
from core.data_cleaner import DataCleaner
from core.data_analyzer import DataAnalyzer
from core.machine_learning import MLModel
from core.visualization import Visualizer
from core.report_generator import ReportGenerator
from core.data_encryptor import DataEncryptor
import plotly.express as px
from plotly.offline import plot
from PyQt6.QtWebEngineWidgets import QWebEngineView

class WorkerThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class DataTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
    
    def rowCount(self, parent=None):
        return len(self._data)
    
    def columnCount(self, parent=None):
        return len(self._data.columns)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            else:
                return str(section)
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataAnalyser - 全功能数据分析工具")
        self.setGeometry(100, 100, 1200, 800)
        
        self.current_df = None
        self.cleaned_df = None
        self.analysis_results = None
        self.ml_results = None
        
        self.settings = QSettings("DataAnalyser", "Settings")
        
        self.init_ui()
    
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        
        self.tabs = QTabWidget()
        
        self.data_tab = QWidget()
        self.data_layout = QVBoxLayout(self.data_tab)
        self.setup_data_tab()
        
        self.clean_tab = QWidget()
        self.clean_layout = QVBoxLayout(self.clean_tab)
        self.setup_clean_tab()
        
        self.analysis_tab = QWidget()
        self.analysis_layout = QVBoxLayout(self.analysis_tab)
        self.setup_analysis_tab()
        
        self.ml_tab = QWidget()
        self.ml_layout = QVBoxLayout(self.ml_tab)
        self.setup_ml_tab()
        
        self.visualization_tab = QWidget()
        self.vis_layout = QVBoxLayout(self.visualization_tab)
        self.setup_visualization_tab()
        
        self.report_tab = QWidget()
        self.report_layout = QVBoxLayout(self.report_tab)
        self.setup_report_tab()
        
        self.tabs.addTab(self.data_tab, "数据导入")
        self.tabs.addTab(self.clean_tab, "数据清洗")
        self.tabs.addTab(self.analysis_tab, "数据分析")
        self.tabs.addTab(self.ml_tab, "机器学习")
        self.tabs.addTab(self.visualization_tab, "可视化")
        self.tabs.addTab(self.report_tab, "报告生成")
        
        self.left_layout.addWidget(self.tabs)
        self.splitter.addWidget(self.left_panel)
        
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        
        self.result_view = QWebEngineView()
        self.right_layout.addWidget(self.result_view)
        
        self.table_view = QTableView()
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        self.result_splitter = QSplitter(Qt.Orientation.Vertical)
        self.result_splitter.addWidget(self.result_view)
        self.result_splitter.addWidget(self.table_view)
        self.right_layout.addWidget(self.result_splitter)
        
        self.splitter.addWidget(self.right_panel)
        self.splitter.setSizes([400, 800])
    
    def setup_data_tab(self):
        self.data_group = QGroupBox("数据导入")
        self.data_layout.addWidget(self.data_group)
        self.data_grid = QGridLayout(self.data_group)
        
        self.file_btn = QPushButton("选择文件")
        self.file_btn.clicked.connect(self.load_file)
        self.data_grid.addWidget(self.file_btn, 0, 0)
        
        self.file_label = QLabel("未选择文件")
        self.data_grid.addWidget(self.file_label, 0, 1)
        
        self.mysql_group = QGroupBox("MySQL连接")
        self.data_layout.addWidget(self.mysql_group)
        self.mysql_grid = QGridLayout(self.mysql_group)
        
        self.mysql_grid.addWidget(QLabel("主机:"), 0, 0)
        self.mysql_host = QLineEdit("localhost")
        self.mysql_grid.addWidget(self.mysql_host, 0, 1)
        
        self.mysql_grid.addWidget(QLabel("端口:"), 1, 0)
        self.mysql_port = QLineEdit("3306")
        self.mysql_grid.addWidget(self.mysql_port, 1, 1)
        
        self.mysql_grid.addWidget(QLabel("用户名:"), 2, 0)
        self.mysql_user = QLineEdit()
        self.mysql_grid.addWidget(self.mysql_user, 2, 1)
        
        self.mysql_grid.addWidget(QLabel("密码:"), 3, 0)
        self.mysql_pass = QLineEdit()
        self.mysql_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.mysql_grid.addWidget(self.mysql_pass, 3, 1)
        
        self.mysql_grid.addWidget(QLabel("数据库:"), 4, 0)
        self.mysql_db = QLineEdit()
        self.mysql_grid.addWidget(self.mysql_db, 4, 1)
        
        self.mysql_grid.addWidget(QLabel("表名:"), 5, 0)
        self.mysql_table = QLineEdit()
        self.mysql_grid.addWidget(self.mysql_table, 5, 1)
        
        self.mysql_btn = QPushButton("连接MySQL")
        self.mysql_btn.clicked.connect(self.connect_mysql)
        self.mysql_grid.addWidget(self.mysql_btn, 6, 0, 1, 2)
        
        self.data_info = QTextEdit()
        self.data_info.setReadOnly(True)
        self.data_layout.addWidget(self.data_info)
        
        self.save_data_btn = QPushButton("保存数据")
        self.save_data_btn.clicked.connect(self.save_data)
        self.data_layout.addWidget(self.save_data_btn)
        
        self.load_encrypted_btn = QPushButton("加载加密数据")
        self.load_encrypted_btn.clicked.connect(self.load_encrypted_data)
        self.data_layout.addWidget(self.load_encrypted_btn)
    
    def setup_clean_tab(self):
        self.clean_group = QGroupBox("数据清洗")
        self.clean_layout.addWidget(self.clean_group)
        self.clean_grid = QGridLayout(self.clean_group)
        
        self.remove_dup_cb = QComboBox()
        self.remove_dup_cb.addItems(["是", "否"])
        self.remove_dup_cb.setCurrentText("是")
        self.clean_grid.addWidget(QLabel("去重:"), 0, 0)
        self.clean_grid.addWidget(self.remove_dup_cb, 0, 1)
        
        self.fill_missing_cb = QComboBox()
        self.fill_missing_cb.addItems(["是", "否"])
        self.fill_missing_cb.setCurrentText("是")
        self.clean_grid.addWidget(QLabel("填充缺失值:"), 1, 0)
        self.clean_grid.addWidget(self.fill_missing_cb, 1, 1)
        
        self.fill_strategy = QComboBox()
        self.fill_strategy.addItems(["mean", "median", "mode", "zero"])
        self.fill_strategy.setCurrentText("mean")
        self.clean_grid.addWidget(QLabel("填充策略:"), 2, 0)
        self.clean_grid.addWidget(self.fill_strategy, 2, 1)
        
        self.remove_outlier_cb = QComboBox()
        self.remove_outlier_cb.addItems(["是", "否"])
        self.remove_outlier_cb.setCurrentText("是")
        self.clean_grid.addWidget(QLabel("移除异常值:"), 3, 0)
        self.clean_grid.addWidget(self.remove_outlier_cb, 3, 1)
        
        self.outlier_method = QComboBox()
        self.outlier_method.addItems(["zscore", "iqr"])
        self.outlier_method.setCurrentText("zscore")
        self.clean_grid.addWidget(QLabel("检测方法:"), 4, 0)
        self.clean_grid.addWidget(self.outlier_method, 4, 1)
        
        self.standardize_cb = QComboBox()
        self.standardize_cb.addItems(["是", "否"])
        self.standardize_cb.setCurrentText("是")
        self.clean_grid.addWidget(QLabel("格式标准化:"), 5, 0)
        self.clean_grid.addWidget(self.standardize_cb, 5, 1)
        
        self.clean_btn = QPushButton("一键清洗")
        self.clean_btn.clicked.connect(self.clean_data)
        self.clean_grid.addWidget(self.clean_btn, 6, 0, 1, 2)
        
        self.clean_info = QTextEdit()
        self.clean_info.setReadOnly(True)
        self.clean_layout.addWidget(self.clean_info)
    
    def setup_analysis_tab(self):
        self.analysis_group = QGroupBox("数据分析")
        self.analysis_layout.addWidget(self.analysis_group)
        self.analysis_grid = QGridLayout(self.analysis_group)
        
        self.describe_btn = QPushButton("描述统计")
        self.describe_btn.clicked.connect(self.show_descriptive)
        self.analysis_grid.addWidget(self.describe_btn, 0, 0)
        
        self.corr_btn = QPushButton("相关性分析")
        self.corr_btn.clicked.connect(self.show_correlation)
        self.analysis_grid.addWidget(self.corr_btn, 0, 1)
        
        self.pivot_btn = QPushButton("透视表")
        self.pivot_btn.clicked.connect(self.show_pivot)
        self.analysis_grid.addWidget(self.pivot_btn, 1, 0)
        
        self.dimension_btn = QPushButton("维度拆解")
        self.dimension_btn.clicked.connect(self.show_dimension)
        self.analysis_grid.addWidget(self.dimension_btn, 1, 1)
        
        self.analysis_result = QTextEdit()
        self.analysis_result.setReadOnly(True)
        self.analysis_layout.addWidget(self.analysis_result)
        
        self.columns_label = QLabel("可用列:")
        self.analysis_layout.addWidget(self.columns_label)
        
        self.columns_list = QComboBox()
        self.analysis_layout.addWidget(self.columns_list)
    
    def setup_ml_tab(self):
        self.ml_group = QGroupBox("机器学习")
        self.ml_layout.addWidget(self.ml_group)
        self.ml_grid = QGridLayout(self.ml_group)
        
        self.cluster_btn = QPushButton("聚类分析")
        self.cluster_btn.clicked.connect(self.run_clustering)
        self.ml_grid.addWidget(self.cluster_btn, 0, 0)
        
        self.cluster_method = QComboBox()
        self.cluster_method.addItems(["KMeans", "DBSCAN"])
        self.ml_grid.addWidget(self.cluster_method, 0, 1)
        
        self.n_clusters = QSpinBox()
        self.n_clusters.setRange(2, 10)
        self.n_clusters.setValue(3)
        self.ml_grid.addWidget(QLabel("聚类数:"), 1, 0)
        self.ml_grid.addWidget(self.n_clusters, 1, 1)
        
        self.classify_btn = QPushButton("分类")
        self.classify_btn.clicked.connect(self.run_classification)
        self.ml_grid.addWidget(self.classify_btn, 2, 0)
        
        self.regress_btn = QPushButton("回归")
        self.regress_btn.clicked.connect(self.run_regression)
        self.ml_grid.addWidget(self.regress_btn, 2, 1)
        
        self.target_col = QComboBox()
        self.ml_grid.addWidget(QLabel("目标列:"), 3, 0)
        self.ml_grid.addWidget(self.target_col, 3, 1)
        
        self.ml_result = QTextEdit()
        self.ml_result.setReadOnly(True)
        self.ml_layout.addWidget(self.ml_result)
    
    def setup_visualization_tab(self):
        self.vis_group = QGroupBox("可视化")
        self.vis_layout.addWidget(self.vis_group)
        self.vis_grid = QGridLayout(self.vis_group)
        
        self.chart_type = QComboBox()
        self.chart_type.addItems(["line", "bar", "pie", "scatter", "heatmap", "histogram", "boxplot", "dashboard", "trend"])
        self.vis_grid.addWidget(QLabel("图表类型:"), 0, 0)
        self.vis_grid.addWidget(self.chart_type, 0, 1)
        
        self.x_col = QComboBox()
        self.vis_grid.addWidget(QLabel("X轴:"), 1, 0)
        self.vis_grid.addWidget(self.x_col, 1, 1)
        
        self.y_col = QComboBox()
        self.vis_grid.addWidget(QLabel("Y轴:"), 2, 0)
        self.vis_grid.addWidget(self.y_col, 2, 1)
        
        self.plot_btn = QPushButton("生成图表")
        self.plot_btn.clicked.connect(self.generate_plot)
        self.vis_grid.addWidget(self.plot_btn, 3, 0, 1, 2)
        
        self.dashboard_btn = QPushButton("仪表盘")
        self.dashboard_btn.clicked.connect(self.show_dashboard)
        self.vis_grid.addWidget(self.dashboard_btn, 4, 0, 1, 2)
    
    def setup_report_tab(self):
        self.report_group = QGroupBox("报告生成")
        self.report_layout.addWidget(self.report_group)
        self.report_grid = QGridLayout(self.report_group)
        
        self.report_format = QComboBox()
        self.report_format.addItems(["pdf", "word", "markdown"])
        self.report_grid.addWidget(QLabel("格式:"), 0, 0)
        self.report_grid.addWidget(self.report_format, 0, 1)
        
        self.report_btn = QPushButton("生成报告")
        self.report_btn.clicked.connect(self.generate_report)
        self.report_grid.addWidget(self.report_btn, 1, 0, 1, 2)
    
    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择数据文件", "", 
            "所有支持格式 (*.csv *.xlsx *.xls *.json *.txt);;CSV文件 (*.csv);;Excel文件 (*.xlsx *.xls);;JSON文件 (*.json);;文本文件 (*.txt)")
        
        if file_path:
            self.file_label.setText(file_path)
            
            def load_data():
                return DataLoader.load_file(file_path)
            
            self.worker = WorkerThread(load_data)
            self.worker.finished.connect(self.on_data_loaded)
            self.worker.error.connect(self.show_error)
            self.worker.start()
    
    def on_data_loaded(self, df):
        if df is not None:
            self.current_df = df
            self.update_table_view(df)
            self.update_columns_list()
            self.data_info.setText(f"数据加载成功!\n行数: {len(df)}\n列数: {len(df.columns)}\n\n列名:\n{', '.join(df.columns.tolist())}")
        else:
            QMessageBox.warning(self, "错误", "无法加载文件")
    
    def show_error(self, msg):
        QMessageBox.critical(self, "错误", msg)
    
    def connect_mysql(self):
        host = self.mysql_host.text()
        port = int(self.mysql_port.text())
        user = self.mysql_user.text()
        password = self.mysql_pass.text()
        database = self.mysql_db.text()
        table = self.mysql_table.text()
        
        def connect():
            return DataLoader.load_mysql(host, port, user, password, database, table)
        
        self.worker = WorkerThread(connect)
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.error.connect(self.show_error)
        self.worker.start()
    
    def save_data(self):
        if self.current_df is None:
            QMessageBox.warning(self, "警告", "没有数据可保存")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "保存数据", "", 
            "加密数据文件 (*.data);;CSV文件 (*.csv);;Excel文件 (*.xlsx)")
        
        if file_path:
            if file_path.endswith('.data'):
                password, ok = QInputDialog.getText(self, "设置密码", "请输入加密密码:", QLineEdit.EchoMode.Password)
                if ok and password:
                    success = DataEncryptor.save_encrypted(self.current_df, file_path, password)
                    if success:
                        QMessageBox.information(self, "成功", "数据已加密保存")
                    else:
                        QMessageBox.warning(self, "错误", "保存失败")
            elif file_path.endswith('.csv'):
                self.current_df.to_csv(file_path, index=False, encoding='utf-8')
                QMessageBox.information(self, "成功", "数据已保存")
            elif file_path.endswith('.xlsx'):
                self.current_df.to_excel(file_path, index=False)
                QMessageBox.information(self, "成功", "数据已保存")
    
    def load_encrypted_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "加载加密数据", "", "加密数据文件 (*.data)")
        
        if file_path:
            password, ok = QInputDialog.getText(self, "输入密码", "请输入解密密码:", QLineEdit.EchoMode.Password)
            if ok and password:
                df = DataEncryptor.load_encrypted(file_path, password)
                if df is not None:
                    self.current_df = df
                    self.update_table_view(df)
                    self.update_columns_list()
                    QMessageBox.information(self, "成功", "数据加载成功")
                else:
                    QMessageBox.warning(self, "错误", "密码错误或文件损坏")
    
    def update_table_view(self, df):
        model = DataTableModel(df)
        self.table_view.setModel(model)
    
    def update_columns_list(self):
        if self.current_df is not None:
            columns = self.current_df.columns.tolist()
            self.columns_list.clear()
            self.columns_list.addItems(columns)
            self.x_col.clear()
            self.x_col.addItems(columns)
            self.y_col.clear()
            self.y_col.addItems(columns)
            self.target_col.clear()
            self.target_col.addItems(columns)
    
    def clean_data(self):
        if self.current_df is None:
            QMessageBox.warning(self, "警告", "请先加载数据")
            return
        
        config = {
            'remove_duplicates': self.remove_dup_cb.currentText() == '是',
            'fill_missing': self.fill_missing_cb.currentText() == '是',
            'missing_strategy': self.fill_strategy.currentText(),
            'remove_outliers': self.remove_outlier_cb.currentText() == '是',
            'outlier_method': self.outlier_method.currentText(),
            'standardize': self.standardize_cb.currentText() == '是'
        }
        
        result = DataCleaner.clean_data(self.current_df, config)
        self.cleaned_df = result['cleaned']
        
        info = "\n".join(result['info'])
        info += f"\n\n清洗前行数: {len(result['original'])}"
        info += f"\n清洗后行数: {len(result['cleaned'])}"
        info += f"\n移除重复: {result['removed_duplicates']} 行"
        info += f"\n移除异常值: {len(result['removed_outliers'])} 行"
        
        self.clean_info.setText(info)
        self.update_table_view(result['cleaned'])
        QMessageBox.information(self, "成功", "数据清洗完成")
    
    def show_descriptive(self):
        if self.current_df is None:
            QMessageBox.warning(self, "警告", "请先加载数据")
            return
        
        df_to_use = self.cleaned_df if self.cleaned_df is not None else self.current_df
        stats = DataAnalyzer.descriptive_statistics(df_to_use)
        
        if not stats.empty:
            self.analysis_result.setText(stats.to_string())
        else:
            QMessageBox.warning(self, "警告", "没有数值型列可分析")
    
    def show_correlation(self):
        if self.current_df is None:
            QMessageBox.warning(self, "警告", "请先加载数据")
            return
        
        df_to_use = self.cleaned_df if self.cleaned_df is not None else self.current_df
        corr = DataAnalyzer.correlation_analysis(df_to_use)
        
        if not corr.empty:
            self.analysis_result.setText(corr.to_string())
        else:
            QMessageBox.warning(self, "警告", "没有足够的数值型列进行相关分析")
    
    def show_pivot(self):
        if self.current_df is None:
            QMessageBox.warning(self, "警告", "请先加载数据")
            return
        
        df_to_use = self.cleaned_df if self.cleaned_df is not None else self.current_df
        
        if len(df_to_use.columns) < 3:
            QMessageBox.warning(self, "警告", "至少需要3列数据")
            return
        
        index_col = df_to_use.columns[0]
        columns_col = df_to_use.columns[1]
        values_col = df_to_use.columns[2]
        
        pivot = DataAnalyzer.pivot_analysis(df_to_use, index_col, columns_col, values_col)
        
        if not pivot.empty:
            self.analysis_result.setText(pivot.to_string())
    
    def show_dimension(self):
        if self.current_df is None:
            QMessageBox.warning(self, "警告", "请先加载数据")
            return
        
        df_to_use = self.cleaned_df if self.cleaned_df is not None else self.current_df
        
        if len(df_to_use.columns) < 2:
            QMessageBox.warning(self, "警告", "至少需要2列数据")
            return
        
        group_col = df_to_use.columns[0]
        value_col = df_to_use.columns[1]
        
        result = DataAnalyzer.dimension_analysis(df_to_use, group_col, value_col)
        
        if result:
            text = "分组统计:\n"
            for key, val in result.items():
                text += f"\n{key}:\n"
                if isinstance(val, dict):
                    for k, v in val.items():
                        text += f"  {k}: {v}\n"
                else:
                    text += f"  {val}\n"
            self.analysis_result.setText(text)
    
    def run_clustering(self):
        if self.current_df is None:
            QMessageBox.warning(self, "警告", "请先加载数据")
            return
        
        df_to_use = self.cleaned_df if self.cleaned_df is not None else self.current_df
        
        method = self.cluster_method.currentText()
        n_clusters = self.n_clusters.value()
        
        if method == 'KMeans':
            df_result, info = MLModel.cluster_kmeans(df_to_use, n_clusters)
        else:
            df_result, info = MLModel.cluster_dbscan(df_to_use)
        
        if 'error' not in info:
            self.current_df = df_result
            self.update_table_view(df_result)
            
            text = "聚类结果:\n"
            for key, val in info.items():
                text += f"{key}: {val}\n"
            text += f"\n聚类标签已添加到 'cluster' 列"
            self.ml_result.setText(text)
            
            QMessageBox.information(self, "成功", "聚类分析完成")
        else:
            QMessageBox.warning(self, "错误", info['error'])
    
    def run_classification(self):
        if self.current_df is None:
            QMessageBox.warning(self, "警告", "请先加载数据")
            return
        
        df_to_use = self.cleaned_df if self.cleaned_df is not None else self.current_df
        
        target_col = self.target_col.currentText()
        if not target_col:
            QMessageBox.warning(self, "警告", "请选择目标列")
            return
        
        result = MLModel.classify(df_to_use, target_col)
        
        if 'error' not in result:
            text = "分类结果:\n"
            text += f"准确率: {result['accuracy']:.4f}\n"
            text += f"精确率: {result['precision']:.4f}\n"
            text += f"召回率: {result['recall']:.4f}\n"
            text += f"F1分数: {result['f1']:.4f}\n"
            text += "\n特征重要性:\n"
            for feat, imp in sorted(result['feature_importance'].items(), key=lambda x: -x[1]):
                text += f"  {feat}: {imp:.4f}\n"
            self.ml_result.setText(text)
            QMessageBox.information(self, "成功", "分类完成")
        else:
            QMessageBox.warning(self, "错误", result['error'])
    
    def run_regression(self):
        if self.current_df is None:
            QMessageBox.warning(self, "警告", "请先加载数据")
            return
        
        df_to_use = self.cleaned_df if self.cleaned_df is not None else self.current_df
        
        target_col = self.target_col.currentText()
        if not target_col:
            QMessageBox.warning(self, "警告", "请选择目标列")
            return
        
        result = MLModel.regress(df_to_use, target_col)
        
        if 'error' not in result:
            text = "回归结果:\n"
            text += f"MSE: {result['mse']:.4f}\n"
            text += f"MAE: {result['mae']:.4f}\n"
            text += f"R2: {result['r2']:.4f}\n"
            text += "\n特征重要性:\n"
            for feat, imp in sorted(result['feature_importance'].items(), key=lambda x: -x[1]):
                text += f"  {feat}: {imp:.4f}\n"
            self.ml_result.setText(text)
            QMessageBox.information(self, "成功", "回归完成")
        else:
            QMessageBox.warning(self, "错误", result['error'])
    
    def generate_plot(self):
        print("DEBUG: generate_plot called")
        if self.current_df is None:
            QMessageBox.warning(self, "警告", "请先加载数据")
            return
        
        df_to_use = self.cleaned_df if self.cleaned_df is not None else self.current_df
        
        chart_type = self.chart_type.currentText()
        x_col = self.x_col.currentText()
        y_col = self.y_col.currentText()
        
        print(f"DEBUG: chart_type={chart_type}, x_col={x_col}, y_col={y_col}")
        
        if not x_col:
            QMessageBox.warning(self, "警告", "请选择X轴")
            return
        
        try:
            if chart_type == 'heatmap':
                numeric_df = df_to_use.select_dtypes(include=['number'])
                if numeric_df.empty:
                    QMessageBox.warning(self, "警告", "数据中没有数值列")
                    return
                fig = Visualizer.plot_heatmap(numeric_df)
            elif chart_type == 'histogram':
                fig = Visualizer.plot_histogram(df_to_use, x_col)
            elif chart_type == 'pie':
                if not y_col:
                    QMessageBox.warning(self, "警告", "请选择Y轴（数值列）")
                    return
                fig = Visualizer.generate_plot(df_to_use, chart_type, values=y_col, names=x_col)
            else:
                if not y_col:
                    QMessageBox.warning(self, "警告", "请选择Y轴")
                    return
                fig = Visualizer.generate_plot(df_to_use, chart_type, x=x_col, y=y_col)
            
            html = plot(fig, output_type='div')
            print("DEBUG: HTML generated successfully")
            self.result_view.setHtml(html)
            print("DEBUG: HTML set to result_view")
        except Exception as e:
            print(f"DEBUG: Error: {str(e)}")
            QMessageBox.warning(self, "错误", str(e))
    
    def show_dashboard(self):
        print("DEBUG: show_dashboard called")
        if self.current_df is None:
            QMessageBox.warning(self, "警告", "请先加载数据")
            return
        
        df_to_use = self.cleaned_df if self.cleaned_df is not None else self.current_df
        
        try:
            fig = Visualizer.plot_dashboard(df_to_use)
            print("DEBUG: Dashboard figure created")
            if fig is None or not hasattr(fig, 'to_dict'):
                QMessageBox.warning(self, "警告", "无法生成仪表盘，数据可能不包含数值列")
                return
            html = plot(fig, output_type='div')
            print("DEBUG: Dashboard HTML generated")
            self.result_view.setHtml(html)
            print("DEBUG: Dashboard HTML set to result_view")
        except Exception as e:
            print(f"DEBUG: Dashboard Error: {str(e)}")
            QMessageBox.warning(self, "错误", f"生成仪表盘失败: {str(e)}")
    
    def generate_report(self):
        if self.current_df is None:
            QMessageBox.warning(self, "警告", "请先加载数据")
            return
        
        df_to_use = self.cleaned_df if self.cleaned_df is not None else self.current_df
        
        format_type = self.report_format.currentText()
        file_path, _ = QFileDialog.getSaveFileName(self, "保存报告", "", 
            f"{format_type.upper()}文件 (*.{format_type})")
        
        if file_path:
            data = DataAnalyzer.analyze_data(df_to_use)
            success = ReportGenerator.generate_report(data, file_path, format_type)
            
            if success:
                QMessageBox.information(self, "成功", "报告已生成")
            else:
                QMessageBox.warning(self, "错误", "生成失败")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    main()
