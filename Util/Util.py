import os
from functools import wraps
import time


def read_to_list(filename):
    # 将文件读入到list中，每行对应一个元素
    data_list = []
    if not os.path.exists(filename):
        print('The file \"{0}\" does not exist.'.format(os.path.abspath(filename)))
    else:
        try:
            with open(filename, 'r') as f:
                data_list = f.readlines()
        except IOError:
            print('The file \"{0}\" is not readable.'.format(os.path.abspath(filename)))
        finally:
            # it's fine if IOError occurred in which case data_list = []
            data_list = [item.rstrip('\n').rstrip('\r').rstrip(' ') for item in data_list]
    return data_list


def list_to_str(data_list, sep=' '):
    """
    !!! 不再使用这个函数，用str.join() !!!
    将data_list的所有元素合并为一个string，用>sep<分隔
    要求输入data_list的每个元素都可以转化为string
    :param data_list:
    :param sep:
    :return:
    """
    data_list = [str(item) for item in data_list]
    return sep.join(data_list)


def write_list(data_list, filename, mode='w'):
    # 将list写入文件，每个元素对应一行
    # Each element occupy one line
    with open(filename, mode) as f:
        if data_list:
            f.write(data_list[0])
            for i in range(1, len(data_list)):
                f.write('\n' + data_list[i])


class CodeTimer(object):
    """
    用上下文管理器计时
    """
    def __init__(self):
        pass

    def __init__(self, processName):
        self.processName = processName
        pass

    def __enter__(self):
        try:
            print('\"{0}\" start >>>>'.format(self.processName))
        except Exception:
            pass
        self.t0 = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            print('\"{0}\" end <<<<'.format(self.processName))
        except Exception:
            pass
        print('>>>> TAKES time {time:.2f}sec <<<<'.format(time = time.time() - self.t0))
