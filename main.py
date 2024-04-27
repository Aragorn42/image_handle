import cv2
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import Qt
from datetime import datetime
import cv_funcs
uiLoader = QUiLoader()

class main_window():
    handle_img = None
    small_img = None
    def __init__(self):
        self.ui = QUiLoader().load(r"D:\Code\Code_Py\GNU_PS\Ture_main.ui")
        self.prepare()
        self.ui.show()
        
    def prepare(self):
        self.ui.actionNewFile.triggered.connect(self.open_file)
        self.ui.cbox_prev_channel.addItems(["RGB", "R", "G", "B"])
        self.ui.cbox_curv_channel.addItems(["RGB", "R", "G", "B"])
        self.ui.cbox_function.addItem("调整亮度")
        self.ui.cbox_function.addItem("调整饱和度")
        self.ui.slider_right.valueChanged.connect(lambda: self.image_enhance(self.ui.label_prev))
        self.ui.button_run.clicked.connect(lambda: self.image_enhance(self.ui.label_main)) # 增加代码复用度
        

    def image_enhance(self, label):
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
            self.__display_image_when_open(file_name)
    
    def display_image(self, label, img):
        height, width, _ = img.shape
        bytesPerLine = 3 * width
        qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(qImg)
        pixmap = pixmap.scaled(label.width(), label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pixmap)
    
    def display_image_info(self, file_name, img):
        height, width, _ = img.shape
        size = os.path.getsize(file_name) /(1024)
        file_type = os.path.splitext(file_name)[1]
        modified_time = datetime.fromtimestamp(os.path.getmtime(file_name)).strftime('%Y-%m-%d %H:%M:%S')
        info = f"Resolution: {width}x{height}\nSize: {size:.2f} KB\nType: {file_type}\nModified: {modified_time}"
        self.ui.img_info.setText(info)
        
    def __display_image_when_open(self, file_name):
        img = cv2.imread(file_name)
        self.display_image(self.ui.label_main, img)
        height, width, _ = img.shape
        img_small = cv2.resize(img, (width // 8, height // 8))
        self.handle_img = img
        self.small_img = img_small
        self.display_image(self.ui.label_prev, img_small)
        # 显示图片和图片预览
        self.display_image_info(file_name, img)
        # 显示图片信息
        
    
        
if __name__ == '__main__':
    app = QApplication([])
    window = main_window()
    window.ui.showMaximized()
    app.exec()