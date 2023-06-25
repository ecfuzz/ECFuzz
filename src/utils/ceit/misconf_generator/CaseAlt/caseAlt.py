class CaseAlt():

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
                     "PERMISSION" : self.permission_misconf}

        self.option_value = option["value"]
        self.option_num = option["constraint"].count("|")+1
        constraints_list = option["constraint"].split("|")
        if self.option_num == 1:
            self.option_values.append(option["value"])
            type, constraint = self.extract_constraints(constraints_list[0])
            self.option_constraints.append(constraint)
            self.option_types.append(type)
        else:
            for i in range(self.option_num):
                id = str(i+1)
                self.option_values.append(option["value"+id])
                type, constraint = self.extract_constraints(constraints_list[i])
                self.option_constraints.append(constraint)
                self.option_types.append(type)
        self.misconfs = []
        for i in range(self.option_num):
            value = self.option_values[i]
            constraint = self.option_constraints[i]
            type = self.option_types[i]
            misconf_list = func_dict[type](value, constraint)
            misconf_list = self.add_other_values(misconf_list, i)
            self.misconfs.extend(misconf_list)

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
        return []

    def enum_misconf(self, value, constraint):
        return []

    def bool_misconf(self, value, constraint):
        return []

    def num_misconf(self, value, constraint):
        casealt = self.case_alt(value)
        for c in value:
            pass
        misconf1 = {"name": "num_changecase",
                 "key": None,
                 "operator": None,
                 "value": casealt}
        return [misconf1]


    def url_misconf(self, value, constraint):
        return []

    def ip_misconf(self, value, constraint):
        return []

    def port_misconf(self, value, constraint):
        return []

    def path_misconf(self, value, constraint):
        return []

    def spe_str_misconf(self, value, constraint):
        return []

    def permission_misconf(self, value, constraint):
        return []

    def path_handle_constraints(self, constraint):

        constraint = constraint.strip( "[]" )
        constraint = constraint.split( ',' )
        absolute_or_relative = constraint[0] #A,R,B
        create_or_not = constraint[1] #Y,N
        file_or_dir = constraint[2] #F,D
        return absolute_or_relative, create_or_not, file_or_dir

    def num_handle_constraints(self, constraint):
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

    def prepare_test_env(self):
        import os, shutil
        if os.path.exists( "/ceitinspector/TEST_CONFUZZ" ):
            shutil.rmtree( "/ceitinspector/TEST_CONFUZZ" )
        try:
            os.makedirs( "/ceitinspector/TEST_CONFUZZ" )
            with open("/ceitinspector/TEST_CONFUZZ/ConfuzzFile2Test", 'w') as fp:
                pass
        except:
            pass

    def prepare_port(self):
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
            else:
                if c.isalpha():
                    out += c.swapcase()
                else:
                    pass
        return out
