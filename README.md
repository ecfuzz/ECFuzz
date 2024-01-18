# ECFuzz: Effective Configuration Fuzzing for Large-Scale Systems

## Introduction

An effective configuration fuzzer for large-scale systems.
46th International Conference on Software Engineering (ICSE 2024) 

## Runtime Preview

<img src="_preview/running-alluxio.png" alt="image-20221109195021554" style="zoom:67%;" />

## Experiment Data Link
[Experiment Data](https://docs.google.com/spreadsheets/d/1dJ7qdBNry2ljwq6jxRf4Ee-vH1ESG4Un/edit?usp=share_link&ouid=106562655925167731023&rtpof=true&sd=true)

[Exption Crash Files](https://drive.google.com/drive/folders/1d_M6RPpgkSwFKjeCSDBG-6SzYIAEUCVp?usp=sharing)

## Usage 

Please see `data/README.md`. **Some files related to java scripts are also in `data/README.md`**.

You can also use docker image from docker hub like below
```shell
sudo docker pull ecfuzz/ecfuzz:1.2
sudo docker run -it --privileged --name icse-ecfuzz ecfuzz/ecfuzz:1.0 /bin/bash
# and then enter the docker container, and run the fuzzer
cd ecfuzz/src
python3 fuzzer.py
```
