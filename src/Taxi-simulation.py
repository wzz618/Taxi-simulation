import pickle

import database
import log_management
import simulation_run

_name_ = 'Taxi-Simulation'


class TaxiSimulation:
    def __init__(self, config):
        # 进行配置文件读取和参数判断的初始化
        self._config_ = config
        # 进行日志文件的初始化
        self._log_ = log_management.log_management(self._config_.get('LOG', 'dir_path'), _name_)
        self._log_.write_tip(_name_)
        # 进行数据库的连接
        self._conn_ = database.MySQLCONNECTION(self._config_)
        self._cursor_ = self._conn_.cursor()

        # 加载图网络数据
        with open(self._config_.get('CACHE', 'Gdata_path'), 'rb') as f:
            self._G_ = pickle.load(f)  # 图网络数据

        # 模拟器状态
        self._now_time_ = 0

    def Run(self):
        # 程序模拟总时间间隔
        run_times = int(self._config_.get('PARAMETERS', 'run_times'))
        # 按照时间间隔逐步迭代
        while self._now_time_ < run_times:
            # 当前进度提醒
            tip = f"进度 {self._now_time_}/{self._config_.get('PARAMETERS', 'run_times')}"
            self._log_.write_tip(tip=tip, scale=3)

            # 乘客更新
            simulation_run.Customer_Appear(**self.__dict__)
            simulation_run.Customer_Boarding(**self.__dict__)

            # 车辆寻客
            simulation_run.Customer_Destribution(**self.__dict__)

            # 模拟运行

            # 更新状态
            self._now_time_ += 1


if __name__ == '__main__':
    import configparser

    config_file = r"config.ini"
    # 进行文件读取和参数判断的初始化
    config = configparser.ConfigParser()
    # READ CONFIG FILE
    config.read(config_file, encoding="utf-8")
    obj = TaxiSimulation(config)
    obj.Run()
