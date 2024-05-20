#include <cstdio>
#include <iostream>
#include "opencv2/core.hpp"
#include "opencv2/imgproc.hpp"
#include "opencv2/highgui.hpp"
#include "Curves.hpp"
#include <opencv2/highgui/highgui_c.h>

using namespace std;
using namespace cv;

static string window_name = "Photo";
static Mat src;

static string curves_window = "Adjust Curves";
static Mat curves_mat;
static int channel = 0;
Curves  curves;

static void invalidate() // curves_mat, src
{
	curves.draw(curves_mat);
	imshow(curves_window, curves_mat);
	imshow(window_name, curves.adjust(src));
}

static void callbackAdjustChannel(int , void *)
{
	switch (channel) {
	case 3:
		curves.CurrentChannel = &curves.BlueChannel;
		break;
	case 2:
		curves.CurrentChannel = &curves.GreenChannel;
		break;
	case 1:
		curves.CurrentChannel = &curves.RedChannel;
		break;
	default:
		curves.CurrentChannel = &curves.RGBChannel;
		break;
	}

	invalidate();
}

static void callbackMouseEvent(int mouseEvent, int x, int y, int flags, void* param)
{
	switch(mouseEvent) {
	case CV_EVENT_LBUTTONDOWN:
		curves.mouseDown(x, y);
		invalidate();
		break;
	case CV_EVENT_MOUSEMOVE:
		if ( curves.mouseMove(x, y) )
			invalidate();
		break;
	case CV_EVENT_LBUTTONUP:
		curves.mouseUp(x, y);
		invalidate();
		break;
	}
	return;
}


int main()
{
	//read image file
	//std::cout << "hello" << std::endl;
	src = imread("D://Code//Code_Cpp//opencv//cv_cpp//Manda.png");
	if ( !src.data ) {
		cout << "error read image" << endl;
		return -1;
	}
		
	//create window
	namedWindow(window_name);
	imshow(window_name, src);

	//create Mat for curves
	curves_mat = Mat::ones(256, 256, CV_8UC3);
	// 初始化为空
	curves.get_points();
	//create window for curves
	namedWindow(curves_window);
	setMouseCallback(curves_window, callbackMouseEvent, NULL);
	createTrackbar("Channel", curves_window, &channel,  3, callbackAdjustChannel);
	
	std::vector<Point> P;
	P = curves.get_points();
	std::cout << "points size: " << P.size() << std::endl;
	curves.set_points(P, P, P, P);

	invalidate();


	waitKey();

	return 0;

}
