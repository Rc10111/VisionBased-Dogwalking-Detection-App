import sys
import os
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import torch
from ui import MainUI
from detector import DogLeashDetector


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = MainUI()
        self.ui.setupUi(self)

        # 初始化检测器
        self.detector = DogLeashDetector()

        # 连接信号和槽
        self.connect_signals()

        # 当前检测状态
        self.is_detecting = False
        self.video_capture = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_video_frame)

        # 视频检测结果统计
        self.video_results = []

    def connect_signals(self):
        """连接UI信号和槽函数"""
        self.ui.btn_select_image.clicked.connect(self.select_image)
        self.ui.btn_select_video.clicked.connect(self.select_video)
        self.ui.btn_start_detection.clicked.connect(self.toggle_detection)

    def select_image(self):
        """选择图片文件"""
        from PyQt5.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            self.process_image(file_path)

    def select_video(self):
        """选择视频文件"""
        from PyQt5.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频", "",
            "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )

        if file_path:
            self.process_video(file_path)

    def process_image(self, image_path):
        """处理图片检测"""
        try:
            # 使用检测器进行预测
            results = self.detector.detect(image_path)

            # 显示原图
            self.display_image(image_path, self.ui.label_original)

            # 显示检测结果
            if results and len(results) > 0:
                result_image = self.detector.draw_detections(image_path, results)
                self.display_result_image(result_image)

                # 分析检测结果
                analysis = self.analyze_detection_results(results)
                self.display_detection_result(analysis)
            else:
                self.display_detection_result("未检测到遛狗场景")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"图片处理失败: {str(e)}")

    def process_video(self, video_path):
        """处理视频文件"""
        try:
            self.video_path = video_path
            self.video_capture = cv2.VideoCapture(video_path)
            self.video_results = []

            # 显示第一帧
            ret, frame = self.video_capture.read()
            if ret:
                self.display_cv_image(frame, self.ui.label_original)

            self.ui.btn_start_detection.setEnabled(True)
            self.ui.label_status.setText("准备开始视频检测")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"视频加载失败: {str(e)}")

    def toggle_detection(self):
        """开始/停止视频检测"""
        if not self.is_detecting:
            # 开始检测
            if self.video_capture:
                self.is_detecting = True
                self.ui.btn_start_detection.setText("停止检测")
                self.timer.start(30)  # 30ms更新一帧
                self.video_results = []
        else:
            # 停止检测
            self.is_detecting = False
            self.ui.btn_start_detection.setText("开始检测")
            self.timer.stop()

            # 显示最终统计结果
            if self.video_results:
                final_result = self.get_final_video_result()
                self.display_detection_result(final_result)

    def update_video_frame(self):
        """更新视频帧"""
        if self.video_capture and self.is_detecting:
            ret, frame = self.video_capture.read()
            if ret:
                # 显示原帧
                self.display_cv_image(frame, self.ui.label_original)

                # 进行检测
                results = self.detector.detect_frame(frame)

                if results and len(results) > 0:
                    # 绘制检测框
                    result_frame = self.detector.draw_detections_on_frame(frame, results)
                    self.display_cv_image(result_frame, self.ui.label_result)

                    # 记录检测结果
                    analysis = self.analyze_detection_results(results)
                    self.video_results.append(analysis)

                    # 更新状态
                    self.ui.label_status.setText(f"检测中... 当前状态: {analysis}")
                else:
                    self.display_cv_image(frame, self.ui.label_result)
                    self.ui.label_status.setText("检测中... 未发现目标")
            else:
                # 视频结束
                self.toggle_detection()

    def analyze_detection_results(self, results):
        """分析检测结果"""
        if not results or len(results) == 0:
            return "未检测到目标"

        # 使用检测器获取详细信息
        detection_info = self.detector.get_detection_info(results)

        dog_detected = detection_info["dog_detected"]
        leash_detected = detection_info["leash_detected"]

        if dog_detected:
            if leash_detected:
                return "文明遛狗：已牵绳"
            else:
                return "不文明遛狗：未牵绳"
        else:
            return "未检测到狗狗"
    def get_final_video_result(self):
        """获取视频的最终检测结果"""
        if not self.video_results:
            return "未检测到有效结果"

        # 统计各种结果的出现次数
        result_count = {}
        for result in self.video_results:
            result_count[result] = result_count.get(result, 0) + 1

        # 返回出现最多的结果
        final_result = max(result_count.items(), key=lambda x: x[1])
        return f"最终检测结果: {final_result[0]} (出现{final_result[1]}次)"

    def display_image(self, image_path, label):
        """显示图片到QLabel"""
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(label.width(), label.height(),
                                      Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaled_pixmap)

    def display_cv_image(self, cv_img, label):
        """显示OpenCV图片到QLabel"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(label.width(), label.height(),
                                      Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaled_pixmap)

    def display_result_image(self, image_path):
        """显示结果图片"""
        self.display_image(image_path, self.ui.label_result)

    def display_detection_result(self, result_text):
        """显示检测结果文本"""
        self.ui.text_result.setText(result_text)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()