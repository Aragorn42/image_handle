import sys, os
os.chdir(os.path.dirname(__file__))
sys.path.append('../../include')
import curves as curves
import numpy as np
import MyWidget
class Curves:
    def __init__(self, main):
        self.C = curves.Curves()
        self.curves_mat = np.ones((256, 256, 3), dtype=np.uint8)
        self.main = main
        
    def update(self, is_prev=True, wanna_return = False, wanna_store = True):
        # wanna_store表示是否想把当前操作加入undo_stack
        chan = self.main.ui.cbox_curv_channel.currentText()
        pre_img = None
        pre_P = None
        temp_img = None
        self.chan_cho(chan)
        self.C.draw(self.curves_mat)
        self.main.display_image(self.main.ui.label_curv, self.curves_mat)  # 通用
        if is_prev:
            if wanna_store:
                pre_img = self.main.small_img.copy()
                pre_P = self.get_points()
            temp_img = self.C.adjust(self.main.small_img)
            self.main.display_single_channel(temp_img)
        else:
            temp_img = self.C.adjust(self.main.handle_img)
            self.main.display_image(self.main.ui.label_main, temp_img)

        self.main.display_image(self.main.ui.label_hist, self.main.funcs.display_histogram(self.main.ui.label_hist, chan, temp_img))
        if is_prev and wanna_store:   
            self.main.undo_stack.push(MyWidget.AdjustCommand(self.main, pre_img, temp_img,
                                    pre_P = pre_P, cur_P = self.get_points()))
        if wanna_return:
            return temp_img
        
    def update_curve(self, img):
        # 单独更新曲线
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
    
    def set_points(self, pointsRGB = [(0, 0), (255, 255)], pointsR = [(0, 0), (255, 255)],\
                   pointsG = [(0, 0), (255, 255)], pointsB = [(0, 0), (255, 255)]):
        self.C.set_points(pointsRGB, pointsR, pointsG, pointsB)
        #self.update()
        self.update(wanna_store=False) # 防止循环调用
        
    def callbackMouseEvent(self, mouseEvent, pos):
        if self.main.ui.cbox_function.currentText() == "调整曲线":
            if mouseEvent == "press":
                self.C.mouseDown(pos[0], pos[1])
            elif mouseEvent == "move":
                self.C.mouseMove(pos[0], pos[1])
            elif mouseEvent == "up":
                self.C.mouseUp(pos[0], pos[1])
            self.update()


    
        