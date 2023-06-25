#!/bin/bash

# set up env for Linux ubuntu
sudo apt-get install openjdk-8-jdk
sudo apt-get install maven
sudo apt-get install build-essential autoconf automake libtool cmake zlib1g-dev pkg-config libssl-dev

# install python3.9
wget https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tgz
tar -xvf Python-3.9.0.tgz
cd Python-3.9.0
./configure --enable-optimizations
make -j $(nproc)
sudo make altinstall
python3 --version

# install python requirement
pip3 install psutil
pip3 install pymongo
pip3 install reprint

# install protobuf 2.5
curdir=$PWD
cd /usr/local/src/
wget https://github.com/google/protobuf/releases/download/v2.5.0/protobuf-2.5.0.tar.gz
tar xvf protobuf-2.5.0.tar.gz
cd protobuf-2.5.0
./autogen.sh
./configure --prefix=/usr
make
make install
protoc --version

cd $curdir
