#!/usr/bin/python
import os

os.system("pip install metrixpp")
os.system("pip install flawfinder")

if os.path.exists("Duplo"):
    print("Duplo Directory alredy exists")
    exit(1)

os.system("git clone https://github.com/dlidstrom/Duplo.git -b v0.6.1 -c advice.detachedHead=false")
patch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Duplo_patch/duplo_stdc++17_revert.patch")
os.system("cd Duplo && git apply %s && mkdir build && cd build && cmake .. && make" % (str(patch_path)))

print("Typing below command.\nPATH=${PWD}/Duplo/build:${PATH}")
