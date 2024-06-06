from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QImage, QPainter, QPen
from PySide6.QtCore import Qt, QPoint

class PaintLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drawing = False
        self.last_point = QPoint()
        self.selected_tool = None  # Add this line

    def set_tool(self, tool):
        self.selected_tool = tool

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.selected_tool == "draw":
            self.drawing = True
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.drawing and self.selected_tool == "draw":
            painter = QPainter(self.pixmap())
            painter.setPen(QPen(Qt.black, 3, Qt.SolidLine))
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.selected_tool == "draw":
            self.drawing = False