# DataAnalyser - 全功能开源数据分析工具

一个轻量级、全中文、一键操作的数据分析工具，支持数据导入、清洗、分析、建模、可视化和报告生成。

## ✨ 功能特性

### 1. 数据导入
- 支持 CSV、Excel (.xlsx/.xls)、JSON、TXT 文件
- 支持 MySQL 数据库连接
- 一键加载数据

### 2. 数据清洗
- 自动去重
- 缺失值填充（均值/中位数/众数）
- 异常值检测（Z-score/IQR 方法）
- 格式标准化

### 3. 数据分析
- 描述性统计（均值、标准差、分位数等）
- 相关性分析（皮尔逊相关系数）
- 维度拆解（分组统计）
- 透视表分析

### 4. 机器学习
- 聚类分析（KMeans、DBSCAN）
- 分类算法（随机森林）
- 回归分析（线性回归、随机森林回归）
- 预测功能

### 5. 可视化
- 自动推荐图表类型
- 支持折线图、柱状图、饼图、散点图、热力图、直方图、箱线图
- 交互式仪表盘
- 基于 Plotly 的交互式图表

### 6. 报告生成
- 一键导出分析报告
- 支持 PDF、Word、Markdown 格式
- 包含数据概览、描述统计、相关性分析等内容

### 7. 数据存档
- 自定义加密格式 `.data`
- 使用 Fernet 加密算法
- 防篡改、防作弊

## 🛠️ 技术栈

- **语言**: Python 3.10+
- **GUI框架**: PyQt6
- **数据处理**: Pandas, NumPy
- **可视化**: Matplotlib, Seaborn, Plotly
- **机器学习**: Scikit-learn
- **数据库**: MySQL Connector
- **报告生成**: ReportLab (PDF), python-docx (Word), Markdown
- **加密**: Cryptography (Fernet)

## 📦 安装步骤

### 1. 克隆仓库
```bash
git clone https://github.com/your-username/DataAnalyser.git
cd DataAnalyser
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行程序
```bash
python main.py
```
或双击 `start.bat`（Windows）

## 📖 使用说明

1. **启动程序**: 运行 `python main.py` 或双击 `start.bat`
2. **加载数据**: 在"数据导入"标签页点击"选择文件"
3. **数据清洗**: 使用"数据清洗"标签页进行预处理
4. **数据分析**: 在"数据分析"标签页进行统计分析
5. **机器学习**: 使用"机器学习"标签页进行建模
6. **可视化**: 在"可视化"标签页生成图表
7. **报告生成**: 在"报告生成"标签页导出报告

## 📁 项目结构

```
DataAnalyser/
├── core/                 # 核心模块
│   ├── data_loader.py    # 数据加载
│   ├── data_cleaner.py   # 数据清洗
│   ├── data_analyzer.py  # 数据分析
│   ├── machine_learning.py # 机器学习
│   ├── visualization.py  # 可视化
│   ├── report_generator.py # 报告生成
│   └── data_encryptor.py # 数据加密
├── gui/                  # GUI界面
│   └── main_window.py    # 主窗口
├── main.py               # 入口文件
├── requirements.txt      # 依赖清单
├── start.bat             # Windows启动脚本
└── README.md             # 项目说明
```

## 🤝 贡献指南

欢迎贡献代码！请按照以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📧 联系方式

如有问题或建议，请提交 Issue 或发送邮件。

---

**DataAnalyser** - 让数据分析更简单！
