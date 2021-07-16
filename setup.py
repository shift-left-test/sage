import os
import setuptools
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "sage")))
from _version import __version__ 

setuptools.setup(
    name="sage",
    version=__version__,
    license="MIT",
    author="sunggon.kim",
    author_email="sunggon82.kim@lge.com",
    description="Defines a common interface for static code analyzers to provide usability and scalability",
    long_description=open('README.md').read(),
    url="",
    packages=setuptools.find_packages(exclude=['tests']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        "compiledb",
        "texttable",
    ],
    entry_points={
        'console_scripts': [
            'sage=sage.__main__:main',
        ]
    }
)
