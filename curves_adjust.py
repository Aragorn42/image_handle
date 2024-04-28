import curves
import numpy as np
import main
import cv2
from PySide6.QtCore import Qt

class Curves(main.main_window):
    def __init__(self, src, label1, label2): #src ndarray
        self.C = curves.Curves()
        self.src = src
        self.curves_mat = np.ones((256, 256, 3), dtype=np.uint8)
        self.label1 = label1
        self.label2 = label2
        
    def update(self): #cv::U8C3, cv::U8C3, curve_win, main_win
        self.C.draw(self.curves_mat)
        super().display_image(self.label1, self.curves_mat)
        super().display_image(self.label2, self.C.adjust(self.src))
        
    def chan_cho(self, s):
        print(s)
        if s == "R":
            self.C.channel_chose(1)
        elif s == "G":
            self.C.channel_chose(2)
        elif s == "B":
            self.C.channel_chose(3)
        else:
            self.C.channel_chose(4)
        print("chose success")
        self.update()
        
    def callbackMouseEvent(self, mouseEvent, pos):
        if mouseEvent == "press":
            self.C.mouseDown(pos[0], pos[1])
            self.update()
        elif mouseEvent == "move":
            self.C.mouseMove(pos[0], pos[1])
            self.update()
        elif mouseEvent == "up":
            self.C.mouseUp(pos[0], pos[1])
            self.update()
    
        