# 突变是现有配置错误注入测试工具中使用最广泛的配置错误生成方法，包括 ConfErr [21]、ConfInject [8]、ConfTest [25]、ConfVD [24] 和 ConfDiagDetector [56]。
# 关键思想是改变给定的配置值（通常是默认值）以根据预定义的变异规则（例如遗漏、大小写更改）生成错误值，以模拟各种类型的人为错误 [21]。
# 我们实现了 ConfDiagDetector [56]（最先进的基于突变的配置错误注入测试工具）使用的五个突变规则，它们代表了基于突变的工具中的突变规则 [8、21、24、25 , 56]。
# 五个规则是 1) 删除现有值（例如，łXMLž→łž），
# 2）从预定义池中随机选择相同数据类型的值（例如，łXMLž→łTXTž），
# 3）随机选择值来自预定义池的不同数据类型（例如 łXMLž → ł123ž），
# 4）随机注入拼写错误（例如 łXMLž → łXLLž），
# 以及 5）更改文本的大小写（例如 łXMLž → łxmlž）。
# 因此，我们为每个参数生成五个错误值

class ConfDiagDetector():
# 突变 类型推断对应到相应类型的misconf生成 返回[misconf1, misconf2]相同类型和不同类型的值 然后再对这个值进行MISPELLING_VALUE、DELETE_VALUE、CHANGE_CASE_VALUE类型的变化
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
        self.option_types = []
        self.option_values = []
        self.option_value = ""
        self.option_constraints = []
        self.option_num = 0
        self.misconfs = []
        func_dict = {"STR": self.str_misconf,
                     "ENUM": self.enum_misconf,
                     "BOOL": self.bool_misconf,
                     "NUM" : self.num_misconf,
                     "URL": self.url_misconf,
                     "IP": self.ip_misconf,
                     "PORT": self.port_misconf,
                     "PATH": self.path_misconf,
                     "SPECSTR" : self.spe_str_misconf,
                     "PERMISSION" : self.permission_misconf} #数据类型

        value_func_dict = {
            "MISPELLING_VALUE": self.misspelling_value,
            "DELETE_VALUE": self.delete_value,
            "CHANGE_CASE_VALUE": self.change_case_value,#值改变类型

        }

        self.option_value = option["value"]
        self.option_num = option["constraint"].count("|")+1
        constraints_list = option["constraint"].split("|")
        if self.option_num == 1:
            self.option_values.append(option["value"])#默认值
            type, constraint = self.extract_constraints(constraints_list[0])
            self.option_constraints.append(constraint)#提取约束
            self.option_types.append(type)#提取类型
        else:
            for i in range(self.option_num):
                id = str(i+1)
                self.option_values.append(option["value"+id])
                type, constraint = self.extract_constraints(constraints_list[i])
                self.option_constraints.append(constraint)
                self.option_types.append(type)
        self.misconfs = []
        for i in range(self.option_num):
            key = option["key"]
            value = self.option_values[i]
            constraint = self.option_constraints[i]
            type = self.option_types[i]
            misconf_list = func_dict[type](value, constraint) # 类型推断对应到相应类型的misconf生成 返回[misconf1, misconf2]相同类型和不同类型的值
            misconf_list = self.add_other_values(misconf_list, i)
            self.misconfs.extend(misconf_list)
            misconf_list = []
            for j in value_func_dict:# 再对第一次返回[misconf1, misconf2]进行值变化MISPELLING_VALUE、DELETE_VALUE、CHANGE_CASE_VALUE
                if value_func_dict[j]( key, value ) != None:
                    misconf_list = [value_func_dict[j]( key, value )] # 值变化后的[misconf1, misconf2]
                misconf_list = self.add_other_values( misconf_list, i ) 
                self.misconfs.extend( misconf_list )

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
        else:
            for misconf in misconf_list:
                misconf_value = misconf["value"]
                temp_list = []
                for j in range(self.option_num):
                    if j == i:
                        temp_list.append(misconf_value)
                    else:
                        temp_list.append(self.option_values[j])

                target_value = " ".join(temp_list)
                misconf["value"] = target_value
                misconf["name"] = "option_" + str(i) + "_" + misconf["name"]
            return misconf_list




    def extract_constraints(self, constraint):
            if "[" not in constraint:
                option_type = constraint
                option_constraint = ""
            else:
                option_type = constraint.split( "[" )[0]
                option_constraint = "[" + constraint.split( "[" )[1]
            return option_type, option_constraint

    def str_misconf(self, value, constraint):
        misconf1 = {"name": "str_othertype",
                 "key": None,
                 "operator": None,
                 "value": "1024"}
        misconf2 = {"name": "str_sametype",
                 "key": None,
                 "operator": None,
                 "value": "ceitinspector"}
        return [misconf1, misconf2]

    def enum_misconf(self, value, constraint):
        misconf1 = {"name": "enum_othertype",
                 "key": None,
                 "operator": None,
                 "value": "1024"}
        misconf2 = {"name": "enum_sametype",
                 "key": None,
                 "operator": None,
                 "value": "ceitinspector"}
        return [misconf1, misconf2]

    def bool_misconf(self, value, constraint):
        misconf1 = {"name": "bool_othertype",
                 "key": None,
                 "operator": None,
                 "value": "1024"}
        misconf2 = {"name": "bool_sametype",
                 "key": None,
                 "operator": None,
                 "value": "yes"}
        return [misconf1, misconf2]

    def num_misconf(self, value, constraint):
        from random import randint
        randnum = randint(-2147483648,2147483647)
        misconf1 = {"name": "num_sametype",
                 "key": None,
                 "operator": None,
                 "value": str(randnum)}
        misconf2 = {"name": "num_othertype",
                 "key": None,
                 "operator": None,
                 "value": "ceitinspector"}
        return [misconf1, misconf2]


    def url_misconf(self, value, constraint):
        misconf1 = {"name": "url_othertype",
                 "key": None,
                 "operator": None,
                 "value": "1024"}
        misconf2 = {"name": "url_sametype",
                 "key": None,
                 "operator": None,
                 "value": "www.ceitinspector.com"}
        return [misconf1, misconf2]

    def ip_misconf(self, value, constraint):
        misconf1 = {"name": "ip_othertype",
                 "key": None,
                 "operator": None,
                 "value": "1024"}
        misconf2 = {"name": "ip_sametype",
                 "key": None,
                 "operator": None,
                 "value": "127.127.127.127"}
        return [misconf1, misconf2]

    def port_misconf(self, value, constraint):
        from random import randint
        randnum = randint(0,65535)
        misconf1 = {"name": "port_othertype",
                 "key": None,
                 "operator": None,
                 "value": "ceitinspector"}
        misconf2 = {"name": "port_sametype",
                 "key": None,
                 "operator": None,
                 "value": str(randnum)}
        return [misconf1, misconf2]

    def path_misconf(self, value, constraint):

        misconf1 = {"name": "path_othertype",
                 "key": None,
                 "operator": None,
                 "value": "1024"}
        misconf2 = {"name": "path_sametype",
                 "key": None,
                 "operator": None,
                 "value": "/ceitinspector"}
        return [misconf1, misconf2]

    def spe_str_misconf(self, value, constraint):
        misconf1 = {"name": "spec_othertype",
                 "key": None,
                 "operator": None,
                 "value": "1024"}
        misconf2 = {"name": "spec_sametype",
                 "key": None,
                 "operator": None,
                 "value": "ceitinspector"}
        return [misconf1, misconf2]

    def permission_misconf(self, value, constraint):
        misconf1 = {"name": "permission_othertype",
                 "key": None,
                 "operator": None,
                 "value": "ceitinspector"}
        misconf2 = {"name": "permission_sametype",
                 "key": None,
                 "operator": None,
                 "value": "0111"}
        return [misconf1, misconf2]

    def change_case_value(self, key, value):
        new_value = self.case_alt(value)
        return {"name": "change_case_value",
                    "key": None,
                    "operator": None,
                    "value": new_value}

    def delete_value(self, key, value):
        return {"name": "delete_value",
                "key": None,
                "operator": None,
                "value": ""}

    def misspelling_value(self, key, value):
        if len(value) == 0:
            return {"name": "mispellingValue",
                    "key": None,
                    "operator": None,
                    "value": ""}
        character = value[0]
        ascii = ord( character )
        #new_character = chr( ascii + 1 )
        new_character = "cfz"
        new_value = new_character + value[1:]
        return {"name": "mispellingValue",
                "key": None,
                "operator": None,
                "value": new_value}

    def path_handle_constraints(self, constraint): #方法内没用到

        constraint = constraint.strip( "[]" )
        constraint = constraint.split( ',' )
        absolute_or_relative = constraint[0] #A,R,B
        create_or_not = constraint[1] #Y,N
        file_or_dir = constraint[2] #F,D
        return absolute_or_relative, create_or_not, file_or_dir

    def num_handle_constraints(self, constraint): #方法内没用到
        constraint = constraint.strip( "[]" )
        default_types = {"UINT":[0, 4294967295],
                         "ULONG" : [0, 4294967295],
                         "INT" : [-2147483648,2147483647],
                         "LONG" : [-2147483648, 2147483647],
                         "LONGLONG" : [-9223372036854775808, 9223372036854775807],
                         "ULONGLONG": [0, 18446744073709551615],
                         "FLOAT":["",""],
                         "DOUBLE":["",""]}

        constraint = constraint.split( ',' )
        type = constraint[0]
        if type in default_types:
            type_range = default_types[type]
            if type in ["UINT", "ULONG", "INT", "LONG", "LONGLONG", "ULONGLONG"]:
                float_flag = False
            else:
                float_flag = True
        type_min = type_range[0]
        type_max = type_range[1]
        min_number = constraint[1]
        max_number = constraint[2]
        unit = constraint[3]
        return float_flag, type_min, type_max, min_number, max_number, unit

    def get_misconfs(self):
        return self.misconfs

    def prepare_test_env(self): #方法内没用到
        import os, shutil
        if os.path.exists( "/ceitinspector/TEST_CONFUZZ" ):
            shutil.rmtree( "/ceitinspector/TEST_CONFUZZ" )
        try:
            os.makedirs( "/ceitinspector/TEST_CONFUZZ" )
            with open("/ceitinspector/TEST_CONFUZZ/ConfuzzFile2Test", 'w') as fp:
                pass
        except:
            pass

    def prepare_port(self): #方法内没用到
        from threading import Thread
        class daemon_port(Thread):
            def __init__(self):
                Thread.__init__(self)
            def run(self):
                import socket
                address = ('localhost', 6789)
                server = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                server.bind( address )

                server.listen( 5 )

                client, addr = server.accept()
                data = client.recv( 1000 )
                client.sendall( b'Do you want to talk to me' )
                client.close()
                server.close()
        try:
            dp = daemon_port()
            dp.setDaemon(True)
            dp.start()
        except Exception:
            pass

    def case_alt(self, value):
        out = ""
        for c in value :
            if c == "1":
                out += '!'
            elif c == "2":
                out += '@'
            elif c == "3":
                out += '#'
            elif c == "4":
                out += '$'
            elif c == "5":
                out += '%'
            elif c == "6":
                out += "^"
            elif c == "7":
                out += '&'
            elif c == '8':
                out += "*"
            elif c == "9":
                out += "("
            elif c == "0":
                out += ")"
            elif c == " ":
                out += " "
            elif c.isalpha():
                out += c.swapcase()
            else:
                out += c
        return out