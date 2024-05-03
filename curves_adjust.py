import curves as curves
import numpy as np
import main
import cv_funcs
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor, QPainter

class Curves(main.main_window):
    def __init__(self, src, label1, label2, label3):
        self.C = curves.Curves()
        self.src = src
        self.curves_mat = np.ones((256, 256, 3), dtype=np.uint8)
        self.label1 = label1
        self.label2 = label2
        self.label3 = label3
        
    def update(self, chan):
        self.C.draw(self.curves_mat)
        super().display_image(self.label1, self.curves_mat)
        temp_img = self.C.adjust(self.src)
        super().display_image(self.label2, temp_img)
        super().display_image(self.label3, self.__display_histogram(self.label3, chan, temp_img))
        
    def __display_histogram(self, label, chan, img) -> None: # only in Curves.update()
        hist, color = cv_funcs.calc_hist(img, chan)
        pixmap = QPixmap(label.width(), label.height())
        pixmap.fill(QColor(223, 223, 223))
        painter = QPainter(pixmap)
        painter.setPen(color)
        for i in range(256):
            height = hist[i][0] * label.height() / max(hist)[0]  # Access the value in the single-element array
            painter.drawLine(i, label.height(), i, label.height() - height)
        painter.end()
        return pixmap
               
    def chan_cho(self, s):
        if s == "R":
            self.C.channel_chose(1)
        elif s == "G":
            self.C.channel_chose(2)
        elif s == "B":
            self.C.channel_chose(3)
        else:
            self.C.channel_chose(4)
        self.update(s)
        
    def callbackMouseEvent(self, mouseEvent, pos, chan):
        if mouseEvent == "press":
            self.C.mouseDown(pos[0], pos[1])
        elif mouseEvent == "move":
            self.C.mouseMove(pos[0], pos[1])
        elif mouseEvent == "up":
            self.C.mouseUp(pos[0], pos[1])
        self.update(chan)
    
        