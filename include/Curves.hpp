#ifndef OPENCV2_PS_CURVES_HPP_
#define OPENCV2_PS_CURVES_HPP_

#include "opencv2/core.hpp"
#include "opencv2/imgproc.hpp"
#include "opencv2/highgui.hpp"
#include <iostream>

namespace cv {

class Curve {
protected:
	Scalar color;
	Scalar back_color;
	int tolerance; //鼠标按下或移动时，捕获曲线点的误差范围
	bool is_mouse_down;
	std::vector<Point>::iterator current;  //pointer to current point 当前控制点的指针

	std::vector<Point>::iterator  find(int x);
	std::vector<Point>::iterator  find(int x, int y);
	std::vector<Point>::iterator  add(int x, int y);

public:
	Curve();
	virtual ~Curve();
	std::vector<Point> points;  //control points 曲线的所有控制点
	int calcCurve(double *z); //供内部调用的方法：计算曲线

	void draw(Mat &mat);  //将曲线画在mat上
	void mouseDown(int x, int y); //当鼠标按下，请调用mouseDown()方法
	bool mouseMove(int x, int y); //当鼠标移动，请调用mouseMove()方法
	void mouseUp(int x, int y); //当鼠标抬起，请调用mouseUp()方法

	//以下方法用于：用编程方式生成曲线
	void clearPoints(); //清除曲线上所有的点
	int  addPoint(const Point &p); //增加一个点
	int  deletePoint(const Point &p); //删除一个点
	int  movePoint(const Point &p, int x, int y); //移动一个点
};

// 集合4个(R,G,B,RGB)通道的曲线
class Curves {
protected:
	void createColorTables(uchar colorTables[][256]);
public:
	Curves();
	virtual ~Curves();

	Curve RGBChannel;   //RGB总通道
	Curve RedChannel;   //Red通道
	Curve GreenChannel; //Green通道
	Curve BlueChannel;  //Blue通道

	Curve * CurrentChannel; //当前通道的指针

	void draw(Mat &mat);  //将曲线画在mat上
	void mouseDown(int x, int y); //当鼠标按下，请调用mouseDown()方法
	bool mouseMove(int x, int y); //当鼠标移动，请调用mouseMove()方法
	void mouseUp(int x, int y); //当鼠标抬起，请调用mouseUp()方法
    void channel_chose(int channel);
	std::vector<Point> get_points();  
	//实施曲线调整
	Mat adjust(Mat src);

};
} /* namespace cv */

#endif /* OPENCV2_PS_CURVES_HPP_ */