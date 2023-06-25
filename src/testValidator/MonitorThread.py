import psutil, time, os, threading
from queue import Queue

class MonitorThread(object):
    # static filed
    CpuException : bool = False
    MemoryException : bool = False
    FileSizeException : bool = False
    
    @staticmethod
    def cpuMonitorThread(stopQueue: Queue, stopSoon) -> None:
        # init the flag
        MonitorThread.CpuException = False
        data = []
        while True:
            # check the cpuPercent per second
            time.sleep(2)
            cpuPercent = psutil.cpu_percent()
            data.append(cpuPercent)
            if len(data) >= 5 and MonitorThread.isContinue(data):
                MonitorThread.CpuException = True
            # determine when to kill the thread
            if not stopQueue.empty():
                break
            if not stopSoon.empty():
                break
            
    @staticmethod
    def memoryMonitorThread(stopQueue: Queue, stopSoon) -> None:
        # init the flag
        MonitorThread.MemoryException = False
        data = []
        while True:
            # check the memoryPercent per second
            time.sleep(2)
            memoryPercent = psutil.virtual_memory().percent
            data.append(memoryPercent)
            if len(data) >= 5 and MonitorThread.isContinue(data):
                MonitorThread.MemoryException = True
            # determine when to kill the thread
            if not stopQueue.empty():
                break
            if not stopSoon.empty():
                break
    
    @staticmethod
    def fileSizeMonitorThread(stopQueue: Queue, fileDir:str, stopSoon) -> None:
        # init the flag
        MonitorThread.FileSizeException = False
        while True:
            # check the cpuPercent per second
            time.sleep(2)
            fileSize = MonitorThread.get_dir_size(fileDir)
            if fileSize > 500:
                MonitorThread.FileSizeException = True
            # determine when to kill the thread
            if not stopQueue.empty():
                break
            if not stopSoon.empty():
                break
    
    @staticmethod
    def get_dir_size(dir_path:str):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(dir_path):
            for file in filenames:
                file_path = os.path.join(dirpath, file)
                if os.path.isfile(file_path):
                    try:
                        total_size += os.path.getsize(file_path)
                    except Exception:
                        pass
        # 将字节数转换为 MB
        total_size_mb = total_size / (1024 * 1024)
        return total_size_mb
    
    @staticmethod
    def isContinue(data: list):
        count = 0
        for d in data:
            if d >= 90:
                count += 1
        if count >= 5:
            return True
        return False
        
    @staticmethod
    def threadMonitor(stopQueue: Queue, fileDir:str, stopSoon):
        # use stopQueue as a stop signal
        threading.Thread(target=MonitorThread.cpuMonitorThread, args=[stopQueue, stopSoon]).start()
        threading.Thread(target=MonitorThread.memoryMonitorThread, args=[stopQueue, stopSoon]).start()
        threading.Thread(target=MonitorThread.fileSizeMonitorThread, args=[stopQueue, fileDir, stopSoon]).start()