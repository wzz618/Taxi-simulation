import configparser
import pickle
import time

# import data_lord

config_file = r"config.ini"
# 进行文件读取和参数判断的初始化
config = configparser.ConfigParser()
# READ CONFIG FILE
config.read(config_file, encoding="utf-8")
time_list = [time.perf_counter()]
with open(config.get('CACHE', 'maplayer_path'), 'rb') as f:
    fig, ax = pickle.load(f)  # 图网络数据
time_list.append(time.perf_counter())
print(f'耗时 {time_list[-1] - time_list[-2]:.2f} s')
