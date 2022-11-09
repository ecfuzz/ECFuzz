# pre-define some constant variable for later unit test
import os
from os.path import dirname, abspath, join

ROOT_DIR = dirname(dirname(dirname(abspath(__file__))))
SRC_DIR = join(ROOT_DIR, "src")
DATA_DIR = join(ROOT_DIR, "data")
FUZZER_DIR = join(DATA_DIR, "fuzzer")
TEST_DIR = join(ROOT_DIR, "test")

CUR = os.path.dirname(os.path.realpath(__file__))
CUR_DIR = os.path.join(os.path.dirname(os.path.dirname(CUR)), "data")
APP_DIR = os.path.join(CUR_DIR, "app")
TIME_DIR = os.path.join(CUR_DIR, "execTime")

HCOMMON = "hadoop-common"
HDFS = "hadoop-hdfs"
HBASE = "hbase-server"
ZOOKEEPER = "zookeeper-server"
ALLUXIO = "alluxio-core"

CTEST_HADOOP_DIR = os.path.join(APP_DIR, "ctest-hadoop")
CTEST_HBASE_DIR = os.path.join(APP_DIR, "ctest-hbase")
CTEST_ZK_DIR = os.path.join(APP_DIR, "ctest-zookeeper")
CTEST_ALLUXIO_DIR = os.path.join(APP_DIR, "ctest-alluxio")

TESTTIMEFILE = {
    HCOMMON : os.path.join(TIME_DIR, "hadoop-common", "hadoop-common-testcase.tsv"),
    HDFS : os.path.join(TIME_DIR, "hadoop-hdfs", "hadoop-hdfs-testcase.tsv"),
    HBASE : os.path.join(TIME_DIR, "hbase-server", "hbase-server-testcase.tsv"),
    ZOOKEEPER : os.path.join(TIME_DIR, "zookeeper-server", "zookeeper-server-testcase.tsv"),
    ALLUXIO : os.path.join(TIME_DIR, "alluxio-core", "alluxio-core-testcase.tsv"),
}

PROJECT_DIR = {
    HCOMMON: CTEST_HADOOP_DIR,
    HDFS: CTEST_HADOOP_DIR,
    HBASE: CTEST_HBASE_DIR,
    ZOOKEEPER: CTEST_ZK_DIR,
    ALLUXIO: CTEST_ALLUXIO_DIR,
}

MODULE_SUBDIR = {
    HCOMMON: "hadoop-common-project/hadoop-common",
    HDFS: "hadoop-hdfs-project/hadoop-hdfs",
    HBASE: "hbase-server",
    ZOOKEEPER: "zookeeper-server",
    ALLUXIO: "core",
}

SUREFIRE_SUBDIR = "target/surefire-reports/"
SUREFIRE_XML = "TEST-{}.xml" # slot is the classname
SUREFIRE_TXT = "{}.txt" # testclass
SUREFIRE_OUTTXT = "{}-output.txt" #testclass 

SUREFIRE_DIR = {
    HCOMMON: [os.path.join(CTEST_HADOOP_DIR, MODULE_SUBDIR[HCOMMON], SUREFIRE_SUBDIR)],
    HDFS: [os.path.join(CTEST_HADOOP_DIR, MODULE_SUBDIR[HDFS], SUREFIRE_SUBDIR)],
    HBASE: [os.path.join(CTEST_HBASE_DIR, MODULE_SUBDIR[HBASE], SUREFIRE_SUBDIR)],
    ZOOKEEPER: [os.path.join(CTEST_ZK_DIR, MODULE_SUBDIR[ZOOKEEPER], SUREFIRE_SUBDIR)],
    ALLUXIO: [
        os.path.join(CTEST_ALLUXIO_DIR, MODULE_SUBDIR[ALLUXIO], "base", SUREFIRE_SUBDIR),
        os.path.join(CTEST_ALLUXIO_DIR, MODULE_SUBDIR[ALLUXIO], "client/fs", SUREFIRE_SUBDIR),
        os.path.join(CTEST_ALLUXIO_DIR, MODULE_SUBDIR[ALLUXIO], "client/hdfs", SUREFIRE_SUBDIR),
        os.path.join(CTEST_ALLUXIO_DIR, MODULE_SUBDIR[ALLUXIO], "common", SUREFIRE_SUBDIR),
        os.path.join(CTEST_ALLUXIO_DIR, MODULE_SUBDIR[ALLUXIO], "server/common", SUREFIRE_SUBDIR),
        os.path.join(CTEST_ALLUXIO_DIR, MODULE_SUBDIR[ALLUXIO], "server/proxy", SUREFIRE_SUBDIR),
        os.path.join(CTEST_ALLUXIO_DIR, MODULE_SUBDIR[ALLUXIO], "server/worker", SUREFIRE_SUBDIR),
        os.path.join(CTEST_ALLUXIO_DIR, MODULE_SUBDIR[ALLUXIO], "server/master", SUREFIRE_SUBDIR),
    ],
}

# default or deprecate conf path
DEPRECATE_CONF_DIR = os.path.join(CUR_DIR, "deprecated_configs")
DEFAULT_CONF_DIR = os.path.join(CUR_DIR, "default_configs")

DEPRECATE_CONF_FILE = {
    HCOMMON: os.path.join(DEPRECATE_CONF_DIR, "hadoop.list"),
    HDFS: os.path.join(DEPRECATE_CONF_DIR, "hadoop.list")
}

DEFAULT_CONF_FILE = {
    HCOMMON: os.path.join(DEFAULT_CONF_DIR, HCOMMON + "-default.tsv"),
    HDFS: os.path.join(DEFAULT_CONF_DIR, HDFS + "-default.tsv"),
    HBASE: os.path.join(DEFAULT_CONF_DIR, HBASE + "-default.tsv"),
    ALLUXIO: os.path.join(DEFAULT_CONF_DIR, ALLUXIO + "-default.tsv"),
    ZOOKEEPER: os.path.join(DEFAULT_CONF_DIR, ZOOKEEPER + "-default.tsv")
}

INJECTION_PATH = {
    HCOMMON: [
        os.path.join(CTEST_HADOOP_DIR, "hadoop-common-project/hadoop-common/target/classes/core-ctest.xml")
    ],
    HDFS: [
        os.path.join(CTEST_HADOOP_DIR, "hadoop-hdfs-project/hadoop-hdfs/target/classes/core-ctest.xml"),
        os.path.join(CTEST_HADOOP_DIR, "hadoop-hdfs-project/hadoop-hdfs/target/classes/hdfs-ctest.xml")
    ],
    HBASE: [
        os.path.join(CTEST_HBASE_DIR, "hbase-server/target/classes/core-ctest.xml"),
        os.path.join(CTEST_HBASE_DIR, "hbase-server/target/classes/hbase-ctest.xml")
    ],
    ZOOKEEPER: [
        os.path.join(CTEST_ZK_DIR, "zookeeper-server/ctest.cfg")
    ],
    ALLUXIO: [
        os.path.join(CTEST_ALLUXIO_DIR, "core/alluxio-ctest.properties")
    ],
}

MAPPING_PATH = os.path.join(CUR_DIR, "ctest_mapping")
MAPPING = {
    HCOMMON: os.path.join(MAPPING_PATH,"opensource-hadoop-common.json"),
    HDFS: os.path.join(MAPPING_PATH, "opensource-hadoop-hdfs.json"),
    HBASE: os.path.join(MAPPING_PATH, "opensource-hbase-server.json"),
    ZOOKEEPER: os.path.join(MAPPING_PATH, "opensource-zookeeper-server.json"),
    ALLUXIO: os.path.join(MAPPING_PATH, "opensource-alluxio-core.json"),
}
TESTING_DIR = {
    HCOMMON: os.path.join(CTEST_HADOOP_DIR, MODULE_SUBDIR[HCOMMON]),
    HDFS: os.path.join(CTEST_HADOOP_DIR, MODULE_SUBDIR[HDFS]),
    HBASE: os.path.join(CTEST_HBASE_DIR, MODULE_SUBDIR[HBASE]),
    ZOOKEEPER: os.path.join(CTEST_ZK_DIR, MODULE_SUBDIR[ZOOKEEPER]),
    ALLUXIO: os.path.join(CTEST_ALLUXIO_DIR, MODULE_SUBDIR[ALLUXIO]),
}

RUN_TEST_DIR = {
    HCOMMON: os.path.join(os.path.dirname(CUR_DIR), "src", "testValidator"),
    HDFS: os.path.join(os.path.dirname(CUR_DIR), "src", "testValidator"),
    HBASE: os.path.join(os.path.dirname(CUR_DIR), "src", "testValidator"),
    ZOOKEEPER: os.path.join(os.path.dirname(CUR_DIR), "src", "testValidator"),
    ALLUXIO: os.path.join(os.path.dirname(CUR_DIR), "src", "testValidator"),
}

TR_FILE = "test_result_{id}.tsv"
FAIL = "f" # test failed
PASS = "p" # test passed

# pre-define some constant variable for later system test
APP_SYS_DIR = os.path.join(CUR_DIR, "app_sysTest")

SYS_TEST_HDFS_DIR = os.path.join(APP_SYS_DIR, "hadoop-3.1.3-work")
SYS_TEST_HBASE_DIR = os.path.join(APP_SYS_DIR, "hbase-2.2.2-work") 

REPALCE_CONFIG_PATH = {
    HDFS: os.path.join(SYS_TEST_HDFS_DIR, "etc/hadoop"),
    HBASE: os.path.join(SYS_TEST_HBASE_DIR, "conf"),
}

REPALCE_CONFIG_NAME = {
    HDFS: "hdfs-site.xml",
    HBASE: "hbase-site.xml",
}

SYS_TEST_SHELL_PATH = {
    HDFS: os.path.join(DATA_DIR, "systest_java/hdfs/test_hdfs"),
    HBASE: os.path.join(DATA_DIR,"systest_java/hbase/test_hbase"), 
}

SYS_TEST_SHELL = {
    HDFS: "cd " + SYS_TEST_SHELL_PATH[HDFS] + "&&" + "java " + "test_hdfs_shell",
    HBASE: "cd " + SYS_TEST_SHELL_PATH[HBASE] + "&&" + "java " + "test_hbase_shell_api",
}