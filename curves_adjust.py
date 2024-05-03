import curves as curves
import numpy as np
import cv_funcs
from PySide6.QtGui import QPixmap, QColor, QPainter


class Curves:
    def __init__(self, mainwindow, src, label1, label2, label3):
        self.C = curves.Curves()
        self.src = src
        self.curves_mat = np.ones((256, 256, 3), dtype=np.uint8)
        self.label1 = label1 # label1 is the label for curves
        self.label2 = label2 # label2 is the label for the image
        self.label3 = label3 # label3 is the label for the histogram
        self.mainwindow = mainwindow
        
    def update(self):
        chan = self.mainwindow.ui.cbox_curv_channel.currentText()
        self.chan_cho(chan)
        self.C.draw(self.curves_mat)
        self.mainwindow.display_image(self.label1, self.curves_mat)
        temp_img = self.C.adjust(self.src)# 区别之处
        self.mainwindow.display_image(self.label2, temp_img)
        self.mainwindow.display_image(self.label3, cv_funcs.display_histogram(self.label3, chan, temp_img))

    def chan_cho(self, s):
        if s == "R":
            self.C.channel_chose(1)
        elif s == "G":
            self.C.channel_chose(2)
        elif s == "B":
            self.C.channel_chose(3)
        else:
            self.C.channel_chose(4)
        
    def callbackMouseEvent(self, mouseEvent, pos):
        if mouseEvent == "press":
            self.C.mouseDown(pos[0], pos[1])
        elif mouseEvent == "move":
            self.C.mouseMove(pos[0], pos[1])
        elif mouseEvent == "up":
            self.C.mouseUp(pos[0], pos[1])
        self.update()


    
        