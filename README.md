# 项目说明
本项目基于Python3.11.5, 使用[PySlide6](https://doc.qt.io/qtforpython-6/)框架编前端, [OpenCV](https://opencv.org/)作为主要算法库, 复杂的代码使用C++(11+)编写, 并使用[Pybind11](https://pybind11.readthedocs.io)将接口暴露给Python, 以提高运行效率. 其中使用[这个](https://github.com/open-dynamic-robot-initiative/pybind11_opencv.git)仓库让Python当中可以自由地在C++当中传递参数.

# 运行步骤
windows下运行以下命令:
```powershell
pip install -r requirements.txt
mkdir include
cd include
git clone https://github.com/pybind/pybind11.git
cd ..
python src/python/main.py
```

