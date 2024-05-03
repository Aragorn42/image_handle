import cv2
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor, QPainter
from datetime import datetime
import os
def brightness_change(value, img):
    img = cv2.convertScaleAbs(img, alpha=1, beta=value)
    return img

def Saturation(img, value):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv = hsv.astype('float32')

    # Adjust the saturation
    hsv[..., 1] = hsv[..., 1] * (1 + value / 255.0)
    hsv[..., 1][hsv[..., 1] > 255] = 255
    hsv[..., 1][hsv[..., 1] < 0] = 0
    hsv = hsv.astype('uint8')
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    return img

def __calc_hist(img, chan: str): # return numpy.ndarray
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
# only in cv_funcs.display_histogram()

def display_histogram(label, chan, img): # only in Curves.update()
    hist, color = __calc_hist(img, chan)
    pixmap = QPixmap(label.width(), label.height())
    pixmap.fill(QColor(223, 223, 223))
    painter = QPainter(pixmap)
    painter.setPen(color)
    for i in range(256):
        height = hist[i][0] * label.height() / max(hist)[0]  # Access the value in the single-element array
        painter.drawLine(i, label.height(), i, label.height() - height)
    painter.end()
    return pixmap

def display_image_info(label, file_name, img):
    height, width, _ = img.shape
    size = os.path.getsize(file_name) /(1024)
    file_type = os.path.splitext(file_name)[1]
    modified_time = datetime.fromtimestamp(os.path.getmtime(file_name)).strftime('%Y-%m-%d %H:%M:%S')
    info = f"Resolution: {width}x{height}\nSize: {size:.2f} KB\nType: {file_type}\nModified: {modified_time}"
    label.setText(info)