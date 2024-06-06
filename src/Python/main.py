import cv2
from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
import cv_funcs
import curves_adjust
import MyWidget
import numpy as np

uiLoader = MyWidget.MyUiLoader()

class main_window:
    handle_img = None # 主窗口中显示的图片
    small_img = None # 预览窗口显示的图片
    def __init__(self):
        self.funcs = cv_funcs.Funcs()
        self.ui = uiLoader.load("../../include/main.ui")
        self.prepare()
        self.ui.show()
         
    def prepare(self):
        self.ui.actionNewFile.triggered.connect(self.open_file)
        self.ui.cbox_prev_channel.addItems(["RGB", "R", "G", "B"])
        self.ui.cbox_curv_channel.addItems(["RGB", "R", "G", "B"])
        self.ui.cbox_res.addItems(["4x", "8x", "16x"])
        self.ui.cbox_function.addItems(["调整亮度", "调整饱和度", "调整曲线", "draw"])
        self.ui.cbox_style.addItems(["无", "Cyper Punk"])
        self.ui.action_turnleft.triggered.connect(lambda: self.main_rotate_image(-90))
        self.ui.action_turnright.triggered.connect(lambda: self.main_rotate_image(90))
        
    def prepare_after_load_img(self, file_name):
        img = cv2.imread(file_name)
        self.handle_img = img
        self.update_small_img()
        self.ca = curves_adjust.Curves(self) # 将当前类传进去在其中被调用
        self.ui.label_curv.setCurve(self.ca, self) # MyWidget当中的函数
        # 将各种信号连接到槽函数
        self.ca.update()
        self.ui.cbox_curv_channel.currentIndexChanged.connect(self.ca.update)
        self.ui.slider_right.valueChanged.connect(lambda: self.adjust(self.ui.label_prev))
        self.ui.cbox_function.currentIndexChanged.connect(lambda: self.adjust(self.ui.label_main))
        self.ui.cbox_res.currentIndexChanged.connect(self.update_small_img)
        self.ui.button_run.clicked.connect(self.run_and_save)
        self.ui.cbox_prev_channel.currentIndexChanged.connect(lambda: self.display_single_channel(self.small_img))
        self.display_image(self.ui.label_main, img)
        self.ui.actionSave.triggered.connect(self.save)
        self.ui.actionSave_As.triggered.connect(self.save_as)
        self.ui.cbox_style.currentIndexChanged.connect(self.change_style)
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
        
    def adjust(self, label):
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
        self.ca.update_curve(img)
        
    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self.ui, "Open file", "", "Images (*.png *.xpm *.jpg)")
        self.last_saved_file = file_name
        if file_name:
            self.prepare_after_load_img(file_name)
    
    def display_image(self, label, img):
        if isinstance(img, QPixmap):
            label.setPixmap(img)
            return
        height, width, _ = img.shape
        bytesPerLine = 3 * width
        qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(qImg)
        pixmap = pixmap.scaled(label.width(), label.height(),\
                                Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pixmap)

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
        self.update_small_img()
        self.display_image(self.ui.label_main, img)
        self.ui.slider_right.setValue(0)
        self.ca.set_points()

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
        self.adjust(self.ui.label_prev)
   
    def display_single_channel(self, img):
        temp_color = self.ui.cbox_prev_channel.currentText()
        temp_img = np.zeros_like(img)
        if temp_color == "RGB":
            self.display_image(self.ui.label_prev, img)
        elif temp_color == "B":
            temp_img[:, :, 0] = img[:, :, 0]
            self.display_image(self.ui.label_prev, temp_img)
        elif temp_color == "G":
            temp_img[:, :, 1] = img[:, :, 1]
            self.display_image(self.ui.label_prev, temp_img)
        elif temp_color == "R":
            temp_img[:, :, 2] = img[:, :, 2]
            self.display_image(self.ui.label_prev, temp_img)
        else:
            print("Error: display_single_channel")
        
    def change_style(self):
        if self.ui.cbox_style.currentText() == "Cyper Punk": # 需要在前面同步更改
            self.ca.set_points([(0, 0), (46, 73), (53, 54), (76, 142), (121, 149), (204, 129), (255, 255)])
        else:
            self.ca.set_points()
            
    def main_rotate_image(self, rotation):
        if rotation == 90:
            self.handle_img = cv_funcs.Funcs.rotate_image(self.handle_img, 90)
            self.small_img = cv_funcs.Funcs.rotate_image(self.small_img, 90)
        elif rotation == -90:
            self.handle_img = cv_funcs.Funcs.rotate_image(self.handle_img, -90)
            self.small_img = cv_funcs.Funcs.rotate_image(self.small_img, -90)
        else:
            print("Error: turn angle is not 90 or -90")
        self.display_image(self.ui.label_main, self.handle_img)
        self.display_image(self.ui.label_prev, self.small_img)
        
if __name__ == '__main__':
    app = QApplication([])
    window = main_window()
    window.ui.showMaximized()
    app.exec()