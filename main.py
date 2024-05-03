import cv2
import os
from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
import cv_funcs
import curves_adjust
import MyWidget

uiLoader = MyWidget.MyUiLoader()

class main_window:
    handle_img = None
    small_img = None
    def __init__(self):
        self.ui = uiLoader.load("main.ui")
        self.prepare()
        self.ui.show()
         
    def prepare(self):
        self.ca = None # 先占位, 还没有导入图片
        self.ui.actionNewFile.triggered.connect(self.open_file)
        self.ui.cbox_prev_channel.addItems(["RGB", "R", "G", "B"])
        self.ui.cbox_curv_channel.addItems(["RGB", "R", "G", "B"])
        self.ui.cbox_function.addItems(["调整亮度", "调整饱和度"])
        self.ui.cbox_curv_channel.currentIndexChanged.connect(lambda x: self.ca.update() if self.ca\
            else self.open_file()) # 如果还未导入图片, 则导入图片
        self.ui.slider_right.valueChanged.connect(lambda: self.adjust_by_bar(self.ui.label_prev))
        self.ui.button_run.clicked.connect(lambda: self.adjust_by_bar(self.ui.label_main)) # 增加代码复用度
        self.ui.cbox_function.currentIndexChanged.connect(lambda: self.adjust_by_bar(self.ui.label_main))
    def prepare_after_load_img(self, file_name):
        img = cv2.imread(file_name)
        height, width, _ = img.shape
        img_small = cv2.resize(img, (width // 8, height // 8))
        self.handle_img = img
        self.small_img = img_small

        self.ca = curves_adjust.Curves(self, self.handle_img, self.ui.label_curv, self.ui.label_main, self.ui.label_hist)
        self.ui.label_curv.setCurve(self.ca, self)
        self.ca.update()

        self.display_image(self.ui.label_main, img)
        self.display_image(self.ui.label_prev, img_small)
    def adjust_by_bar(self, label):
        if self.handle_img is None:
            self.open_file()
        if label == self.ui.label_main:
            img = self.handle_img
        else:
            img = self.small_img
            
        if self.ui.cbox_function.currentText() == "调整亮度":
            value = self.ui.slider_right.value()
            img = cv_funcs.brightness_change(value, img)
            self.display_image(label, img)
            
        elif self.ui.cbox_function.currentText() == "调整饱和度":
            value = self.ui.slider_right.value()
            img = cv_funcs.Saturation(img, value)
            self.display_image(label, img)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self.ui, "Open file", "", "Images (*.png *.xpm *.jpg)")
        if file_name:
            self.prepare_after_load_img(file_name)
    
    def display_image(self, label, img):
        label.clear()
        try:
            height, width, _ = img.shape
            bytesPerLine = 3 * width
            qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(qImg)
            pixmap = pixmap.scaled(label.width(), label.height(),\
                                   Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(pixmap)
        except:
            label.setPixmap(img)


if __name__ == '__main__':
    app = QApplication([])
    window = main_window()
    window.ui.showMaximized()
    app.exec()