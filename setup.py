import setuptools

setuptools.setup(
    name="sage",
    version="0.4.0",
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
        "metrixpp",
        "cpplint",
        "flawfinder"
    ],
    entry_points={
        'console_scripts': [
            'sage=sage.__main__:main',
        ]
    }
)
