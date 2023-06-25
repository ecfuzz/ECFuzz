class ConfErr():
# ConfErr突变 和afl的变异思路类似
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
        none_value_func_dict = {"OMISSION": self.omission,
                                "MISPELLING_PARAMETER": self.misspelling_parameter,
                                "CHANGE_CASE_PARAMETER": self.change_case_parameter,
                                "WRONG_DELIMITER": self.wrong_delimiter,
                                "DELETE_DELIMITER": self.delete_delimiter
                                }
        value_func_dict = {
            "MISPELLING_VALUE": self.misspelling_value,
            "DELETE_VALUE": self.delete_value,
            "CHANGE_CASE_VALUE": self.change_case_value,

        }

        self.option_values = []
        self.option_value = option["value"]
        self.option_num = option["constraint"].count( "|" ) + 1
        if self.option_num == 1:
            self.option_values.append( option["value"] )
        else:
            for i in range( self.option_num ):
                id = str( i + 1 )
                self.option_values.append( option["value" + id] )
        misconf_list = []
        key = option["key"]
        value = option["value"]
        self.misconfs = []
        # for j in none_value_func_dict:
        #     if none_value_func_dict[j]( key, value ) != None:
        #         misconf_list = [none_value_func_dict[j]( key, value )]
        #         self.misconfs.extend( misconf_list )

        for i in range( self.option_num ):
            value = self.option_values[i]
            for j in value_func_dict:
                if value_func_dict[j]( key, value ) != None:
                    misconf_list =[value_func_dict[j]( key, value )]
                misconf_list = self.add_other_values( misconf_list, i )
                self.misconfs.extend( misconf_list )

    def omission(self, key, value):
        return {"name": "omission",
                "key": "",
                "operator": None,
                "value": None}

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

    def misspelling_parameter(self, key, value):
        character = key[0]
        ascii = ord( character )
        new_character = chr( ascii + 1 )
        new_key = new_character + key[1:]
        return {"name": "mispelling_parameter",
                "key": new_key,
                "operator": None,
                "value": None}

    def delete_value(self, key, value):
        return {"name": "delete_value",
                "key": None,
                "operator": None,
                "value": ""}

    def change_case_parameter(self, key, value):
        if key.isupper():
            new_key = key.lower()
        elif key.islower():
            new_key = key.upper()
        else:
            new_key = key.upper()
        if new_key != key:
            return {"name": "change_case_parameter",
                    "key": new_key,
                    "operator": None,
                    "value": None}
        else:
            return None

    def change_case_value(self, key, value):
        if value.isupper():
            new_value = value.lower()
        elif value.islower():
            new_value = value.upper()
        else:
            new_value = value.upper()
        if new_value != value:
            return {"name": "change_case_value",
                    "key": None,
                    "operator": None,
                    "value": new_value}
        else:
            return None

    def wrong_delimiter(self, key, value):
        return {"name": "wrong_delimiter",
                "key": None,
                "operator": " : ",
                "value": None}

    def delete_delimiter(self, key, value):
        return {"name": "delete_delimiter",
                "key": None,
                "operator": "",
                "value": None}

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
        else:

            for misconf in misconf_list:
                misconf_value = misconf["value"]
                temp_list = []
                for j in range( self.option_num ):
                    if j == i:
                        if misconf_value == None:
                            temp_list.append( self.option_values[j] )
                        else:
                            temp_list.append( misconf_value )
                    else:
                        temp_list.append( self.option_values[j] )
                target_value = " ".join( temp_list )
                misconf["value"] = target_value
                misconf["name"] = "option_" + str( i ) + "_" + misconf["name"]
            return misconf_list


def main():
    option = {"key": "Test", "value": "80", "constraint" : "NUM"}
    cf = ConfErr( option )
    # print cf.get_misconfs()
    # print len(cf.get_misconfs())


if __name__ == '__main__':
    main()
