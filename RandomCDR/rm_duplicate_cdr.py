#! python

import generate_random_cdr

# 根据需要替换下列field name
calling_number = generate_random_cdr.CDR.Calling_Number
called_number = generate_random_cdr.CDR.Called_Number
call_time = generate_random_cdr.CDR.Call_Time
duration = generate_random_cdr.CDR.Duration_SEC
cdr_type = generate_random_cdr.CDR.CDR_Type


def group_cdr(cdr_list, group_fields):
    """
    将通话记录按照*主被叫号码*进行分组
    :param cdr_list: list of dicts
        通话记录
    :return pp_to_cdr_list: dict
        分组后的通话记录
    """
    pp_to_cdr_list = {}  # key: phone pair, value: cdr_list
    for cdr in cdr_list:
        pp = (min(cdr[group_fields[0]], cdr[group_fields[1]]),
              max(cdr[group_fields[0]], cdr[group_fields[1]]))
        if pp not in pp_to_cdr_list:
            pp_to_cdr_list[pp] = []
        pp_to_cdr_list[pp].append(cdr)
    return pp_to_cdr_list


def sort_cdr(pp_to_cdr_list, sorted_field):
    """
    将每一对手机号码间的通话记录按照>sorted_field<指定的字段排序
    :param pp_to_cdr_list: dict
        按主被叫号码分组后的通话记录
    :param sorted_field:
        排序依据
    :return: None
        排序后的通话记录自动保存到 >pp_to_cdr_list<
    """
    for pp, cdr_list in pp_to_cdr_list.items():
        pp_to_cdr_list[pp] = sorted(cdr_list, key=lambda c: c[sorted_field])


def merge_cdr(cdr_to_keep, cdr_to_rm):
    # todo: 根据具体情况合并两条记录，将第二条记录的主叫数据加到第一条的被叫数据中，例如：
    # cdr_to_keep['Called_Cell_ID'] = cdr_to_rm['Calling_Cell_ID']
    return cdr_to_keep


def rm_dup_cdr_for_list(cdr_list):
    """
    对一个通话记录列表合并
    :param cdr_list: list of CDRs
        所有cdr对应同一对手机号码
    :return cdr_list: list of CDRs
        去重后的通话记录列表
    """
    num_cdr = len(cdr_list)
    for i in range(num_cdr):
        cdr_first = cdr_list[i]
        if not cdr_first:
            continue

        for j in range(i+1, num_cdr):
            cdr_second = cdr_list[j]
            if not cdr_second:
                continue

            # d = (cdr_second[call_time] - cdr_first[call_time]).seconds
            if (cdr_second[call_time] - cdr_first[call_time]).seconds <= cdr_first[duration]:
                # 两次通话时间上有重叠

                if cdr_first[calling_number] == cdr_second[called_number] and \
                        cdr_first[called_number] == cdr_second[calling_number]:
                    # 两次通话主被叫恰好相反

                    # 将主被叫号码颠倒的记录合并到正常的记录中，并保存为list的第i条数据
                    if cdr_first[cdr_type] in ['0', '6'] and cdr_second[cdr_type] in ['1', '7']:
                        cdr_list[i] = merge_cdr(cdr_to_keep=cdr_first, cdr_to_rm=cdr_second)
                        cdr_list[j] = None
                    elif cdr_first[cdr_type] in ['1', '7'] and cdr_second[cdr_type] in ['2', '6']:
                        cdr_list[i] = merge_cdr(cdr_to_keep=cdr_second, cdr_to_rm=cdr_first)
                        cdr_list[j] = None
                    else:
                        print('This should not happen - 1.')
                else:
                    print('This should not happen - 2.')
                break
            else:
                break
    cdr_list = list(filter(None, cdr_list))
    return cdr_list


def rm_dup_cdr(pp_to_cdr_list):
    """
    对每一对手机号码间的通话记录去重
    :param pp_to_cdr_list: dict
        按主被叫号码分组后的通话记录
    :return: None
        排序后的通话记录自动保存到 >pp_to_cdr_list<
    """
    for pp, cdr_list in pp_to_cdr_list.items():
        pp_to_cdr_list[pp] = rm_dup_cdr_for_list(cdr_list)


# 生成随机数据
cdr_graph = generate_random_cdr.init_cdr_graph()
data = generate_random_cdr.generate_duplicate_cdr_data(cdr_graph)

# 去重
pp_to_cdr_list = group_cdr(data, group_fields=(calling_number, called_number))
sort_cdr(pp_to_cdr_list, sorted_field=call_time)
rm_dup_cdr(pp_to_cdr_list)
pass