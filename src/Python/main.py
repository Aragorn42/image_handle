import cv2
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QWidget
from PySide6.QtGui import QUndoStack,  QImage, QPixmap, QIcon
from PySide6.QtCore import Qt
import cv_funcs
import curves_adjust
import MyWidget
import numpy as np

uiLoader = MyWidget.MyUiLoader()

class MainWindow():
    handle_img = None # 主窗口中显示的图片
    small_img = None # 预览窗口显示的图片
    def __init__(self):
        self.funcs = cv_funcs.Funcs()
        self.ui = uiLoader.load("../../include/main.ui")
        self.undo_stack = QUndoStack()
        self.prepare()
        self.ui.show()
        
    def prepare(self):
        # __init__中的一些准备工作, 为了代码整洁单独提出来
        self.ui.actionNewFile.triggered.connect(self.open_file)
        # 打开文件
        self.ui.cbox_prev_channel.addItems(["RGB", "R", "G", "B"])
        # 预览窗口的通道选择
        self.ui.cbox_curv_channel.addItems(["RGB", "R", "G", "B"])
        # 曲线的通道选择
        self.ui.cbox_res.addItems(["4x", "8x", "16x"])
        # 预览的分辨率选择, 越高分辨率越低, 对性能要求越低
        self.ui.cbox_function.addItems(["调整亮度", "调整饱和度", "调整曲线"])
        # 功能选择
        self.ui.cbox_style.addItems(["无", "Cyper Punk"])
        # 风格选择
        self.ui.action_turnleft.triggered.connect(lambda: self.main_rotate_image(-90))
        self.ui.action_turnright.triggered.connect(lambda: self.main_rotate_image(90))
        # 旋转图片
        self.ui.actionUndo.triggered.connect(self.undo_stack.undo)
        self.ui.actionRedo.triggered.connect(self.undo_stack.redo)
        # 撤销和重做功能
        self.ui.action_about.triggered.connect(lambda: self.infomation("about"))
        self.ui.action_imginfo.triggered.connect(lambda: self.infomation("info"))
        # 关于和图片信息, 在子窗口里面显示
        
    def prepare_after_load_img(self, file_name):
        # 一些需要有图片之后才能进行的操作, 所以在打开图片之后调用
        img = cv2.imread(file_name)
        self.handle_img = img 
        self.update_small_img() # 更新预览窗口的图片
        self.ca = curves_adjust.Curves(self) 
        # 将当前类传进去在其中被调用, 曲线调整类
        self.ui.label_curv.setCurve(self.ca, self) 
        # MyWidget当中的函数, 把ca类传递进去调用
        self.ca.update_curve(self.handle_img)
        # 显示曲线
        self.ui.cbox_curv_channel.currentIndexChanged.connect(self.ca.update)
        # 曲线通道选择, 每次重新选择都会更新曲线
        self.ui.slider_right.valueChanged.connect(lambda: self.adjust(self.ui.label_prev))
        # 亮度和饱和度调整
        self.ui.cbox_function.currentIndexChanged.connect(lambda: self.adjust(self.ui.label_main))
        # 功能选择调整
        self.ui.cbox_res.currentIndexChanged.connect(self.update_small_img)
        # 分辨率选择
        self.ui.button_run.clicked.connect(self.run_and_save)
        # 运行并保存, 每次点击之后更新图片, 清空undo_stack, 不会更新文件
        self.ui.cbox_prev_channel.currentIndexChanged.connect(lambda: self.display_single_channel(self.small_img))
        # 预览窗口的通道选择
        self.display_image(self.ui.label_main, img)
        self.ui.actionSave.triggered.connect(self.save)
        # 保存到最后一次文件
        self.ui.actionSave_As.triggered.connect(self.save_as)
        # 保存为文件
        self.ui.cbox_style.currentIndexChanged.connect(self.change_style)
        # 每次选择风格都会更新曲线, 实际上是更新了曲线的点

    def update_small_img(self):
        # 按照选择的缩放倍率, 更新预览窗口的图片
        if self.handle_img is None:
            return
        src = self.handle_img
        times = int(self.ui.cbox_res.currentText()[:-1])
        #print(f"small img updated for:{times}")
        height, width, _ = src.shape
        self.small_img = cv2.resize(src, (width // times, height // times))
        self.display_image(self.ui.label_prev, self.small_img)
        
    def adjust(self, label):
        # 调整亮度和饱和度, 但是选项有3个, 第三个功能的调整因为绑定了鼠标动作, 所以单独处理
        # 其余两个调用cv_funcs.Funcs类中的函数
        pre_img = None
        pre_Bar = None
        if self.handle_img is None:
            self.open_file()
        if label == self.ui.label_main:
            img = self.handle_img
        else:
            img = self.small_img
            pre_img = self.small_img
            pre_Bar = self.ui.slider_right.value()
            
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

        self.ca.update_curve(img) # 使得曲线和图片同步
        if label == self.ui.label_prev:
            self.undo_stack.push(MyWidget.AdjustCommand(self, pre_img, img,\
                pre_Bar = pre_Bar, cur_Bar = self.ui.slider_right.value()))
        # 如果是预览窗口, 则加入undo_stack

    def open_file(self):
        # 打开文件, 调用prepare_after_load_img
        file_name, _ = QFileDialog.getOpenFileName(self.ui, "Open file", "", "Images (*.png *.xpm *.jpg)")
        self.last_saved_file = file_name
        if file_name:
            self.prepare_after_load_img(file_name)
    
    def display_image(self, label, img):
        # 在label上显示img, 显示之前根据label的size自动调整, 被很多地方调用
        if isinstance(img, QPixmap):
            # 如果是QPixmap, 直接显示, 这种情况在显示直方图的时候会出现
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
        # 按"确定"键的时候调用
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
        # 调整条归零
        self.undo_stack.clear()
        # 每次保存清空栈
        self.ca.set_points()
        # 所有通道曲线拉直

    def save(self):
        # 保存到最后一次文件
        self.run_and_save()
        print(self.last_saved_file)
        temp_name = self.last_saved_file.split("/")[-1]
        cv2.imwrite(temp_name, self.handle_img)
        
    def save_as(self):
        # 另存为
        file_name, _ = QFileDialog.getSaveFileName(self.ui, "Save file", "", "Images (*.png *.xpm *.jpg)")
        if file_name:
            cv2.imwrite(file_name, self.handle_img)
            self.last_saved_file = file_name
            
    def update_and_adjust(self):
        # 同时运行两个函数, 方便给slot绑定
        self.update_small_img()
        self.adjust(self.ui.label_prev)
   
    def display_single_channel(self, img):
        # 在预览窗口显示某一通道的图片
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
        
    def infomation(self, type):
        if type == "about":
            QMessageBox.about(SubWindow(), "About:", "This is a simple image processing software\nhttps://github.com/Aragorn42/image_handle")
        elif type == "info":
            QMessageBox.about(SubWindow(), "Image Infomation", \
                cv_funcs.Funcs.display_image_info(self.last_saved_file, self.handle_img))

class SubWindow(QWidget):
    def __init__(self):
        super().__init__()


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.ui.showMaximized()
    window.ui.setWindowIcon(QIcon("../../include/icon.png"))
    window.ui.setWindowTitle("Image Handle")
    app.exec()