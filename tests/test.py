import os
import sys
os.chdir(os.path.dirname(__file__))
sys.path.append('../src/Python')
import cv_funcs
import cv2

funcs = cv_funcs.Funcs()

img = cv2.imread("1709711433138.png")
for i in range(0, 99):
    img2 = funcs.brightness_change(i, img)
    cv2.imshow("img", img2)
    cv2.waitKey(100)

# @property
# def small_img(self):
#     return self.__small_img
# @small_img.setter
# def small_img(self, value):
#     current_frame = inspect.currentframe()
#     caller_frame = inspect.getouterframes(current_frame, 2)
#     print(f"small_img is being set by {caller_frame[1][3]}")
#     print("small_img updated", value.shape)
#     self.__small_img = value
# 这段函数可以检测到small_img的变化, 直接加到当中
    