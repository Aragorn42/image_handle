from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt
from PySide6.QtGui import QUndoCommand


class MyLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def setCurve(self, curves, main):
        self.main = main
        self.curves = curves
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.curves.callbackMouseEvent("press", self.mapTo255(event.position()))
            
    def mouseMoveEvent(self, event):
        x, y = self.mapTo255(event.position())
        x, y = min(255, y), min(255, y)
        x, y = max(0, x), max(0, y) # 防止鼠标移出去
        self.curves.callbackMouseEvent("move", self.mapTo255(event.position()))
        
    def mouseReleaseEvent(self, event) -> None:
        self.curves.callbackMouseEvent("up", self.mapTo255(event.position()))
        
    def mapTo255(self, pos):
        label_size = self.size()
        x = int(pos.x() / label_size.width() * 255)
        y = int(pos.y() / label_size.height() * 255)
        return x, y


class AdjustCommand(QUndoCommand):
    def __init__(self, main, previous_img, current_img, \
        pre_P=None, cur_P=None, pre_Bar = None, cur_Bar = None):
        super().__init__()
        self.main = main
        self.previous_img = previous_img
        self.current_img = current_img
        self.pre_P = pre_P
        self.cur_P = cur_P
        self.pre_Bar = pre_Bar
        self.cur_Bar = cur_Bar

    def undo(self):
        self.main.small_img = self.previous_img
        self.main.display_image(self.main.ui.label_prev, self.previous_img)
        self.main.ca.update_curve(self.previous_img)
        if self.pre_P:
            self.main.ca.set_points(self.pre_P)
        if self.pre_Bar:
            self.main.ui.slider_right.setValue(self.pre_Bar)
            
    def redo(self):
        self.main.small_img = self.current_img
        self.main.display_image(self.main.ui.label_prev, self.current_img)
        self.main.ca.update_curve(self.current_img)
        if self.cur_P:
            self.main.ca.set_points(self.cur_P)
        if self.cur_Bar:
            self.main.ui.slider_right.setValue(self.cur_Bar)
    # 每次undo之后, 如果栈没有加入新的元素, 则可以redo, 否则不行
  
      
class MyUiLoader(QUiLoader):
    def createWidget(self, className, parent=None, name=''):
        if className == 'MyLabel':
            return MyLabel(parent)
        return super().createWidget(className, parent, name)
     
     
class SubWindow(QWidget):
    def __init__(self):
        super().__init__()
