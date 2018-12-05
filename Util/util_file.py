#! python
# -*- coding: utf-8 -*-

# import string
# import json
# import re
# import sys

# import codecs
import chardet


def get_encoding(filename):
    """
    获取给定文件的编码格式
    注意：文件编码在文件头的位置指明，因此只需要读取第一行就能做出判断
    :param filename: 指定目标文件的完整路径
    :return: string，指定文件的编码格式
    """
    encoding = None
    with open(filename, 'r') as f:
        line = f.readline()
        if len(line) > 100:
            line = line[:100]
        encoding = chardet.detect(line)['encoding']
    return encoding


if __name__ == '__main__':
    filename = '../l24z1xo4z0ln9ymd-21-ftp-banner-full_ipv4-20180129T023002-zgrab-results.json'
    print get_encoding(filename)
