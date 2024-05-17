#include "Curves.hpp"

#define SWAP(a, b, t) \
    do {              \
        t = a;        \
        a = b;        \
        b = t;        \
    } while (0)
#define CLIP_RANGE(value, min, max) \
    ((value) > (max) ? (max) : (((value) < (min)) ? (min) : (value)))
#define COLOR_RANGE(value) CLIP_RANGE((value), 0, 255)

#define WITHIN(x1, delta, x2) ((delta) > 0) ? ((x1) <= (x2)) : ((x1) >= (x2))
#define EXCEED(x1, delta, x2) ((delta) > 0) ? ((x1) >= (x2)) : ((x1) <= (x2))
using std::vector;

namespace cv {

    static double spline(double* x, double* y, int n, double* t, int m, double* z) {
        double* dy = new double[n];
        memset(dy, 0, sizeof(double) * n);
        dy[0] = -0.5;

        double* ddy = new double[n];
        memset(ddy, 0, sizeof(double) * n);

        double h1 = 0;
        double * s = new double[n];
        double h0 = x[1] - x[0];

        s[0] = 3.0 * (y[1] - y[0]) / (2.0 * h0) - ddy[0] * h0 / 4.0;
        for (int j = 1; j <= n - 2; ++j) {
            h1 = x[j + 1] - x[j];
            double alpha = h0 / (h0 + h1);
            double beta = (1.0 - alpha) * (y[j] - y[j - 1]) / h0;
            beta = 3.0 * (beta + alpha * (y[j + 1] - y[j]) / h1);
            dy[j] = -alpha / (2.0 + (1.0 - alpha) * dy[j - 1]);
            s[j] = (beta - (1.0 - alpha) * s[j - 1]);
            s[j] = s[j] / (2.0 + (1.0 - alpha) * dy[j - 1]);
            h0 = h1;
        }
        dy[n - 1] =
            (3.0 * (y[n - 1] - y[n - 2]) / h1 + ddy[n - 1] * h1 / 2.0 - s[n - 2]) /
            (2.0 + dy[n - 2]);

        for (int j = n - 2; j >= 0; --j) {
            dy[j] = dy[j] * dy[j + 1] + s[j];
        }

        for (int j = 0; j <= n - 2; ++j) {
            s[j] = x[j + 1] - x[j];
        }

        for (int j = 0; j <= n - 2; ++j) {
            h1 = s[j] * s[j];
            ddy[j] = 6.0 * (y[j + 1] - y[j]) / h1 -
                2.0 * (2.0 * dy[j] + dy[j + 1]) / s[j];
        }

        h1 = s[n - 2] * s[n - 2];
        ddy[n - 1] = 6.0 * (y[n - 2] - y[n - 1]) / h1 +
            2.0 * (2.0 * dy[n - 1] + dy[n - 2]) / s[n - 2];
        double g = 0.0;
        for (int i = 0; i <= n - 2; i++) {
            h1 = 0.5 * s[i] * (y[i] + y[i + 1]);
            h1 = h1 - s[i] * s[i] * s[i] * (ddy[i] + ddy[i + 1]) / 24.0;
            g = g + h1;
        }

        for (int j = 0; j <= m - 1; j++) {
            int i;
            if (t[j] >= x[n - 1]) {
                i = n - 2;
            }
            else {
                i = 0;
                while (t[j] > x[i + 1]) {
                    i = i + 1;
                }
            }
            h1 = (x[i + 1] - t[j]) / s[i];
            h0 = h1 * h1;
            z[j] = (3.0 * h0 - 2.0 * h0 * h1) * y[i];
            z[j] = z[j] + s[i] * (h0 - h0 * h1) * dy[i];
            h1 = (t[j] - x[i]) / s[i];
            h0 = h1 * h1;
            z[j] = z[j] + (3.0 * h0 - 2.0 * h0 * h1) * y[i + 1];
            z[j] = z[j] - s[i] * (h0 - h0 * h1) * dy[i + 1];
        }

        delete[] s;
        delete[] dy;
        delete[] ddy;

        return (g);
    }
    // 计算样条插值, x, y为控制点坐标, n为控制点个数, t为输出点坐标, m为输出点个数, z为输出点坐标
    // 函数首先初始化一些用于计算的数组，然后计算第一个控制点的斜率。然后，它进入一个循环，对每个控制点进行处理，以生成样条曲线
    // g为样条曲线的总长度，z为输出点坐标
    // 该函数返回样条曲线的总长度

    Curve::Curve() {
        color = Scalar(180, 180, 180);
        back_color = Scalar(223, 223, 223);
        tolerance = 3;
        is_mouse_down = false;
        points.push_back(Point(0, 0));
        points.push_back(Point(255, 255));
        current = points.end();
    }
    Curve::~Curve() {}
    // 析构函数

    vector<Point>::iterator Curve::find(int x) {
        vector<Point>::iterator iter;
        for (iter = points.begin(); iter != points.end(); ++iter) {
            if (::abs(iter->x - x) <= tolerance)
                return iter;
        }
        return points.end();
    }
    vector<Point>::iterator Curve::find(int x, int y) {
        vector<Point>::iterator iter;
        for (iter = points.begin(); iter != points.end(); ++iter) {
            if (::abs(iter->x - x) <= tolerance && ::abs(iter->y - y) <= tolerance)
                return iter;
        }
        return points.end();
    }


    vector<Point>::iterator Curve::add(int x, int y) {
        vector<Point>::iterator it = find(x);
        if (it == points.end()) {
            Point p(x, y);
            vector<Point>::iterator iter;
            for (iter = points.begin(); iter != points.end(); ++iter) {
                if (iter == points.begin() && iter->x > p.x) {
                    //DEBUG_PRINT("points insert at beginning");
                    return points.insert(iter, p);
                }

                if (iter->x < x && (iter + 1) != points.end() &&
                    (iter + 1)->x > p.x) {
                    //DEBUG_PRINT("points insert");
                    return points.insert(iter + 1, p);
                }
            }
            //DEBUG_PRINT("points append");
            return points.insert(points.end(), p);
        }
        else {
            return it;
        }
    }

    int Curve::calcCurve(double* output_y) {
        // if count of control points is less than 2, return linear output
        if (points.size() < 2) {
            for (int i = 0; i < 256; ++i)
                output_y[i] = 255 - i;
            return 0;
        }

        // if count of control points is 2, return linear output
        if (points.size() == 2) {
            vector<Point>::iterator point1 = points.begin();
            vector<Point>::iterator point2 = point1 + 1;

            double delta_y = 0;
            if (point2->x != point1->x)
                delta_y = (point2->y - point1->y) * 1.0 / (point2->x - point1->x);

            // create output
            for (int i = 0; i < 256; ++i) {
                if (i < point1->x) {
                    output_y[i] = point1->y;
                }
                else if (i >= point1->x && i < point2->x) {
                    output_y[i] =
                        COLOR_RANGE(point1->y + delta_y * (i - point1->x));
                }
                else {
                    output_y[i] = point2->y;
                }
            }
            return 0;
        }

        // the count of control points is greater than 2,  create spline line

        int n = (int)points.size();  // count of points

        // create array of x-coordinate and y-coordinate of control points
        double* x = new double[n + 1];
        double* y = new double[n + 1];
        vector<Point>::iterator start_point = points.end();
        vector<Point>::iterator end_point = points.end();
        vector<Point>::iterator iter;
        int k = 0;
        for (iter = points.begin(); iter != points.end(); ++iter, ++k) {
            if (k == 0)
                start_point = iter;
            x[k] = iter->x - start_point->x;
            y[k] = iter->y;
            end_point = iter;
        }

        // if start_point or end_point is invalid
        if (start_point == points.end() || end_point == points.end() ||
            start_point == end_point) {
            for (int i = 0; i < 256; ++i)
                output_y[i] = 255 - i;
            return 1;
        }

        // create array of x-coordinate of output points
        int m = end_point->x - start_point->x;
        double* t = new double[m];  // array of x-coordinate of output points
        double* z = new double[m];  // array of y-coordinate of output points
        // initialize array of x-coordinate
        for (int i = 0; i < m; ++i) {
            t[i] = i;
        }

        // perform spline, output y-coordinate is stored in array z
        spline(x, y, n, t, m, z);

        // create output
        for (int i = 0; i < 256; ++i) {
            if (i < start_point->x) {
                output_y[i] = start_point->y;
            }
            else if (i >= start_point->x && i < end_point->x) {
                output_y[i] = CLIP_RANGE(z[i - start_point->x], 0, 255);
            }
            else {
                output_y[i] = end_point->y;
            }
        }

        return 0;
    }

    void Curve::draw(Mat& mat) {
        int thinkness = 1;
        int n = 0;
        Point lastPoint;

        // clear background
        mat.setTo(back_color);

        vector<Point>::iterator it;
        //for (it = points.begin(); it != points.end(); ++it) {
        //    cout << "point:  " << it->x << ", " << it->y << endl;
        //}
        int thickness = 1;
        int lineType = 8;
        //line(mat, p1, p2, color, thickness, lineType);
        line(mat, Point(0, 0),   Point(255, 0),   color, thickness, lineType);
        line(mat, Point(0, 255), Point(255, 255), color, thickness, lineType);
        line(mat, Point(63, 0),  Point(63, 255),  color, thickness, lineType);
        line(mat, Point(127, 0), Point(127, 255), color, thickness, lineType);
        line(mat, Point(191, 0), Point(191, 255), color, thickness, lineType);
        line(mat, Point(0, 255- 63), Point(255, 255 - 63),  color, thickness, lineType);
        line(mat, Point(0, 255-127), Point(255, 255 - 127), color, thickness, lineType);
        line(mat, Point(0, 255-191), Point(255, 255 - 191), color, thickness, lineType);
        
        // create curve
        double z[256];
        calcCurve(z);
        for (int i = 1; i < 256; ++i) {
            line(mat, Point(i - 1, 255 - int(z[i - 1])), Point(i, 255 - int(z[i])), (0, 0, 0), 1, 8);
        }
        // 画曲线, 颜色为曲线的颜色
        // 
        // draw control points
        vector<Point>::iterator iter, iter_next;
        for (iter = points.begin(); iter != points.end(); ++iter, ++n) {
            thinkness = (iter == current) ? -1 : 1;
            circle(mat, Point(iter->x, 255- iter->y), 1, (100, 100, 100), 1, 16);
        }
    }

    void Curve::mouseDown(int x, int y) {
        y = 255 - y;
        current = add(x, y);
        is_mouse_down = true;
    }

    bool Curve::mouseMove(int x, int y) {
        y = 255 - y;
        if (is_mouse_down) {
            if (current != points.end()) {
                int prev_x = 0;
                int next_x = 255;

                if (current != points.begin()) {
                    int prev_y = (current - 1)->y;
                    prev_x = (current - 1)->x;

                    // match the previous point
                    if (points.size() > 2 && ::abs(x - prev_x) <= tolerance &&
                        ::abs(y - prev_y) <= tolerance) {
                        current--;
                        current = points.erase(current);
                        //DEBUG_PRINT("erase previous");
                        return true;
                    }

                    // if x less than x of previou point
                    if (x <= prev_x) {
                        // DEBUG_PRINT("less than prev_x");
                        return true;
                    }
                }

                if ((current + 1) != points.end()) {
                    int next_y = (current + 1)->y;
                    next_x = (current + 1)->x;

                    // match the next point
                    if (points.size() > 2 && ::abs(x - next_x) <= tolerance &&
                        ::abs(y - next_y) <= tolerance) {
                        current = points.erase(current);
                        //DEBUG_PRINT("erase next");
                        return true;
                    }

                    // if x great than x of next point
                    if (x >= next_x) {
                        // DEBUG_PRINT("large than next_x");
                        return true;
                    }
                }

                current->x = CLIP_RANGE(x, 0, 255);
                current->y = CLIP_RANGE(y, 0, 255);

                return true;
            }
        }
        return false;
    }

    void Curve::mouseUp(int x, int y) {
        y = 255 - y;
        is_mouse_down = false;
    }

    void Curve::clearPoints() {
        points.clear();
    }

    int Curve::addPoint(const Point& p) {
        vector<Point>::iterator iter = add(p.x, p.y);
        if (iter != points.end())
            return 1;
        else
            return 0;
    }

    int Curve::deletePoint(const Point& p) {
        vector<Point>::iterator iter;
        iter = find(p.x, p.y);
        if (iter != points.end()) {
            if (current == iter)
                current = points.end();
            points.erase(iter);
            return 1;
        }
        return 0;
    }

    int Curve::movePoint(const Point& p, int x, int y) {
        vector<Point>::iterator iter;
        iter = find(p.x, p.y);
        if (iter != points.end()) {
            iter->x = x;
            iter->y = y;
            return 1;
        }
        return 0;
    }

    //==========================================================
    // Curves

    Curves::Curves() {
        CurrentChannel = &RGBChannel;
    }

    Curves::~Curves() {}

    void Curves::draw(Mat& mat) {
        if (CurrentChannel)
            CurrentChannel->draw(mat);
    }

    void Curves::mouseDown(int x, int y) {
        if (CurrentChannel)
            CurrentChannel->mouseDown(x, y);
    }

    bool Curves::mouseMove(int x, int y) {
        if (CurrentChannel)
            return CurrentChannel->mouseMove(x, y);
        return false;
    }

    void Curves::mouseUp(int x, int y) {
        if (CurrentChannel)
            CurrentChannel->mouseUp(x, y);
    }

    void Curves::createColorTables(uchar colorTables[][256]) {
        double z[256];

        BlueChannel.calcCurve(z);
        for (int i = 0; i < 256; ++i) {
            colorTables[0][i] = z[i];
        }

        GreenChannel.calcCurve(z);
        for (int i = 0; i < 256; ++i)
            colorTables[1][i] = z[i];

        RedChannel.calcCurve(z);
        for (int i = 0; i < 256; ++i) {
            colorTables[2][i] = z[i];
        }

        uchar value;
        RGBChannel.calcCurve(z);
        for (int i = 0; i < 256; ++i) {
            for (int c = 0; c < 3; c++) {
                value = colorTables[c][i];
                colorTables[c][i] = z[value];
            }
        }
    }

    Mat Curves::adjust(Mat src) {
        Mat input = src;
        Mat output = Mat(src.size(), src.type());

        const uchar* in;
        uchar* out;
        int width = input.cols;
        int height = input.rows;
        int channels = input.channels();

        uchar colorTables[3][256];
        createColorTables(colorTables);
        // create color tables
        
        // adjust each pixel
        for (int y = 0; y < height; y++) {
            in = input.ptr<uchar>(y);
            out = output.ptr<uchar>(y);
            for (int x = 0; x < width; x++) {
                for (int c = 0; c < 3; c++) {
                    *out++ = colorTables[c][*in++];
                }
                for (int c = 0; c < channels - 3; c++) {
                    *out++ = *in++;
                }
            }
        }
        return output;
    }
    vector<Point> Curves::get_points() {
        vector<Point> points;
        points = CurrentChannel->points;
        return points;
    }

    
    void Curves::channel_chose(int channel){
        switch(channel) {
        case 3:
            CurrentChannel = &BlueChannel;
            break;
        case 2:
            CurrentChannel = &GreenChannel;
            break;
        case 1:
            CurrentChannel = &RedChannel;
            break;
        default:
            CurrentChannel = &RGBChannel;
            break;
        }
}

} /* namespace cv */