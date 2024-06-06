import cv2
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor, QPainter
from datetime import datetime
from math import fabs, sin, cos, radians
import os


class Funcs:
    def __init__(self):
        pass
    def brightness_change(self, value, img): # 亮度调整
        img = cv2.convertScaleAbs(img, alpha=1, beta=value)
        return img

    def Saturation(self, img, value): # 对比度调整
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv = hsv.astype('float32')

        # Adjust the saturation
        hsv[..., 1] = hsv[..., 1] * (1 + value / 255.0)
        hsv[..., 1][hsv[..., 1] > 255] = 255
        hsv[..., 1][hsv[..., 1] < 0] = 0
        hsv = hsv.astype('uint8')
        img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        return img

    def _calc_hist_(self, img, chan: str): # return numpy.ndarray
        if chan == "RGB":
            hist = cv2.calcHist([img], [0], None, [256], [0, 256]) + cv2.calcHist([img], [1], None, [256], [0, 256]) + cv2.calcHist([img], [2], None, [256], [0, 256])
            color = Qt.black
        elif chan == "B":
            hist = cv2.calcHist([img], [0], None, [256], [0, 256])
            color = Qt.blue
        elif chan == "G":
            hist = cv2.calcHist([img], [1], None, [256], [0, 256])
            color = Qt.green
        elif chan == "R":
            hist = cv2.calcHist([img], [2], None, [256], [0, 256])
            color = Qt.red
        else:
            hist, color = None, None
            print("Invalid channel")
        return hist, color
    # 计算显示直方图需要的信息
    
    def display_histogram(self, label, chan, img):
        hist, color = self._calc_hist_(img, chan)
        pixmap = QPixmap(label.width(), label.height())
        pixmap.fill(QColor(223, 223, 223))
        painter = QPainter(pixmap)
        painter.setPen(color)
        for i in range(256):
            height = hist[i][0] * label.height() / max(hist)[0]  # Access the value in the single-element array
            painter.drawLine(i, label.height(), i, label.height() - height)
        painter.end()
        return pixmap
    # 在label中显示直方图
    
    def rotate_image(img, angle):
        h, w = img.shape[:2]
        center = (w / 2, h / 2)
        scale = 1.0
        # 2.1获取M矩阵
        """
        M矩阵
        [
        cosA -sinA (1-cosA)*centerX+sinA*centerY
        sinA cosA  -sinA*centerX+(1-cosA)*centerY
        ]
        """
        M = cv2.getRotationMatrix2D(center, angle, scale)
        # 2.2 新的宽高，radians(angle) 把角度转为弧度 sin(弧度)
        new_H = int(w * fabs(sin(radians(angle))) + h * fabs(cos(radians(angle))))
        new_W = int(h * fabs(sin(radians(angle))) + w * fabs(cos(radians(angle))))
        # 2.3 平移
        M[0, 2] += (new_W - w) / 2
        M[1, 2] += (new_H - h) / 2
        rotate = cv2.warpAffine(img, M, (new_W, new_H), borderValue=(0, 0, 0))
        return rotate

    def display_image_info(self, label, file_name, img):
        height, width, _ = img.shape
        size = os.path.getsize(file_name) /(1024)
        file_type = os.path.splitext(file_name)[1]
        modified_time = datetime.fromtimestamp(os.path.getmtime(file_name)).strftime('%Y-%m-%d %H:%M:%S')
        info = f"Resolution: {width}x{height}\nSize: {size:.2f} KB\nType: {file_type}\nModified: {modified_time}"
        label.setText(info)
    # 显示图片信息, 暂时没有用到