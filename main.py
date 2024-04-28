import cv2
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QImage, QMouseEvent, QPixmap
from PySide6.QtWidgets import QFileDialog, QLabel
from PySide6.QtCore import Qt
from datetime import datetime
import cv_funcs
import curves_adjust

class MyLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
    def setCurve(self, curves, main):
        self.main = main
        self.curves = curves
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.curves.callbackMouseEvent("press", self.mapTo255(event.position()))
            self.main.curves_adjust()
    def mouseMoveEvent(self, event):
        x, y = self.mapTo255(event.position())
        x, y = min(255, y), min(255, y)
        x, y = max(0, x), max(0, y)
        self.curves.callbackMouseEvent("move", self.mapTo255(event.position()))
        self.main.curves_adjust()
    def mouseReleaseEvent(self, event) -> None:
        self.curves.callbackMouseEvent("up", self.mapTo255(event.position()))
        self.main.curves_adjust()
    def mapTo255(self, pos):
        label_size = self.size()
        x = int(pos.x() / label_size.width() * 255)
        y = int(pos.y() / label_size.height() * 255)
        return (x, y)
    
class MyUiLoader(QUiLoader):
    def createWidget(self, className, parent=None, name=''):
        if className == 'MyLabel':
            return MyLabel(parent)
        return super().createWidget(className, parent, name)


uiLoader = MyUiLoader()
class main_window():
    handle_img = None
    small_img = None
    def __init__(self):
        self.ui = uiLoader.load(r"D:/Code/Code_Py/image_handle/main.ui")
        self.prepare()
        self.ui.show()
         
    def prepare(self):
        self.ui.actionNewFile.triggered.connect(self.open_file)
        self.ui.cbox_prev_channel.addItems(["RGB", "R", "G", "B"])
        self.ui.cbox_curv_channel.addItems(["RGB", "R", "G", "B"])
        self.ui.cbox_function.addItems(["调整亮度", "调整饱和度"])
        self.ui.slider_right.valueChanged.connect(lambda: self.image_enhance(self.ui.label_prev))
        self.ui.button_run.clicked.connect(lambda: self.image_enhance(self.ui.label_main)) # 增加代码复用度
        self.ui.cbox_function.currentIndexChanged.connect(lambda: self.image_enhance(self.ui.label_main))
        
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
        
    def curves_adjust(self):
        print("mfklmakmldv")
        self.display_image(self.ui.label_main, self.handle_img)
        self.ca.chan_cho(self.ui.cbox_curv_channel.currentText())
        self.ca.update()
    def display_image_info(self, file_name, img):
        height, width, _ = img.shape
        size = os.path.getsize(file_name) /(1024)
        file_type = os.path.splitext(file_name)[1]
        modified_time = datetime.fromtimestamp(os.path.getmtime(file_name)).strftime('%Y-%m-%d %H:%M:%S')
        info = f"Resolution: {width}x{height}\nSize: {size:.2f} KB\nType: {file_type}\nModified: {modified_time}"
        self.ui.img_info.setText(info)
        
    def __display_image_when_open(self, file_name):
        img = cv2.imread(file_name)
        height, width, _ = img.shape
        img_small = cv2.resize(img, (width // 8, height // 8))
        self.handle_img = img
        self.small_img = img_small
        self.ca = curves_adjust.Curves(self.handle_img, self.ui.label_curv, self.ui.label_main)
        self.ui.label_curv.setCurve(self.ca, self)
        self.ca.update()
        self.ui.cbox_curv_channel.currentIndexChanged.connect(self.curves_adjust)
        self.display_image(self.ui.label_main, img)
        self.display_image(self.ui.label_prev, img_small)
        # 显示图片和图片预览
        self.display_image_info(file_name, img)
        # 显示图片信息
        
    
        
if __name__ == '__main__':
    app = QApplication([])
    window = main_window()
    window.ui.showMaximized()
    app.exec()