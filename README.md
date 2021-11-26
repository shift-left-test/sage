# SAGE

> Static Analysis Group Executor


## About

This program runs a series of static analysis tools to collect and visualize the various software metric information.


## Requirements

To install required packages

```bash
$ apt-get install build-essential cmake wget python3 python3-pip libpcre3-dev unzip
```

To install clang-tidy
```bash
$ apt-get install clang clang-tidy
```

To install Duplo
```bash
$ mkdir Duplo && \
      cd Duplo && \
      wget https://github.com/dlidstrom/Duplo/releases/download/v0.6.1/duplo-linux.zip && \
      unzip duplo-linux.zip && \
      cp duplo /usr/bin/
```

To install cppcheck
```bash
$ mkdir cppcheck && \
      cd cppcheck && \
      wget https://github.com/danmar/cppcheck/archive/2.1.tar.gz && \
      tar xvf 2.1.tar.gz && \
      cmake cppcheck-2.1/ -DUSE_MATCHCOMPILER=ON -DHAVE_RULES=ON && \
      make -j && \
      make install
```

To install cpplint
```bash
pip3 install cpplint
```

To install tox (optional for runnting tests)
```bash
pip3 install tox
```


## How to run tests

```bash
tox
```


## How to install

```bash
pip3 install .
```


## Licenses

The project source code is available under MIT license. See [LICENSE](LICENSE).
