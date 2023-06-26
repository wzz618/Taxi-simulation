import configparser
import os

import database

config_file = r"config.ini"
# 进行文件读取和参数判断的初始化
config = configparser.ConfigParser()
# READ CONFIG FILE
config.read(config_file, encoding="utf-8")


# # READ LOG FILE
# log = log_management.log_management(config['LOG']['log_dir'], 'orderData')
# log.write_tip('地图地理数据')


def config_initialization():
    """
        对配置文件进行初始化
        1.修改配置文件中的绝对路径
        2.检查数据库连接
    :return:
    """
    # ------------------------------------------------------------------------------------------
    # 修改文件目录
    # 获取上一级目录的路径
    parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config.set('DIR', 'main_path', parent_directory)
    config.set('LOG', 'dir_path', os.path.normpath(parent_directory + r'\log'))

    # ------------------------------------------------------------------------------------------
    # 创建数据库
    database.MySQLCONNECTION(config)

    # ------------------------------------------------------------------------------------------
    # 保存修改后的配置文件
    with open('config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)


if __name__ == '__main__':
    config_initialization()
