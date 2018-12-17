# -*- coding: utf-8 -*-
from pymongo import MongoClient


def connect_mongo():
    return MongoClient(host=['10.42.0.96:27017', '10.42.0.99:27017'],
                       username='admin', password='admin',
                       replicaSet='csmd')


def pull_data(table_name, filter_query, proj_query=None):
    client = connect_mongo()
    db = client['csmd']
    if table_name not in db.list_collection_names():
        print('The collection does not exist, I will create a new one.')
        client.close()
        return False
    else:
        collection = db[table_name]
        if proj_query:
            crs = collection.find(filter_query, proj_query)
        else:
            crs = collection.find(filter_query)
        data_ret = [item for item in crs]
        client.close()
        return data_ret


if __name__ == '__main__':
    city_list = pull_data(table_name='tblR_CityInfo', filter_query={'country_zh': '印度'}, proj_query={'_id': False})
    print(city_list)