#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "cvbind.hpp"
#include "Curves.hpp"


namespace py = pybind11;


PYBIND11_MODULE(curves, m) {
    py::class_<cv::Curves>(m, "Curves")
        .def(py::init<>())
        .def("draw", &cv::Curves::draw)
        .def("adjust", &cv::Curves::adjust)
        .def("mouseDown", &cv::Curves::mouseDown)
        .def("mouseMove", &cv::Curves::mouseMove)
        .def("mouseUp", &cv::Curves::mouseUp)
        .def("channel_chose", &cv::Curves::channel_chose)
        .def("get_points", &cv::Curves::get_points);
}
