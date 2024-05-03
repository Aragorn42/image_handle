from PySide6.QtWidgets import QLabel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt

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
    
class MyUiLoader(QUiLoader):
    def createWidget(self, className, parent=None, name=''):
        if className == 'MyLabel':
            return MyLabel(parent)
        return super().createWidget(className, parent, name)