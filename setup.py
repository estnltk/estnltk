import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "estnltk",
    version = "1.0",
    author = "Timo Petmanson, Aleksandr Tkachenko, Siim Orasmaa, Raul Sirel, Karl-Oskar Masing, Tanel Pärnamaa, Dage Särg, Sven Laur, Tarmo Vainoi, Heiki-Jaan Kaalep",
    author_email = "tpetmanson@gmail.com",
    description = ("API for performing natural language processing tasks in Estonian."),
    license = "BSD",
    keywords = "example documentation tutorial",
    url = "http://packages.python.org/an_example_pypi_project",
    packages=['an_example_pypi_project', 'tests'],
    long_description=read('README'),
    classifiers=[],
)
