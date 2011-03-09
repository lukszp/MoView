import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "moView",
    version = "0.0.1",
    packages = find_packages(),
    entry_points = {
        'console_scripts': ['moview=moview.moview:main'],
        },
    install_requires=[
        'jinja2',
        'xmlrpclib',
        'argparse',
        'IMDbPY>4.0',
        ],
    author = "Lukasz Szpak",
    author_email = "lukasz.j.szpak@gmail.com",
    description = ("MoView allows you to obtain most important movie data from "
                   " imdb.com and choose what's worth watching tonight."),
    license = "GPL",
    keywords = "media film movie utility",
    url = "https://github.com/lukszp/MoView",
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    include_package_data=True,
)
