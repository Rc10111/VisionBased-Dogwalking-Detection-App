from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QGroupBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class MainUI:
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)
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
        left_panel.setMaximumWidth(300)
        left_panel.setFrameStyle(QFrame.StyledPanel)

        left_layout = QVBoxLayout(left_panel)

        # 标题
        title_label = QLabel("遛狗牵绳检测系统")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title_label)

        left_layout.addSpacing(20)

        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout(file_group)

        self.btn_select_image = QPushButton("选择图片")
        self.btn_select_image.setMinimumHeight(40)
        file_layout.addWidget(self.btn_select_image)

        self.btn_select_video = QPushButton("选择视频")
        self.btn_select_video.setMinimumHeight(40)
        file_layout.addWidget(self.btn_select_video)

        left_layout.addWidget(file_group)

        left_layout.addSpacing(20)

        # 检测控制区域
        control_group = QGroupBox("检测控制")
        control_layout = QVBoxLayout(control_group)

        self.btn_start_detection = QPushButton("开始检测")
        self.btn_start_detection.setMinimumHeight(40)
        self.btn_start_detection.setEnabled(False)
        control_layout.addWidget(self.btn_start_detection)

        left_layout.addWidget(control_group)

        left_layout.addSpacing(20)

        # 状态显示
        status_group = QGroupBox("检测状态")
        status_layout = QVBoxLayout(status_group)

        self.label_status = QLabel("等待选择文件...")
        self.label_status.setWordWrap(True)
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
        images_group = QGroupBox("图像显示")
        images_layout = QHBoxLayout(images_group)

        # 原图显示
        original_group = QGroupBox("原图")
        original_layout = QVBoxLayout(original_group)
        self.label_original = QLabel()
        self.label_original.setMinimumSize(400, 300)
        self.label_original.setFrameStyle(QFrame.Box)
        self.label_original.setAlignment(Qt.AlignCenter)
        self.label_original.setText("原图将显示在这里")
        original_layout.addWidget(self.label_original)

        # 结果图显示
        result_group = QGroupBox("检测结果")
        result_layout = QVBoxLayout(result_group)
        self.label_result = QLabel()
        self.label_result.setMinimumSize(400, 300)
        self.label_result.setFrameStyle(QFrame.Box)
        self.label_result.setAlignment(Qt.AlignCenter)
        self.label_result.setText("检测结果将显示在这里")
        result_layout.addWidget(self.label_result)

        images_layout.addWidget(original_group)
        images_layout.addWidget(result_group)

        right_layout.addWidget(images_group)

        # 结果文本显示
        result_text_group = QGroupBox("检测结果")
        result_text_layout = QVBoxLayout(result_text_group)

        self.text_result = QTextEdit()
        self.text_result.setMaximumHeight(150)
        self.text_result.setPlaceholderText("检测结果将显示在这里...")
        result_text_layout.addWidget(self.text_result)

        right_layout.addWidget(result_text_group)

        self.main_layout.addWidget(right_panel)