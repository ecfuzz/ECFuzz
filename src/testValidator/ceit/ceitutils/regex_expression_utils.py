# -*- coding:utf-8 -*-

import re



def get_re_pattern(string):
    pass

def find_pattern(string, pattern):
    a = re.search(pattern=pattern, string=string)
    if a != None:
        return a.span()
    else:
        return False

def remove_pattern(string, pattern):
    a = find_pattern(string, pattern)
    if type(a) == tuple:
        head = a[0]
        tail = a[1]
        sub_string = string[head:tail]
        new_string = string.replace(sub_string, " ")
        return new_string
    else:
        return string

def add_escape(string):
    #string = string.replace("d", "\d")
    #string = string.replace("|", "\|")

    return string

def main():
    str = "[Fri Jan 18 15:06:10.321380 2019] [core:notice] [pid 25013] AH00094: Command line: '/root/httpd/prefork/bin/httpd -d /mod_perl-2.0.10/t -f /mod_perl-2.0.10/t/conf/httpd.conf -D APACHE2 -D APACHE2_4 -D PERL_USEITHREADS'"
    pattern="/root/httpd/prefork/bin/httpd -d /mod_perl-2.0.10/t"
    pattern=add_escape(pattern)
    # print(find_pattern(string=str, pattern=pattern))
    # print remove_pattern(string=str, pattern=pattern)

if __name__ == '__main__':
    main()