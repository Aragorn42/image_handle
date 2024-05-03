import cv2
from PySide6.QtCore import Qt
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

def calc_hist(img, chan: str): # return numpy.ndarray
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
        print("Invalid channel")
    return hist, color