import sys, os
os.chdir(os.path.dirname(__file__))
sys.path.append('../../include')
import curves as curves # type: ignore
import numpy as np

class Curves:
    def __init__(self, main):
        self.C = curves.Curves()
        self.curves_mat = np.ones((256, 256, 3), dtype=np.uint8)
        self.main = main
        
    def update(self, is_prev=True, wanna_return = False):
        chan = self.main.ui.cbox_curv_channel.currentText()
        self.chan_cho(chan)
        self.C.draw(self.curves_mat)
        self.main.display_image(self.main.ui.label_curv, self.curves_mat)  # 通用
        if is_prev:
            temp_img = self.C.adjust(self.main.small_img)
            self.main.display_single_channel(temp_img)
        else:
            temp_img = self.C.adjust(self.main.handle_img)
            self.main.display_image(self.main.ui.label_main, temp_img)

        self.main.display_image(self.main.ui.label_hist, self.main.funcs.display_histogram(self.main.ui.label_hist, chan, temp_img))
        P = self.get_points()
        print(P)
        if wanna_return:
            return temp_img
        
    # only in adjust by bar
    def update_curve(self, img):
        print("update_curve")
        chan = self.main.ui.cbox_curv_channel.currentText()
        self.chan_cho(chan)
        self.C.draw(self.curves_mat)
        self.main.display_image(self.main.ui.label_curv, self.curves_mat)  # 通用
        self.main.display_image(self.main.ui.label_hist,\
                                self.main.funcs.display_histogram(self.main.ui.label_hist, chan, img))
        
    def chan_cho(self, s):
        if s == "R":
            self.C.channel_chose(1)
        elif s == "G":
            self.C.channel_chose(2)
        elif s == "B":
            self.C.channel_chose(3)
        else:
            self.C.channel_chose(4)
        
    def get_points(self):
        return self.C.get_points()
    def set_points(self, pointsRGB = [(0, 0), (255, 255)], pointsR = [(0, 0), (255, 255)], pointsG = [(0, 0), (255, 255)], pointsB = [(0, 0), (255, 255)]):
        self.C.set_points(pointsRGB, pointsR, pointsG, pointsB)
        self.update()
    def callbackMouseEvent(self, mouseEvent, pos):
        if self.main.ui.cbox_function.currentText() == "调整曲线":
            if mouseEvent == "press":
                self.C.mouseDown(pos[0], pos[1])
            elif mouseEvent == "move":
                self.C.mouseMove(pos[0], pos[1])
            elif mouseEvent == "up":
                self.C.mouseUp(pos[0], pos[1])
            self.update()


    
        