import pymongo, os, json
from pymongo import MongoClient

class MongoServer(object):

    Mongo_Client = None 
    dbs_list = None
    cur_path = os.path.dirname(__file__)
    def __init__(self, host: str, port: int) -> None:
        self.Mongo_Client = MongoClient(host=host, port=port)
        self.dbs_list = self.Mongo_Client.list_database_names()
    
    def show_all_dbs(self):    
        return self.dbs_list
    
    def get_ip_time(self, db_name: str) -> list:
        # return ip, time, project, experimentName
        cnt = 0
        spl = 0
        for index,c in enumerate(db_name):
            if c == '_':
                cnt += 1
            if cnt == 4:
                spl = index
                break
        alter = db_name[spl+1:]
        # find the second and the third '_'
        res = alter.split('_')
        return db_name[:spl], db_name[spl+1:], res[2], res[3]
    
    def mkdirs(self):
        for db_name in self.dbs_list:
            if db_name in ['admin', 'config', 'local']:
                continue
            ip, time, pro, exp = self.get_ip_time(db_name=db_name)
            dir = os.path.join(self.cur_path, ip, time, 'st_fail_testcases')
            if not os.path.exists(dir):
                os.makedirs(dir)
    
    def get_seed_path(self, t_path: str):
        index = t_path.find('st_fail_testcases')
        tmp = t_path[index:]
        tmp = tmp[tmp.find('/')+1:]
        i = tmp.find('/')
        res1 = tmp[:i]
        res2= tmp[i+1:]
        # print(res1,res2)
        return res1, res2
    
    def write_seed_to_disk(self):
        self.mkdirs()
        # traverse the all dbs
        for db_name in self.dbs_list:
            if db_name in ['admin', 'config', 'local']:
                continue
            db = self.Mongo_Client[db_name]
            # seed_col has mutilpul records
            # result_col has one records
            seed_col = db['seed']
            # write seed
            ip, time, pro, exp = self.get_ip_time(db_name=db_name)
            dir = os.path.join(self.cur_path, ip, time, 'st_fail_testcases')
            for seed in seed_col.find():
                file_name = seed.get('file_name')
                file_data = seed.get('file_data')
                # print(file_name)
                st_fail, ts_name = self.get_seed_path(file_name)
                st_dir = os.path.join(dir, st_fail)
                # crate st_dir
                if not os.path.exists(st_dir):
                    os.mkdir(st_dir)
                file_path = os.path.join(st_dir, ts_name)
                with open(file_path, 'wb') as f:
                    f.write(file_data) 
                    
    def write_result_to_disk(self):
        self.mkdirs()
        # traverse the all dbs
        for db_name in self.dbs_list:
            if db_name in ['admin', 'config', 'local']:
                continue
            db = self.Mongo_Client[db_name]

            ip, time, pro, exp = self.get_ip_time(db_name=db_name)
            dir = os.path.join(self.cur_path, ip, time)
            result_col = db['result']
            # write result
            result = result_col.find_one({},{"_id":0})
            # print(result)
            result_path = os.path.join(dir, 'result.json')
            with open(result_path, 'w') as f:
                json.dump(result, f)
    
    def write_exception_to_disk(self):
        self.mkdirs()
        # traverse the all dbs
        for db_name in self.dbs_list:
            if db_name in ['admin', 'config', 'local']:
                continue
            db = self.Mongo_Client[db_name]

            ip, time, pro, exp = self.get_ip_time(db_name=db_name)
            dir = os.path.join(self.cur_path, ip, time)
            result_col = db["exception-map"]
            # write result
            result = result_col.find_one({},{"_id":0})
            # print(result)
            result_path = os.path.join(dir, 'exception-map.json')
            with open(result_path, 'w') as f:
                json.dump(result, f)
            
    def write_cov_to_disk(self):
        self.mkdirs()
        # traverse the all dbs
        for db_name in self.dbs_list:
            if db_name in ['admin', 'config', 'local']:
                continue
            db = self.Mongo_Client[db_name]

            ip, time, pro, exp = self.get_ip_time(db_name=db_name)
            dir = os.path.join(self.cur_path, ip, time)
            cov_unit_col = db['unit-coverage']
            cov_sys_col = db['sys-coverage']
            # write result
            cov1 = cov_unit_col.find_one({},{"_id":0})
            # print(cov1)
            cov2 = cov_sys_col.find_one({},{"_id":0})
            # print(cov2)
            cov_unit_path = os.path.join(dir, f'{pro}-{exp}-cov_unit_result.json')
            with open(cov_unit_path, 'w') as f:
                json.dump(cov1, f)
            cov_sys_path = os.path.join(dir, f'{pro}-{exp}-cov_sys_result.json')
            with open(cov_sys_path, 'w') as f:
                json.dump(cov2, f)
    
    def write_map_to_disk(self, collection_name:str) -> None:
        # 根据传入的集合名称，把改集合中的所有数据写入磁盘
        # 实际上只会写入一条数据，如果是写入的多条数据，那么也可以把全部写入
        self.mkdirs()
        # traverse the all dbs
        for db_name in self.dbs_list:
            if db_name in ['admin', 'config', 'local']:
                continue
            db = self.Mongo_Client[db_name]

            ip, time, pro, exp = self.get_ip_time(db_name=db_name)
            dir = os.path.join(self.cur_path, ip, time)
            
            if collection_name not in db.list_collection_names():
                print(f'there is no collection of {collection_name}')
                continue
            
            result_col = db[collection_name]
            # write result
            res = {}
            for idx, x in enumerate(result_col.find({},{"_id":0})):
                # 第一个数据不要
                # 如果插入的数据有多条，我们需要对它进行编号，比如idx作为编号
                res[idx] = x
            result = result_col.find_one({},{"_id":0})
            # print(result)
            result_path = os.path.join(dir, f'{collection_name}.json')
            with open(result_path, 'w') as f:
                json.dump(res, f)
    
    def clean(self):
    # delete all dbs
        for db in self.dbs_list:
            if db in ['admin', 'config', 'local']:
                continue
            self.Mongo_Client.drop_database(db)

if __name__ == "__main__":
    Mongo_Server = MongoServer('192.168.4.249', 27017)
    # Mongo_Server.write_seed_to_disk()
    # Mongo_Server.mkdirs()
    # 把结果信息保存（不良反应数目）
    Mongo_Server.write_result_to_disk()
    # 保存异常num信息
    Mongo_Server.write_exception_to_disk()
    # 保存异常信息对应的配置文件
    Mongo_Server.write_map_to_disk("ExceptionMapReason")
    Mongo_Server.write_map_to_disk("newEastSeed")
    Mongo_Server.write_map_to_disk("expSeed")
    # 把覆盖率信息保存
    # Mongo_Server.write_cov_to_disk()
    # 清除数据库所有信息，慎用
    # Mongo_Server.clean()