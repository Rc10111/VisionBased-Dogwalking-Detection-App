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
                # 如果没有检测结果，也显示原图作为结果图
                self.display_result_image(image_path)
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

                    # 记录检测结果（改为记录检测信息而不是文本）
                    detection_info = self.detector.get_detection_info(results)
                    self.video_results.append(detection_info)

                    # 更新状态
                    current_status = self.analyze_detection_results(results)
                    self.ui.label_status.setText(f"检测中... 当前状态: {current_status.split(chr(10))[0]}")
                else:
                    self.display_cv_image(frame, self.ui.label_result)
                    # 记录空结果
                    self.video_results.append({"detections": [], "leash_detected": False, "dog_detected": False})
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

        # 调试信息：打印检测到的对象
        detections = detection_info["detections"]
        detection_text = "检测到的对象: "
        for det in detections:
            detection_text += f"{det['class_name']}({det['confidence']:.2f}) "

        dog_detected = detection_info["dog_detected"]
        leash_detected = detection_info["leash_detected"]

        # 根据你的实际类别进行判断
        class_names = [det['class_name'].lower() for det in detections]

        if any('withdog' in name for name in class_names) or (dog_detected and leash_detected):
            return "文明遛狗：已牵绳\n" + detection_text
        elif any('withoutdog' in name for name in class_names) or (dog_detected and not leash_detected):
            return "不文明遛狗：未牵绳\n" + detection_text
        elif dog_detected:
            return "检测到狗狗但无法确定是否牵绳\n" + detection_text
        else:
            return "未检测到狗狗\n" + detection_text

    def get_final_video_result(self):
        """获取视频的最终检测结果"""
        if not self.video_results:
            return "未检测到有效结果"

        # 统计各种检测结果
        result_categories = []
        class_count = {}
        total_frames = len(self.video_results)
        frames_with_dog = 0
        frames_with_leash = 0
        frames_with_detection = 0

        for result in self.video_results:
            # 统计检测类别
            for detection in result["detections"]:
                class_name = detection["class_name"]
                class_count[class_name] = class_count.get(class_name, 0) + 1

            # 统计检测状态
            if result["detections"]:
                frames_with_detection += 1
            if result["dog_detected"]:
                frames_with_dog += 1
            if result["leash_detected"]:
                frames_with_leash += 1

            # 分类当前帧的结果
            if result["dog_detected"]:
                if result["leash_detected"]:
                    result_categories.append("文明遛狗：已牵绳")
                else:
                    result_categories.append("不文明遛狗：未牵绳")
            else:
                result_categories.append("未检测到狗狗")

        # 计算出现最多的结果
        if result_categories:
            final_category = max(set(result_categories), key=result_categories.count)
            category_count = result_categories.count(final_category)
        else:
            final_category = "无检测结果"
            category_count = 0

        # 构建详细结果文本
        result_text = f"视频检测完成！\n"
        result_text += f"总帧数: {total_frames}\n"
        result_text += f"有检测结果的帧数: {frames_with_detection}\n"
        result_text += f"检测到狗狗的帧数: {frames_with_dog}\n"
        result_text += f"检测到牵绳的帧数: {frames_with_leash}\n\n"
        result_text += f"最终检测结果: {final_category} (出现{category_count}次)\n\n"
        result_text += "检测到的对象统计:\n"

        if class_count:
            for class_name, count in class_count.items():
                percentage = (count / total_frames) * 100
                result_text += f"  {class_name}: {count}次 ({percentage:.1f}%)\n"
        else:
            result_text += "  未检测到任何对象\n"

        return result_text

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
        # 确保在主线程中更新UI
        self.ui.text_result.setPlainText(result_text)
        # 强制刷新UI
        self.ui.text_result.repaint()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()