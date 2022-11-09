# -*- coding:utf-8 -*-
import os


def get_files_in_dir(directory, recursion = False):
    temp_files = {}
    for root,dirs,files in os.walk(directory):
        if recursion == False:
            temp_files[directory] = files
            return temp_files
        else:
            temp_files[root] = files
    return temp_files

def get_file_content(file_path):
    with open(file_path) as fp:
        return fp.read()

def get_rid_of_string(content, string):
    return content.replace(string, " ")

def path_is_existed(path):
    return os.path.exists(path)



def main():
    files = get_files_in_dir("../modules", recursion=False)
    print(files["../modules"])

if __name__ == '__main__':
    main()

