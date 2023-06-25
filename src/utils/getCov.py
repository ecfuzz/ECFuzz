import os, shutil, stat
import subprocess
from utils.getCovNum import getCovNum
from utils.Logger import getLogger

class getCov(object):
    def __init__(self) -> None:
        self.getCovNum = getCovNum()
        self.logger = getLogger()

    def get_cov_unit_hcommon(self) -> list:
        # return list of cov [branch, path, line]
        unit_path = ["/home/hadoop/ecfuzz/data/app/ctest-hadoop/hadoop-common-project/hadoop-common/target/jacoco.exec"]
        classfiles = ["/home/hadoop/ecfuzz/data/app/ctest-hadoop/hadoop-common-project/hadoop-common/target/hadoop-common-2.8.5.jar"]
        outdir = "/home/hadoop/jacoco-0.8.7/cov-unit-hcommon"
        ans = self.get_cov_unit(unit_path, classfiles, outdir)
        return ans

    def get_cov_unit_hdfs(self) -> list:
        # return list of cov [branch, path, line]
        unit_path = ["/home/hadoop/ecfuzz/data/app/ctest-hadoop/hadoop-hdfs-project/hadoop-hdfs/target/jacoco.exec"]
        classfiles = ["/home/hadoop/ecfuzz/data/app/ctest-hadoop/hadoop-hdfs-project/hadoop-hdfs/target/hadoop-hdfs-2.8.5.jar"]
        outdir = "/home/hadoop/jacoco-0.8.7/cov-unit-hdfs"
        ans = self.get_cov_unit(unit_path, classfiles, outdir)
        return ans

    def get_cov_unit_hbase(self) -> list:
        # return list of cov [branch, path, line]
        unit_path = ["/home/hadoop/ecfuzz/data/app/ctest-hbase/hbase-server/target/jacoco.exec"]
        classfiles = ["/home/hadoop/ecfuzz/data/app/ctest-hbase/hbase-server/target/hbase-server-2.2.2.jar"]
        outdir = "/home/hadoop/jacoco-0.8.7/cov-unit-hdfs"
        ans = self.get_cov_unit(unit_path, classfiles, outdir)
        return ans

    def get_cov_unit_alluxio(self) -> list:
        # return list of cov [branch, path, line]
        unit_path = ["/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/base/target/jacoco.exec",
                        "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/client/fs/target/jacoco.exec",
                        "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/client/hdfs/target/jacoco.exec",
                        "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/common/target/jacoco.exec",
                        "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/server/common/target/jacoco.exec",
                        "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/server/master/target/jacoco.exec",
                        "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/server/proxy/target/jacoco.exec",
                        "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/server/worker/target/jacoco.exec",
                        "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/transport/target/jacoco.exec"
                        ]
        classfiles = ["/home/hadoop/ecfuzz/data/app_sysTest/alluxio-2.1.0-work/assembly/alluxio-client-2.1.0.jar",
                        "/home/hadoop/alluxio-server-2.1.0.jar"]
        outdir = "/home/hadoop/jacoco-0.8.7/cov-unit-alluxio"
        ans = self.get_cov_unit(unit_path, classfiles, outdir)
        return ans

    def get_cov_unit_zookeeper(self) -> list:
        # return list of cov [branch, path, line]
        unit_path = ["/home/hadoop/ecfuzz/data/app/ctest-zookeeper/zookeeper-server/target/jacoco.exec"]
        classfiles = ["/home/hadoop/ecfuzz/data/app/ctest-zookeeper/zookeeper-server/target/zookeeper-3.5.6.jar"]
        outdir = "/home/hadoop/jacoco-0.8.7/cov-unit-zookeeper"
        ans = self.get_cov_unit(unit_path, classfiles, outdir)
        return ans

    def deleteDir(self,directory):
        if os.path.exists( directory ):
            if not os.access(directory, os.W_OK):
                os.chmod(directory, stat.S_IWRITE)
            shutil.rmtree(directory) 

    def get_cov_unit(self,unit_path:list, classfiles:list, outdir:str) -> list:
        # return list of cov [branch, path, line]
        # unit_path = ["/home/hadoop/ecfuzz/data/app/ctest-hbase/hbase-server/target/jacoco.exec"]
        # classfiles = ["/home/hadoop/ecfuzz/data/app/ctest-hbase/hbase-server/target/hbase-server-2.2.2.jar"]
        cmd = f"java -jar /home/hadoop/jacoco-0.8.7/lib/jacococli.jar report"
        flag = False
        for unit in unit_path:
            if os.path.exists(unit):
                # if exec exists
                cmd = cmd + f" {unit}"
                flag = True
        
        if flag == False:
            # if no exec then return 0
            self.logger.info(f'>>>>[getCov] get no exec for project')
            return [0,0,0]

        for classfile in classfiles:
            cmd = cmd + f" --classfiles {classfile}"
        # outdir = "/home/hadoop/jacoco-0.8.7/cov-unit-hdfs"
        cmd = cmd + f" --html {outdir}"
        if os.path.exists(outdir):
            self.deleteDir(outdir)
        # run and get cov info
        with open(os.devnull, 'w') as f:
            try:
                process = subprocess.Popen(cmd, shell=True, stderr=f, stdout=f)
                self.logger.info(f'>>>>[getCov] get cov process is running')
                # print("process running")
                process.communicate()
            except Exception as e:
                # print(e)
                self.logger.info(f'>>>>[getCov] get cov process has exception : {e}')
        # get ans
        index_path = os.path.join(outdir, "index.html")
        ans = self.getCovNum.getHtml(index_path)
        return ans

    def get_cov_sys_hcommon(self) -> list:
        # return list of cov [branch, path, line]
        unit_path = ["/home/hadoop/jacoco-0.8.7/hdfs.exec"]
        classfiles = ["/home/hadoop/ecfuzz/data/app_sysTest/hadoop-2.8.5-work/share/hadoop/common/hadoop-common-2.8.5.jar",
                        "/home/hadoop/ecfuzz/data/app_sysTest/hadoop-2.8.5-work/share/hadoop/hdfs/hadoop-hdfs-2.8.5.jar",
                        "/home/hadoop/ecfuzz/data/app_sysTest/hadoop-2.8.5-work/share/hadoop/hdfs/hadoop-hdfs-client-2.8.5.jar"]
        outdir = "/home/hadoop/jacoco-0.8.7/cov-sys-hcommon"
        ans = self.get_cov_unit(unit_path, classfiles, outdir)
        return ans

    def get_cov_sys_hdfs(self) -> list:
        # return list of cov [branch, path, line]
        unit_path = ["/home/hadoop/jacoco-0.8.7/hdfs.exec"]
        classfiles = ["/home/hadoop/ecfuzz/data/app_sysTest/hadoop-2.8.5-work/share/hadoop/common/hadoop-common-2.8.5.jar",
                        "/home/hadoop/ecfuzz/data/app_sysTest/hadoop-2.8.5-work/share/hadoop/hdfs/hadoop-hdfs-2.8.5.jar",
                        "/home/hadoop/ecfuzz/data/app_sysTest/hadoop-2.8.5-work/share/hadoop/hdfs/hadoop-hdfs-client-2.8.5.jar"]
        outdir = "/home/hadoop/jacoco-0.8.7/cov-sys-hdfs"
        ans = self.get_cov_unit(unit_path, classfiles, outdir)
        return ans

    def get_cov_sys_hbase(self) -> list:
        # return list of cov [branch, path, line]
        unit_path = ["/home/hadoop/jacoco-0.8.7/hbase.exec"]
        classfiles = ["/home/hadoop/ecfuzz/data/app_sysTest/hbase-2.2.2-work/lib/hadoop-common-2.8.5.jar",
                        "/home/hadoop/ecfuzz/data/app_sysTest/hbase-2.2.2-work/lib/hbase-common-2.2.2.jar",
                        "/home/hadoop/ecfuzz/data/app_sysTest/hbase-2.2.2-work/lib/hbase-server-2.2.2.jar",
                        "/home/hadoop/ecfuzz/data/app_sysTest/hbase-2.2.2-work/lib/hbase-client-2.2.2.jar"]
        outdir = "/home/hadoop/jacoco-0.8.7/cov-sys-hdfs"
        ans = self.get_cov_unit(unit_path, classfiles, outdir)
        return ans

    def get_cov_sys_alluxio(self) -> list:
        # return list of cov [branch, path, line]
        unit_path = ["/home/hadoop/jacoco-0.8.7/alluxio.exec"]
        classfiles = ["/home/hadoop/ecfuzz/data/app_sysTest/alluxio-2.1.0-work/assembly/alluxio-client-2.1.0.jar",
                        "/home/hadoop/alluxio-server-2.1.0.jar"]
        outdir = "/home/hadoop/jacoco-0.8.7/cov-sys-alluxio"
        ans = self.get_cov_unit(unit_path, classfiles, outdir)
        return ans

    def get_cov_sys_zookeeper(self) -> list:
        # return list of cov [branch, path, line]
        unit_path = ["/home/hadoop/jacoco-0.8.7/zookeeper.exec"]
        classfiles = ["/home/hadoop/ecfuzz/data/app_sysTest/zookeeper-3.5.6-work/lib/zookeeper-3.5.6.jar"]
        outdir = "/home/hadoop/jacoco-0.8.7/cov-sys-zookeeper"
        ans = self.get_cov_unit(unit_path, classfiles, outdir)
        return ans

    def delete_execs(self):
        # in the end, this method must be called
        exec_list = [
            "/home/hadoop/ecfuzz/data/app/ctest-hadoop/hadoop-common-project/hadoop-common/target/jacoco.exec",
            "/home/hadoop/jacoco-0.8.7/hdfs.exec",
            "/home/hadoop/ecfuzz/data/app/ctest-hadoop/hadoop-hdfs-project/hadoop-hdfs/target/jacoco.exec",
            "/home/hadoop/ecfuzz/data/app/ctest-hbase/hbase-server/target/jacoco.exec",
            "/home/hadoop/jacoco-0.8.7/hbase.exec",
            "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/base/target/jacoco.exec",
            "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/client/fs/target/jacoco.exec",
            "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/client/hdfs/target/jacoco.exec",
            "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/common/target/jacoco.exec",
            "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/server/common/target/jacoco.exec",
            "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/server/master/target/jacoco.exec",
            "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/server/proxy/target/jacoco.exec",
            "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/server/worker/target/jacoco.exec",
            "/home/hadoop/ecfuzz/data/app/ctest-alluxio/core/transport/target/jacoco.exec",
            "/home/hadoop/jacoco-0.8.7/alluxio.exec",
            "/home/hadoop/ecfuzz/data/app/ctest-zookeeper/zookeeper-server/target/jacoco.exec",
            "/home/hadoop/jacoco-0.8.7/zookeeper.exec"
        ]
        for exec in exec_list:
            if os.path.exists(exec):
                os.remove(exec)