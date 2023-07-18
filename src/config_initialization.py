import configparser
import os

import database

cache_file = {
    'cardata_path': 'cardata.csv',
    'orderdata_path': 'orderdata.csv',
    'Gdata_path': 'Gdata.pkl',
    'maplayer_path': 'maplayer.pkl',
}


def config_initialization():
    """
        对配置文件进行初始化
        1.修改配置文件中的绝对路径
        2.检查数据库连接
    :return:
    """
    config_file = r"config.ini"
    # 进行文件读取和参数判断的初始化
    config = configparser.ConfigParser()
    # READ CONFIG FILE
    config.read(config_file, encoding="utf-8")

    # ------------------------------------------------------------------------------------------
    # 修改文件目录
    # 获取上一级目录的路径
    parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 转化为当前目录下的其他文件
    config.set('DIR', 'main_path', os.path.normpath(parent_directory))

    # 日志
    log_dirpath = os.path.normpath(parent_directory + r'\log')
    if not os.path.exists(log_dirpath):
        # 创建文件夹
        os.makedirs(log_dirpath)
    config.set('LOG', 'dir_path', log_dirpath)

    # 缓存文件
    cache = config.get('DIR', 'cache_path')
    if not os.path.exists(os.path.normpath('\\'.join([parent_directory, cache]))):
        # 创建文件夹
        os.makedirs(os.path.normpath('\\'.join([parent_directory, cache])))
    for key, values in cache_file.items():
        new_file_path = os.path.normpath('\\'.join([parent_directory, cache, values]))
        config.set('CACHE', key, new_file_path)

    # 输出文件
    output = config.get('DIR', 'output')
    if not os.path.exists(os.path.normpath('\\'.join([parent_directory, output]))):
        # 创建文件夹
        os.makedirs(os.path.normpath('\\'.join([parent_directory, output])))
    map_name = os.path.basename(config.get('MAP', 'map_path'))
    map_png_name = os.path.splitext(map_name)[0] + '.png'
    map_out_path = '\\'.join([parent_directory, config.get('DIR', 'output'), map_png_name])
    map_out_path = os.path.normpath(map_out_path)
    config.set('OUTPUT', 'map_layer_output', map_out_path)
    fig_out_path = '\\'.join([parent_directory, config.get('DIR', 'output'), 'fig'])
    if not os.path.exists(fig_out_path):
        # 创建文件夹
        os.makedirs(fig_out_path)
    fig_out_path = os.path.normpath(fig_out_path) + '\\'
    config.set('OUTPUT', 'fig_output', fig_out_path)

    # ------------------------------------------------------------------------------------------
    # 创建数据库
    database.MySQLCONNECTION(config)

    # ------------------------------------------------------------------------------------------
    # 保存修改后的配置文件
    with open('config.ini', 'w+', encoding='utf-8') as configfile:
        config.write(configfile)


if __name__ == '__main__':
    config_initialization()
