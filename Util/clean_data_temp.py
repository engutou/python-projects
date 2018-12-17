#! python
# -*- coding:utf-8 -*-
import Util


def extract_city_rank_list():
    filename = 'city_rank_India.txt'
    city_list = Util.read_to_list(filename)
    city_rank_list = []
    for c in city_list:
        items = c.split('\t')
        try:
            int(items[0])
            items[1] = items[1].split('[')[0]
            city_rank_list.append(','.join(items[0:2]))
        except ValueError:
            pass
    Util.write_list(city_rank_list, 'city_rank_India_ok.txt')


if __name__ == '__main__':
    extract_city_rank_list()