import cv2
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
        self.funcs = cv_funcs.Funcs()
        self.ui = uiLoader.load("../../include/main.ui")
        self.prepare()
        self.ui.show()
         
    def prepare(self):
        self.ca = None # 先占位, 还没有导入图片
        self.ui.actionNewFile.triggered.connect(self.open_file)
        self.ui.cbox_prev_channel.addItems(["RGB", "R", "G", "B"])
        self.ui.cbox_curv_channel.addItems(["RGB", "R", "G", "B"])
        self.ui.cbox_res.addItems(["1x", "4x", "8x", "16x"])
        self.ui.cbox_function.addItems(["调整亮度", "调整饱和度", "调整曲线"])
        
    def prepare_after_load_img(self, file_name):
        img = cv2.imread(file_name)
        self.handle_img = img
        self.update_small_img()
        self.ca = curves_adjust.Curves(self, self.handle_img, self.small_img, self.ui.label_curv,\
                                       self.ui.label_main, self.ui.label_hist, self.ui.label_prev)
        self.ui.label_curv.setCurve(self.ca, self)
        self.ca.update()
        self.ui.cbox_curv_channel.currentIndexChanged.connect(lambda: self.ca.update())
        self.ui.slider_right.valueChanged.connect(lambda: self.adjust_by_bar(self.ui.label_prev))
        self.ui.cbox_function.currentIndexChanged.connect(lambda: self.adjust_by_bar(self.ui.label_main))
        self.ui.cbox_res.currentIndexChanged.connect(self.update_small_img)
        self.ui.button_run.clicked.connect(self.run_and_save)
        self.display_image(self.ui.label_main, img)
        self.ui.actionSave.triggered.connect(self.save)
        self.ui.actionSave_As.triggered.connect(self.save_as)
        #self.display_image(self.ui.label_prev, img_small)

    def update_small_img(self):
        if self.handle_img is None:
            return
        src = self.handle_img
        times = int(self.ui.cbox_res.currentText()[:-1])
        #print(f"small img updated for:{times}")
        height, width, _ = src.shape
        self.small_img = cv2.resize(src, (width // times, height // times))
        self.display_image(self.ui.label_prev, self.small_img)
        
    def adjust_by_bar(self, label):
        if self.handle_img is None:
            self.open_file()
        if label == self.ui.label_main:
            img = self.handle_img
        else:
            img = self.small_img
            
        if self.ui.cbox_function.currentText() == "调整亮度":
            value = self.ui.slider_right.value()
            img = self.funcs.brightness_change(value, img)
            self.display_image(label, img)
            
        elif self.ui.cbox_function.currentText() == "调整饱和度":
            value = self.ui.slider_right.value()
            img = self.funcs.Saturation(img, value)
            self.display_image(label, img)
        elif self.ui.cbox_function.currentText() == "调整曲线":
            pass
        self.ca.small_src = img
        self.ca.update(True, False)
        
    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self.ui, "Open file", "", "Images (*.png *.xpm *.jpg)")
        self.last_saved_file = file_name
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

    def run_and_save(self):
        if self.handle_img is None:
            self.open_file()

        img = self.handle_img
        if self.ui.cbox_function.currentText() == "调整亮度":
            value = self.ui.slider_right.value()
            img = self.funcs.brightness_change(value, img)
        elif self.ui.cbox_function.currentText() == "调整饱和度":
            value = self.ui.slider_right.value()
            img = self.funcs.Saturation(img, value)
        elif self.ui.cbox_function.currentText() == "调整曲线":
            img = self.ca.update(is_prev = False, wanna_return = True)
        else:
            return
        self.handle_img = img
        self.ca.src = img
        self.update_small_img()
        self.display_image(self.ui.label_main, img)
        self.ui.slider_right.setValue(0)

    def save(self):
        self.run_and_save()
        print(self.last_saved_file)
        temp_name = self.last_saved_file.split("/")[-1]
        cv2.imwrite(temp_name, self.handle_img)
        
    def save_as(self):
        file_name, _ = QFileDialog.getSaveFileName(self.ui, "Save file", "", "Images (*.png *.xpm *.jpg)")
        if file_name:
            cv2.imwrite(file_name, self.handle_img)
            self.last_saved_file = file_name
            
    def update_and_adjust(self):
        self.update_small_img()
        self.adjust_by_bar(self.ui.label_prev)


if __name__ == '__main__':
    app = QApplication([])
    window = main_window()
    window.ui.showMaximized()
    app.exec()