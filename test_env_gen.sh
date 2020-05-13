#!/bin/bash -eE

mkdir -p tmp
cd tmp

if [ ! -d "$1" ]; then
    git clone http://mod.lge.com/hub/yocto/sample/$1.git
    cd $1
else
    cd $1
    git pull
fi

mkdir -p build && cd build
cmake ..
cd ../..