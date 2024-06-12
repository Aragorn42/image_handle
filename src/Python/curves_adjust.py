import sys, os
os.chdir(os.path.dirname(__file__))
sys.path.append('../../include')
import curves as curves
import numpy as np
import my_widget
class Curves:
    def __init__(self, main):
        self.C = curves.Curves()
        # curves库当中定义的类
        self.curves_mat = np.ones((256, 256, 3), dtype=np.uint8)
        self.main = main
        
    def update(self, is_prev=True, wanna_return = False):
        # wanna_store表示是否想把当前操作加入undo_stack
        chan = self.main.ui.cbox_curv_channel.currentText()
        wanna_store = True if chan == "RGB" else False
        # 否则会出现三个通道的曲线都一样的情况,
        # 因为AdjustCommand只能存储一个通道的曲线, 如果全部都存储可以解决, 但是没必要
        pre_img = None
        pre_P = None
        update_temp_img = None
        self.chan_cho(chan)
        self.C.draw(self.curves_mat)
        self.main.display_image(self.main.ui.label_curv, self.curves_mat)  # 通用
        if is_prev:
            if wanna_store:
                pre_img = self.main.small_img.copy()
                pre_P = self.get_points()
            update_temp_img = self.C.adjust(self.main.temp_img) 
            # 将输入的图像按照曲线进行调整
            self.main.display_single_channel(update_temp_img)
        else:
            update_temp_img = self.C.adjust(self.main.handle_img)
            self.main.display_image(self.main.ui.label_main, update_temp_img)

        self.main.display_image(self.main.ui.label_hist,\
                                self.main.funcs.display_histogram(self.main.ui.label_hist, chan, update_temp_img))
        if is_prev and wanna_store:
            self.main.undo_stack.push(my_widget.AdjustCommand(self.main, pre_img, update_temp_img,
                                    pre_P = pre_P, cur_P = self.get_points()))
        if wanna_return:
            return update_temp_img
        
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
        elif s == "RGB":
            self.C.channel_chose(4)
        else:
            print("Invalid channel")
        
    def get_points(self):
        self.chan_cho(self.main.ui.cbox_curv_channel.currentText())
        return self.C.get_points()
    # 返回当前通道的points

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


    
        