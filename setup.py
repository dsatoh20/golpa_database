# �R���p�C���p
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("scraper.pyx")
)
