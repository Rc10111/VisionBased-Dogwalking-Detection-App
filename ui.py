from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QGroupBox, QFrame, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class MainUI:
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 850)  # 增加高度
        MainWindow.setWindowTitle("遛狗牵绳检测系统")

        # 中央窗口部件
        self.central_widget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.central_widget)

        # 主布局
        self.main_layout = QHBoxLayout(self.central_widget)

        # 左侧控制面板
        self.setup_left_panel()

        # 右侧显示面板
        self.setup_right_panel()

    def setup_left_panel(self):
        """设置左侧控制面板"""
        left_panel = QFrame()
        left_panel.setMaximumWidth(320)  # 稍微加宽
        left_panel.setFrameStyle(QFrame.StyledPanel)

        left_layout = QVBoxLayout(left_panel)

        # 标题
        title_label = QLabel("遛狗牵绳检测系统")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        left_layout.addWidget(title_label)

        left_layout.addSpacing(10)

        # 文件选择区域
        file_group = QGroupBox("📁 文件选择")
        file_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        file_layout = QVBoxLayout(file_group)

        self.btn_select_image = QPushButton("📷 选择图片")
        self.btn_select_image.setMinimumHeight(45)
        self.btn_select_image.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        file_layout.addWidget(self.btn_select_image)

        self.btn_select_video = QPushButton("🎬 选择视频")
        self.btn_select_video.setMinimumHeight(45)
        self.btn_select_video.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        file_layout.addWidget(self.btn_select_video)

        left_layout.addWidget(file_group)

        left_layout.addSpacing(15)

        # 检测控制区域
        control_group = QGroupBox("⚙️ 检测控制")
        control_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        control_layout = QVBoxLayout(control_group)

        self.btn_start_detection = QPushButton("▶️ 开始检测")
        self.btn_start_detection.setMinimumHeight(45)
        self.btn_start_detection.setEnabled(False)
        self.btn_start_detection.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        control_layout.addWidget(self.btn_start_detection)

        left_layout.addWidget(control_group)

        left_layout.addSpacing(15)

        # 历史管理区域
        history_group = QGroupBox("📊 历史管理")
        history_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        history_layout = QVBoxLayout(history_group)

        self.btn_clear_history = QPushButton("🗑️ 清空记录")
        self.btn_clear_history.setMinimumHeight(40)
        self.btn_clear_history.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        history_layout.addWidget(self.btn_clear_history)

        left_layout.addWidget(history_group)

        left_layout.addSpacing(15)

        # 状态显示
        status_group = QGroupBox("📈 检测状态")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        status_layout = QVBoxLayout(status_group)

        self.label_status = QLabel("🟢 等待选择文件...")
        self.label_status.setWordWrap(True)
        self.label_status.setMinimumHeight(80)
        self.label_status.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        status_layout.addWidget(self.label_status)

        left_layout.addWidget(status_group)

        left_layout.addStretch()

        self.main_layout.addWidget(left_panel)

    def setup_right_panel(self):
        """设置右侧显示面板"""
        right_panel = QFrame()
        right_panel.setFrameStyle(QFrame.StyledPanel)

        right_layout = QVBoxLayout(right_panel)

        # 图片显示区域
        images_group = QGroupBox("🖼️ 图像显示")
        images_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        images_layout = QHBoxLayout(images_group)

        # 原图显示
        original_group = QGroupBox("📸 原图")
        original_layout = QVBoxLayout(original_group)
        self.label_original = QLabel()
        self.label_original.setMinimumSize(450, 320)
        self.label_original.setFrameStyle(QFrame.Box)
        self.label_original.setAlignment(Qt.AlignCenter)
        self.label_original.setText("原图将显示在这里")
        self.label_original.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 5px;
            }
        """)
        original_layout.addWidget(self.label_original)

        # 结果图显示
        result_group = QGroupBox("🔍 检测结果")
        result_layout = QVBoxLayout(result_group)
        self.label_result = QLabel()
        self.label_result.setMinimumSize(450, 320)
        self.label_result.setFrameStyle(QFrame.Box)
        self.label_result.setAlignment(Qt.AlignCenter)
        self.label_result.setText("检测结果将显示在这里")
        self.label_result.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 5px;
            }
        """)
        result_layout.addWidget(self.label_result)

        images_layout.addWidget(original_group)
        images_layout.addWidget(result_group)

        right_layout.addWidget(images_group)

        # 结果文本显示 - 使用滚动区域
        result_text_group = QGroupBox("📋 检测记录")
        result_text_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        result_text_layout = QVBoxLayout(result_text_group)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # 创建文本编辑框
        self.text_result = QTextEdit()
        self.text_result.setMinimumHeight(200)
        self.text_result.setReadOnly(True)
        self.text_result.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 11px;
            }
        """)

        # 设置提示文本
        self.text_result.setPlaceholderText(
            "检测记录将显示在这里...\n"
            "每次检测都会添加新的记录\n"
            "可以向上滚动查看历史记录"
        )

        scroll_area.setWidget(self.text_result)
        result_text_layout.addWidget(scroll_area)

        right_layout.addWidget(result_text_group)

        self.main_layout.addWidget(right_panel)