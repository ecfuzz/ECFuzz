
# 1. Setup

## 1.1 Hardware

A CPU server with at least 4-core 4G memory.

## 1.2 Software

We provide a public docker image in docker hub. All software environments are installed in this docker image. The operating system is 64-bit Ubuntu 16.04 LTS.

# 2. Usage

## 2.1 Basic Usage

1. Download the docker image from docker hub.

```shell
# download docker image form docker hub
sudo docker pull ecfuzz/ecfuzz:1.2
sudo docker run -it --privileged --name icse-ecfuzz ecfuzz/ecfuzz:1.2 /bin/bash
```

2. Enter the docker container, prepare for the initial operations before testing.

```shell
# password is kb310
hadoop@a077d82fbc93:~$ bash prepare.sh
```

P.S. Explanation of some instructions in `prepare.sh`:

- The line `/usr/lib/jvm/jdk-11.0.13/bin/java test_hbase_shell_api` occurs twice in the instructions. Because sometimes the large-scale system HBase is unstable at first, so we execute this command twice to ensure that it runs stably before starting the experiment.
- The command `/usr/lib/jvm/jdk-11.0.13/bin/java test_hbase_shell_api` has the operation to terminate the server. When the fuzzer starts running, the server is closed and does not need to be opened in advance.

3. Modify the configuration file of fuzzing (i.e., `fuzzing.conf`), and run our fuzzer named ECFuzz. (If the operation is successful, a display board similar to `AFL` will appear on the terminal)

```shell
hadoop@a077d82fbc93:~$ cd ~/ecfuzz/data/fuzzer/
hadoop@a077d82fbc93:~/ecfuzz/data/fuzzer$ cat fuzzing.conf
# here we can do nothing for config, and run the fuzzer.
hadoop@a077d82fbc93:~$ cd ~/ecfuzz/src/
hadoop@a077d82fbc93:~/ecfuzz/src$ python3 fuzzer.py
```

## 2.2 Reproduction

All of our experimental results were obtained by modifying the configuration file (i.e., `fuzzing.conf`) and running fuzzer repeatedly. Therefore, we introduce the important configuration file (`/home/hadoop/ecfuzz/data/fuzzer/fuzzing.conf`) of our fuzzer below:

 ```shell
# The mutator decides to use ceit or ecfuzz, typical options: (testcaseGenerator.CeitMutator.CeitMutator/testcaseGenerator.SmartMutator.SmartMutator)
mutator
# fuzzer's runtime
run_time 
# whether to skip unit tests
skip_unit_test
# our PUT (program under test)
project 
# choose which seed generation method to use for ceit tools. This config can persist without affecting the operation of ecfuzz
misconf_mode 
 ```

Here we give all the configs for running different fuzzers. Due to the excessive number of configuration parameters, for simplicity, we only provide the configurations that need to be modified. Other parameters in the configuration file do not need to be changed.

`ECFuzz-S`

```shell
mutator=testcaseGenerator.SingleMutator.SingleMutator
run_time=12
skip_unit_test=False
```

`ECFuzz-W`

```shell
mutator=testcaseGenerator.SmartMutator.SmartMutator
run_time=12
skip_unit_test=True
```

`ECFuzz`

```shell
mutator=testcaseGenerator.SmartMutator.SmartMutator
run_time=12
skip_unit_test=False
```

`ConfTest`

```shell
mutator=testcaseGenerator.CeitMutator.CeitMutator
run_time=12
skip_unit_test=True
misconf_mode=ConfTest 
```

`ConfErr`

```shell
mutator=testcaseGenerator.CeitMutator.CeitMutator
run_time=12
skip_unit_test=True
misconf_mode=ConfErr 
```

`ConfDiagDetector`

```shell
mutator=testcaseGenerator.CeitMutator.CeitMutator
run_time=12
skip_unit_test=True
misconf_mode=ConfDiagDetector 
```

And finally, modify the `project` based on requirements. Our artifact supports five large-scale systems: `HCommon`, `HDFS`, `HBase`, `ZooKeeper` and `Alluxio`.

```shell
project=hadoop-hdfs
# hadoop-common;hadoop-hdfs;hbase;zookeeper;alluxio
```

For example, if we want to run `ConfTest` to fuzz HDFS, the configuration file is as follows:

```shell
[fuzzer]
fuzzing_loop=-1
testcase_per_seed=2
seed_pool_selection_ratio=0.5
seed_gen_seq_ratio=0.5
mutator=testcaseGenerator.CeitMutator.CeitMutator
# mutator=testcaseGenerator.SmartMutator.SmartMutator
systemtester=testValidator.SystemTester.SystemTester
trimmer=testValidator.DichotomyTrimmer.DichotomyTrimmer

data_viewer=False
data_viewer_server_address=192.168.1.52
data_viewer_server_port=8097
data_viewer_env=HBASE-mixPool-copy
plot_data_path=data/fuzzer/plot_data.txt

mongodb=False
run_time=12

unit_test_results_dir=data/fuzzer/ut_results
unit_testcase_dir=data/fuzzer/ut_testcases
sys_test_results_dir=data/fuzzer/st_results
seeds_dir=data/fuzzer/seeds
sys_testcase_fail_dir=data/fuzzer/st_fail_testcases
sys_testcase_fail1_dir=data/fuzzer/st_fail_testcases/st_fail1
sys_testcase_fail2_dir=data/fuzzer/st_fail_testcases/st_fail2
sys_testcase_fail3_dir=data/fuzzer/st_fail_testcases/st_fail3
sys_testcase_other_dir=data/fuzzer/st_fail_testcases/st_other_fail

ctests_trim_sampling=5
ctests_trim_scale=1
ctest_total_time=15
use_surefire=False
use_mutil_pro=False
use_pre_kill=True

skip_unit_test=True
force_system_testing_ratio=0.1

project=hadoop-hdfs
# hadoop-common;hadoop-hdfs;hbase;zookeeper;alluxio
misconf_mode=ConfTest 
test_str_list=[lisy,is,handsome]

[hadoop-hdfs]
file_path = data/fuzzer/hadoop-hdfs.conf

[hadoop-common]
file_path = data/fuzzer/hadoop-common.conf

[hbase]
file_path = data/fuzzer/hbase.conf

[zookeeper]
file_path = data/fuzzer/zookeeper.conf

[alluxio]
file_path = data/fuzzer/alluxio.conf

```

## 2.3 Data Details In Our Paper 

An example of the display board on the terminal:

```
effective configuration fuzzing (hadoop-hdfs)                                         
-------------------------------Time-------------------------------- 
run time: 0  days, 0  hrs, 39 min, 36 sec                                        
last new fail unit test: 0  days, 0  hrs, 0  min, 0  sec                                      
last new fail system test: 0  days, 0  hrs, 3  min, 10 sec                                       
longest system test time: 0  days, 0  hrs, 0  min, 50 sec                                         
average unit test time: 0  days, 0  hrs, 0  min, 0  sec                                       
average system test time: 0  days, 0  hrs, 0  min, 39 sec                              
-----------------------------Mutation------------------------------                                                                 
mutation strategy: CeitMutator                                                                  
now mutation type: ConfTest:NUM[INT,,,]                                                    
now test configuration: dfs.cachereport.intervalMsec                                            
total unit test cases: 0                                                                    
total run unit test count: 0                                                                      
total system test cases: 60                                                                       
unit test cmd timeout: 0sec                                                                      
unit test exec speed: 0.0/sec                                                                 
system test exec speed: 0.025500858553621372/sec                                                     
ecFuzz exec speed: 0.025493158404965646/sec                                     
-------------------------Overall results---------------------------                                              
fuzzing progress: 30:60(system testing)                                                             
queue length: 0                                                                     
total system test failed: 27 (26, 1, 0)                                                
------------------------------End----------------------------------    
```

- The mutation strategy list includes two cases: CeitMutator and SmartMutator.

  - The CeitMutator stands for using the baseline method, that is, CEIT (Configuration Error Injection Testing). Among them, CEIT includes three tools, ConfTest, ConfErr and ConfDiagDetector. We can obtain the information from the now mutation type list (i.e., `now mutation type: ConfTest:NUM[INT,,,]` in the display board). The CEIT tools do not use unit testing, so no unit testing results in the display board.

  - The SmartMutator stands for using the method proposed in this work, namely ECFuzz. ECFuzz introduces unit testing into configuration testing techniques to filter out configuration parameters that are unlikely to yield errors before executing system testing, and effectively validate generated configuration parameters. If we want to use ECFuzz for testing, we only need to modify the corresponding parameters in the configuration file (`/home/hadoop/ecfuzz/data/fuzzer/fuzzing.conf`), as shown below:

    ```shell
    mutator=testcaseGenerator.SmartMutator.SmartMutator
    skip_unit_test=False
    ```

Table 5 data: We can get this data from the display board on the terminal.

```bash
# "Testcases" in Table 5 is the number of "total system test cases" on the display board.
Testcases : [total system test cases]
# "Exceptions" in Table 5 is the sum of "total system test failed" on the display board.
Startup Exception, Runtime Exception, Shutdown Exception : [total system test failed: N (X,Y,Z) ]
```

Figure 4 and Table 4 data: We can get this data from the log (`/home/hadoop/ecfuzz/data/fuzzer/fuzzer.log`).

```bash
# find information similar to "exception map reason is :{} " at the end of the log, and the keys of the map are the result of exceptions infomation.
```

Table 6 data: After manually analyzing all the results, we can match them with the issue id.

## 2.4 Other Instructions

We currently support 5 large-scale systems, including: HCommon, HDFS, HBase, ZooKeeper and Alluxio. To test them, we only need to modify the corresponding parameters in `fuzzing.conf` (`/home/hadoop/ecfuzz/data/fuzzer/fuzzing.conf`) according to the instructions in the Section 2.2. If we need to additionally support other large-scale systems, first we need to provide corresponding unit test cases, and then write corresponding test scripts for system startup and shutdown.
