import unittest
import sys

sys.path.append("../../src/")

from utils.Configuration import Configuration


class TestConfiguration(unittest.TestCase):
    def testParseConfiguration(self):
        Configuration.parseConfiguration()
        configuration = Configuration.fuzzerConf

        test_str_list = configuration['test_str_list']

        print(test_str_list)
        res = Configuration.putConf['injecting_location']
        print(res)
        print("surefire dir is : {}".format(Configuration.putConf['surefire_location']))

        assert isinstance(test_str_list, list)


if __name__ == '__main__':
    unittest.main()
