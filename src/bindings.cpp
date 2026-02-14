// bindings.cpp

#include "Boid.h"
#include "Vector2D.h"
#include "simulation.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

PYBIND11_MODULE(boid_engine, m) {
    py::class_<Vector2D>(m, "Vector2D")
        .def(py::init<float, float>())
        .def_readwrite("x", &Vector2D::x)
        .def_readwrite("y", &Vector2D::y)
        .def("__add__", &Vector2D::operator+)
        .def("__sub__", &Vector2D::operator-)
        .def("__mul__", &Vector2D::operator*)
        .def("mag", &Vector2D::mag);

    // py::class_<Boid>(m, "Boid")
    //     .def(py::init<float, float>())
    //     .def_readwrite("pos", &Boid::pos)
    //     .def_readwrite("vel", &Boid::vel)
    //     .def("update", &Boid::update)
    //     .def("applyForce", &Boid::applyForce)
    //     .def("flock", &Boid::flock)
    //     .def("seek", &Boid::seek);

    py::class_<Simulation>(m, "Simulation")
        .def(py::init<int, float, float>())
        .def("step", &Simulation::step)
        .def_readwrite("boids", &Simulation::boids)
        .def("get_all_positions", [](Simulation &self) {
            std::vector<float> pos_data;
            pos_data.reserve(self.boids.size() * 2);
            for (const auto& b : self.boids) {
                pos_data.push_back(b.pos.x);
                pos_data.push_back(b.pos.y);
            }
            return pos_data;
        })
        .def("get_full_state", [](Simulation &self) {
            // Using py::ssize_t for MSVC compatibility
            auto shape = std::vector<py::ssize_t>{ (py::ssize_t)self.boids.size(), 4 };
            auto strides = std::vector<py::ssize_t>{ sizeof(Boid), sizeof(float) };

            return py::array_t<float>(
                shape, 
                strides,            
                (float*)&self.boids[0].pos.x,               
                py::cast(self)                              
            );
    });
}