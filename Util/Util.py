import os


def read_to_list(filename):
    # 将文件读入到list中，每行对应一个元素
    data_list = []
    if not os.path.exists(filename):
        print('The file \"{0}\" does not exist.'.format(os.path.abspath(filename)))
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
    # 将data_list的所有元素合并为一个string，用>sep<分隔
    # 要求输入data_list的每个元素都可以转化为string
    if data_list:
        ret = ''
        for d in data_list:
            ret += (str(d) + sep)
        return ret.rstrip(sep)
    else:
        return ''


def write_list(data_list, filename, mode='w'):
    # 将list写入文件，每个元素对应一行
    # Each element occupy one line
    with open(filename, mode) as f:
        if data_list:
            f.write(data_list[0])
            for i in range(1, len(data_list)):
                f.write('\n' + data_list[i])
