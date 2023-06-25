import pymongo, socket, time
from pymongo import MongoClient
from utils.Configuration import Configuration

class MongoDb(object):
    mongo_client = None
    # 数据库表
    data_base = None
    # 种子的存储集合
    seed_collection = None
    # 最后结果的存储集合
    result_collection = None
    def __init__(self, ip: str, port: int) -> None:
        self.mongo_client = MongoClient(host=ip, port=port)
        self.set_database(self.get_ip_time())
        self.set_collection('seed', 'result')
        self.cov_unit_collection = self.data_base["unit-coverage"]
        self.cov_sys_collection = self.data_base["sys-coverage"]
        self.exception_collection = self.data_base["exception-map"]
        
    def set_database(self, dataBase: str):
        # 先设置数据库表名
        self.data_base = self.mongo_client[dataBase]

    # def clean(self):
    #     # 删除指定的数据库表
    #     # self.data_base.drop_collection()
    #     self.mongo_client.drop_database()
    
    def set_collection(self, seed_collection: str, result_collection: str):
        # 再设置不同名字的集合
        self.seed_collection = self.data_base[seed_collection]
        self.result_collection = self.data_base[result_collection]
        
    def insert_seed_file_to_db(self, file_path:str):
        # 把文件以二进制的形式写入数据库集合
        with open(file_path, 'rb') as file:
            self.seed_collection.insert_one({
                'file_name': file_path,
                'file_data': file.read()
            })
    
    def insert_map_to_db(self, collection_name:str, data:dict) -> None:
        # 根据传入的名称，创建集合，把数据写入到对应的集合中去
        # 在当前数据库中创建一个集合collection_name，并把当前的data写入到对应的集合中去
        col = self.data_base[collection_name]
        # col.delete_many({})
        col.insert_one(data)
    
    def insert_result_to_db(self, data_map: dict):
        # 把一个字典数据全部写入到数据库中
        self.result_collection.insert_one(data_map)
        
    def insert_exception_to_db(self, data_map: dict):
        # 把一个字典数据全部写入到数据库中
        self.exception_collection.insert_one(data_map)        

    def insert_cov_unit_to_db(self, data_map: dict):
        self.cov_unit_collection.insert_one(data_map)
        
    def insert_cov_sys_to_db(self, data_map: dict):
        self.cov_sys_collection.insert_one(data_map)
        
    def write_seed_to_disk(self, file_dir:str):
        # 服务端需要做的事情
        for seed in self.seed_collection.find():
            file_name = seed.get('file_name')
            file_data = seed.get('file_data')
            with open(file_dir, 'wb') as f:
                f.write(file_data)
        pass
    
    def get_data(self):
        for seed in self.seed_collection.find():
            print(seed)
            print(seed.get('file_name'))
        for re in self.result_collection.find():
            print(re)
    
    def show_all_dbs(self):
        print(self.mongo_client.list_database_names())
        
    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        # print(s.getsockname()[0])
        return s.getsockname()[0]

    def get_time(self) -> str:
        return str(time.time())

    def get_ip_time(self) -> str:
        res = self.get_local_ip() + '_' + self.get_time()
        re = ''
        for x in res:
            if x == '.':
                re += '_'
            else:
                re += x
        re = re + '_' + Configuration.fuzzerConf['project'] + '_' + Configuration.fuzzerConf['data_viewer_env']
        return re
        
if __name__ == "__main__":
    mongo = MongoDb('192.168.4.249',27017)
    # mongo.set_database("test1")
    # # 必须保证所有的数据库表名都是不一样的，采用ip加时间戳的形式
    # mongo.set_collection('seed','result')
    # mongo.insert_seed_file_to_db('/home/hadoop/zookeeper-s/st_fail1/Testcase-6.cfg')
    # data = {'total_failed':20, 'st1':15, 'st2':3, 'st3':2}
    # mongo.insert_result_to_db(data)
    # mongo.get_data()
    # mongo.show_all_dbs()
    # mongo.write_seed_to_disk('/home/hadoop/DOCKER/test.cfg')
    # mongo.clean()
    # print(mongo.get_local_ip())
    # print(mongo.get_time())