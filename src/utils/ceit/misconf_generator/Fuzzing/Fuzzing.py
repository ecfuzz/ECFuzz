import hashlib
import time


class Fuzzing( object ):
    def __init__(self, option):
        """
        :param option: {u'key': u'Listen', u'value': u'80', u'constraint': u'PORT'}
                    {
                      "key": "directive",
                      "value" : "123 456 unit"
                      "value1": "123",
                      "value2" : "456",
                      "value3" : "unit",
                      "constraint": "INT[,]|INT[,]|ENUM",
                      "dependency_constraint" : {"2":"www.baidu.com"}
                    }
        """
        self.option_values = []
        self.option_value = option["value"] # 配置项对应到默认值
        self.option_num = option["constraint"].count("|")+1 # 配置项对应到的约束关系
        if self.option_num == 1: 
            self.option_values.append(option["value"]) #如果只有一个约束关系则可以添加默认值到option_values中
        else:
            for i in range(self.option_num): #多个约束关系则可以添加多个值到option_values中
                id = str(i+1)
                self.option_values.append(option["value"+id])


        self.misconfs = [] # 生成的错误配置项值集合
        for i in range(self.option_num):# 对照着约束关系的个数
            misconf = [{ # misconf的数据结构 重要的是k-v
                "name": "randomstring",
                "key": None,
                "operator": None,
                "value": self.create_md5()# 随机生成了字符串
            }]
            misconf = self.add_other_values(misconf, i)
            self.misconfs.extend(misconf)

    def create_md5(self):
        m = hashlib.md5()
        m.update( bytes(str( time.time() ).encode('utf-8'))  )
        return m.hexdigest()

    def get_misconfs(self):
        return self.misconfs

    def add_other_values(self, misconf_list, i):
        """

        :param misconf_list:  [{"name": "str_misconf",
                 "key": None,
                 "operator": None,
                 "value": "wrongvalue"}]
        :param i: the index of the misconf_value
        :return:
        """
        if self.option_num == 1:
            return misconf_list
        else: #存在多个约束关系，对应多个value值
            for misconf in misconf_list:
                misconf_value = misconf["value"] #随机生成的值self.create_md5()
                temp_list = []
                for j in range(self.option_num):# 若为多个 只变对应的约束关系的那一个 其他仍然为给的value
                    if j == i:
                        temp_list.append(misconf_value)
                    else:
                        temp_list.append(self.option_values[j])

                target_value = " ".join(temp_list)
                misconf["value"] = target_value
                misconf["name"] = "option_" + str(i) + "_" + misconf["name"]
            return misconf_list
