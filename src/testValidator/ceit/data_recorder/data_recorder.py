# encoding:utf-8

from testValidator.ceit.data_recorder.data_structure import RedisDataValue
import redis


class DataRecorder( object ):
    prefix = ""
    redis_cli = None
    main_keys = []

    def __init__(self):
        try:
            self.redis_cli = redis.Redis( host='127.0.0.1', port=6379 )
        except Exception as e:
            print(e.message)
        finally:
            pass

    def set_prefix(self, prefix):
        self.prefix = prefix

    def insert(self, name, key, value):
        self.redis_cli.hset( name, key, str(value) )

    def get_names(self):
        return self.redis_cli.keys( pattern=self.prefix + "*" )

    def get_keys(self, name):
        return self.redis_cli.hkeys( name )

    def get_all_value_from_name(self, name):
        return self.redis_cli.hvals( name )

    def get_value_from_key(self, name, key):
        return self.redis_cli.hget( name, key )

    def delete(self, key):
        self.redis_cli.delete( key )

    def clean(self):
        redis_cli = self.redis_cli
        if self.get_names():
            redis_cli.delete( *redis_cli.keys( pattern=self.prefix + "*" ) )

    def dump_overall_results(self, file_path):
        with open(file_path, 'w') as fp:
            fp.write("Option Name, Mutation Name, Testcase Results, Analyzer Results, Observer4Crash, Observer4Hang, Observer4Termination\n")
            r = RedisDataValue()
            for name in self.get_names():
                for key in self.get_keys(name):
                    value = self.get_value_from_key(name, key)
                    r = r(value)
                    testcase_results = r.overall_results.results["testcase_results"]
                    analyzer_results = r.overall_results.results["analyzer_results"]
                    observer_crash_results = str(r.overall_results.results["observer_results"]["crash"])
                    observer_hang_results = str(r.overall_results.results["observer_results"]["hang"])
                    observer_termination_results = str(r.overall_results.results["observer_results"]["termination"])
                    ls = [name, key, testcase_results, analyzer_results, observer_crash_results, observer_hang_results, observer_termination_results]
                    line = ', '.join(ls)
                    line = line + '\n'
                    fp.write(line)



def main():
    # dh = DataRecorder()
    #
    # dh.insert("name1", "key1", {"key1":"value"})
    # dh.insert("name1", "key2", {"key2":"value"})
    # dh.insert("name2", "key3", {"key3":"value"})

    # print dh.get_names()
    # print dh.get_value_from_key("name1", "key1")
    # for name in dh.get_names():
    #     print dh.get_all_value_from_name(name)
    # dh.clean()
    # print dh.redis_cli.keys()
    dh = DataRecorder()
    # dh.clean()
    # dh.insert( "name1", "key1", {"key1": "value"} )
    # for key in dh.get_names():
    #     print "key: " + key
    #     for i in dh.get_all_value_from_name( key ):
    #         print i
    # print dh.get_all_value_from_name("IPaddress")

    dh.dump_overall_results()


if __name__ == '__main__':
    main()
