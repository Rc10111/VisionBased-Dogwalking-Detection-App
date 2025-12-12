import cv2
import torch
import numpy as np
from pathlib import Path
import tempfile
import os
from ultralytics import YOLO


class DogLeashDetector:
    def __init__(self, model_path=None):
        """
        初始化检测器

        Args:
            model_path: YOLOv11模型路径
        """
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.load_model(model_path)

    def load_model(self, model_path):
        """加载YOLOv11模型"""
        try:
            if model_path is None:
                # 只需要修改这个模型名称即可
                model_name = "修改后的4580"  # 在这里改模型名字

                # 尝试在默认路径查找模型
                default_paths = [
                    'runs/detect/train/weights/best.pt',  # 你的训练模型路径
                    f'D:/pycharm 项目库/遛狗不牵绳/models/{model_name}.pt',  # 你的模型库路径
                    f'models/{model_name}.pt',
                    f'{model_name}.pt',
                    'best.pt'
                ]
                for path in default_paths:
                    if Path(path).exists():
                        model_path = path
                        print(f"找到模型文件: {path}")
                        break

            if model_path and Path(model_path).exists():
                # 使用ultralytics加载YOLOv11模型
                self.model = YOLO(model_path)
                print(f"模型加载成功: {model_path}")
                print(f"设备: {self.device}")

            else:
                # 如果没有找到模型文件
                available_models = []
                for root, dirs, files in os.walk('.'):
                    for file in files:
                        if file.endswith('.pt'):
                            available_models.append(os.path.join(root, file))

                if available_models:
                    print("找到以下模型文件:")
                    for model in available_models:
                        print(f"  - {model}")
                    raise FileNotFoundError(f"请指定正确的模型路径，或将模型文件放在以下位置之一: {default_paths}")
                else:
                    raise FileNotFoundError(f"未找到模型文件，请检查模型路径: {model_path}")

        except Exception as e:
            print(f"模型加载失败: {e}")
            raise e

    def detect(self, image_path):
        """
        检测图片中的遛狗牵绳

        Args:
            image_path: 图片路径

        Returns:
            检测结果
        """
        if self.model is None:
            raise ValueError("模型未加载")

        try:
            # 使用YOLOv11进行预测
            results = self.model.predict(
                source=image_path,
                conf=0.25,  # 置信度阈值
                iou=0.45,  # IOU阈值
                save=False  # 不自动保存，我们自己处理
            )
            return results
        except Exception as e:
            print(f"检测失败: {e}")
            return None

    def detect_frame(self, frame):
        """
        检测视频帧

        Args:
            frame: 视频帧 (numpy array)

        Returns:
            检测结果
        """
        if self.model is None:
            raise ValueError("模型未加载")

        try:
            # 使用YOLOv11进行预测
            results = self.model.predict(
                source=frame,
                conf=0.25,
                iou=0.45,
                save=False
            )
            return results
        except Exception as e:
            print(f"帧检测失败: {e}")
            return None

    def draw_detections(self, image_path, results):
        """
        在图片上绘制检测框并保存结果

        Args:
            image_path: 原图片路径
            results: 检测结果

        Returns:
            结果图片路径
        """
        try:
            if not results or len(results) == 0:
                return image_path

            # 使用YOLO的结果绘制功能
            result = results[0]

            # 绘制检测框
            plotted = result.plot()

            # 保存临时文件
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, f"detection_result_{os.path.basename(image_path)}")

            # 保存图片
            cv2.imwrite(output_path, plotted)

            return output_path

        except Exception as e:
            print(f"绘制检测框失败: {e}")
            return image_path

    def draw_detections_on_frame(self, frame, results):
        """
        在视频帧上绘制检测框

        Args:
            frame: 原视频帧
            results: 检测结果

        Returns:
            带检测框的帧
        """
        try:
            if not results or len(results) == 0:
                return frame

            result = results[0]
            plotted_frame = result.plot()
            return plotted_frame

        except Exception as e:
            print(f"绘制帧检测框失败: {e}")
            return frame

    def get_detection_info(self, results):
        """
        获取检测结果的详细信息

        Args:
            results: 检测结果

        Returns:
            检测信息字典
        """
        if not results or len(results) == 0:
            return {"detections": []}

        result = results[0]
        detection_info = {
            "detections": [],
            "leash_detected": False,
            "dog_detected": False
        }

        if hasattr(result, 'boxes') and result.boxes is not None:
            boxes = result.boxes
            for i in range(len(boxes)):
                class_id = int(boxes.cls[i])
                class_name = result.names[class_id]
                confidence = float(boxes.conf[i])

                detection_info["detections"].append({
                    "class_name": class_name,
                    "confidence": confidence,
                    "class_id": class_id
                })

                # 根据你的实际类别名称进行判断
                class_name_lower = class_name.lower()

                # 假设你的类别是：withdog(牵绳狗), withoutdog(未牵绳狗), leash(绳子)等
                if 'withdog' in class_name_lower or 'leash' in class_name_lower or 'with_leash' in class_name_lower:
                    detection_info["leash_detected"] = True
                    detection_info["dog_detected"] = True
                elif 'withoutdog' in class_name_lower or 'no_leash' in class_name_lower:
                    detection_info["dog_detected"] = True
                    # leash_detected 保持 False
                elif 'dog' in class_name_lower and 'leash' not in class_name_lower:
                    detection_info["dog_detected"] = True
                elif 'leash' in class_name_lower or 'rope' in class_name_lower:
                    detection_info["leash_detected"] = True

        return detection_info