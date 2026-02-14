from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext
import os

# Determine compiler flags based on OS
extra_compile_args = ['/openmp'] if os.name == 'nt' else ['-fopenmp']
extra_link_args = ['/openmp'] if os.name == 'nt' else ['-fopenmp']

# Define the extension module
ext_modules = [
    Pybind11Extension(
        "boid_engine",
        ["src/bindings.cpp"],
        include_dirs=["src/engine"],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        cxx_std=11
    ),
]

setup(
    name="boid_engine",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)