## 1 Introduction

Data dir stores some necessary files.

## 2 Usage step

### 2.1 Environment Prepare


Machine is ubuntu16.04.

Use `setup_ubuntu.sh` to set up.

Use `add_project.sh` to add app for unit test.(For example, use like `./add_project.sh hadoop`).

And then download some other files.
```bash
1. Download java11 and install it.

download java11 from https://drive.google.com/file/d/1VLOb5-7onJJifxoti7WtOtOlw2Vbqp7n/view?usp=drive_link, and unzip it to /usr/lib/jvm named jdk-11.0.13.
 
2. download software files and some java scripts
download software from https://drive.google.com/file/d/1-tY4vpRpmlv2SwwvmDDVXWbq564GUR3D/view?usp=sharing, and unzip it to /data/app_sysTest.
download java scipts from https://drive.google.com/file/d/1WSnomUTKmc_Tqp9QeLlgg3wkbeTLWVYv/view?usp=sharing, and unzip it to /data/systest_java.

```

### 2.2 Fuzzing Configuraion

See `data/fuzzer.fuzzing.conf`, this file contains some fuzzer's configurations.

### 2.3 Run

Go to `../src` directory, and then use `python3 fuzzer.py`

