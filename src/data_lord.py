"""
这个模块是为了把模拟前所需要的数据导入到对应的MYSQL数据库，其中包括了一些导入所需的方法
"""

import time

import geopandas as gpd
import pandas as pd

import database
import datatype
import log_management

_name_ = 'data_lord'


def Lord(config):
    """
    模拟器所需数据的导入方法

    :param config:

    :return:
    """
    log_dir = config.get('LOG', 'dir_path')
    log = log_management.log_management(log_dir, _name_)
    log.write_tip(_name_)
    Lord_Cardata(config)
    Lord_Orderdata(config)
    Lord_Mapdata(config)
    ImprovingIndex(config)


def Lord_Cardata(config):
    operation_name = '车辆数据读入'
    time_list = [time.perf_counter()]

    Cardata_path = config.get('CACHE', 'cardata_path')
    car_data_table = config.get('MYSQL', 'car_data')
    log_dir = config.get('LOG', 'dir_path')
    log = log_management.log_management(log_dir, _name_)
    log.write_tip(operation_name, scale=2)

    df_cardata = pd.read_csv(Cardata_path)
    # 数据库连接
    engine = database.MySQLENGINE(config)
    df_cardata.to_sql(car_data_table, engine, if_exists='replace', index=False)
    # 新增一个空列
    conn = database.MySQLCONNECTION(config)
    cursor = conn.cursor()
    sql_alter = f"ALTER TABLE {car_data_table} ADD TASK_PATH JSON"
    cursor.execute(sql_alter)
    conn.commit()
    conn.close()

    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')
    log.write_data(f'数据库表名： {car_data_table}')


def Lord_Orderdata(config):
    operation_name = '订单数据读入'
    time_list = [time.perf_counter()]

    Orderdata_path = config.get('CACHE', 'orderdata_path')
    order_data_table = config.get('MYSQL', 'order_data')
    log_dir = config.get('LOG', 'dir_path')
    log = log_management.log_management(log_dir, _name_)
    log.write_tip(operation_name, scale=2)

    df_orderdata = pd.read_csv(Orderdata_path, encoding='utf-8')
    # 对初始订单数据进行处理

    # 数据库连接
    engine = database.MySQLENGINE(config)
    df_orderdata.to_sql(order_data_table, engine, if_exists='replace', index=False)

    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')
    log.write_data(f'数据库表名： {order_data_table}')


def Lord_Mapdata(config):
    operation_name = '地图数据读入'
    time_list = [time.perf_counter()]

    Mapdata_path = config.get('MAP', 'map_path')
    map_data_table = config.get('MYSQL', 'map_data')
    log_dir = config.get('LOG', 'dir_path')
    log = log_management.log_management(log_dir, _name_)
    log.write_tip(operation_name, scale=2)

    gdf_mapdata = gpd.read_file(Mapdata_path)
    df_mapdata = pd.DataFrame(gdf_mapdata)
    # 数据库连接
    engine = database.MySQLENGINE(config)
    df_mapdata.to_sql(map_data_table, engine, if_exists='replace', index=False)

    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')
    log.write_data(f'数据库表名： {map_data_table}')


def ImprovingIndex(config):
    operation_name = '优化索引'
    time_list = [time.perf_counter()]
    log_dir = config.get('LOG', 'dir_path')
    log = log_management.log_management(log_dir, _name_)
    innodb_buffer_pool_size = eval(config.get('MYSQL', 'innodb_buffer_pool_size'))
    log.write_tip(operation_name, scale=2)

    conn = database.MySQLCONNECTION(config)
    cursor = conn.cursor()
    # 查询缓冲区大小
    sql = "SHOW VARIABLES LIKE 'innodb_buffer_pool_size'"
    cursor.execute(sql)

    # 获取查询结果
    result = cursor.fetchone()
    buffer_pool_size = eval(result[1]) / (1024 * 1024)  # 获取缓冲区大小值(MB)

    # 设置缓冲区
    # 默认是128MB
    if buffer_pool_size != innodb_buffer_pool_size / (1024 * 1024):
        sql = f"SET GLOBAL innodb_buffer_pool_size = {innodb_buffer_pool_size}"
        cursor.execute(sql)
        conn.commit()
        time_list.append(time.perf_counter())
        log.write_data(
            f'已设置缓冲区大小为{innodb_buffer_pool_size / (1024 * 1024 * 1024):.2f} GB，前缓冲区大小为{buffer_pool_size:.2f} MB ')
    else:
        log.write_data(f'当前缓冲区大小为{buffer_pool_size / 1024 :.2f} GB，无需改变')

    # 为常用的列设置索引
    for table_name, cols in datatype.SQL_Index.items():
        if len(cols) == 0:
            continue
        else:
            for col in cols:
                sql = f"CREATE INDEX idx_{table_name}_{col} ON {table_name} ({col})"
                cursor.execute(sql)
    # 提交修改并关闭连接
    conn.commit()
    conn.close()

    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')


if __name__ == '__main__':
    import configparser

    config_file = r"config.ini"
    # 进行文件读取和参数判断的初始化
    config = configparser.ConfigParser()
    # READ CONFIG FILE
    config.read(config_file, encoding="utf-8")
    ImprovingIndex(config)
