import pickle
import time

import database
import log_management
import simulation_relord
import simulation_run
import visualize

_name_ = 'Taxi_Simulation'


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

        # 检测加载绘图图层
        if int(self._config_.get('SWITCH', 'display')) == 1:
            with open(self._config_.get('CACHE', 'maplayer_path'), 'rb') as f:
                self._fig_, self._ax_ = pickle.load(f)  # 图网络数据
            self._vis_threads_ = []

        # 模拟器状态
        self._now_time_ = int(self._config_.get('PARAMETERS', 'now_time'))

    def Run(self):
        # 程序模拟总时间间隔
        run_times = int(self._config_.get('PARAMETERS', 'run_times'))
        unit_time = int(self._config_.get('PARAMETERS', 'unit_time'))
        time_list = [time.perf_counter()]
        # 按照时间间隔逐步迭代
        while self._now_time_ <= run_times:
            # 当前进度提醒
            tip = f"进度 {self._now_time_}/{self._config_.get('PARAMETERS', 'run_times')}"
            self._log_.write_tip(tip=tip, scale=2)

            # 乘客更新
            simulation_run.Customer_Appear(**self.__dict__)

            # 车辆寻客
            simulation_run.Customer_Destribution(**self.__dict__)

            # 模拟运行
            simulation_run.Vehicle_Operation(**self.__dict__)
            self._now_time_ += unit_time

            # 上下客人
            # 先计算下客车辆，否则其节点会保存
            simulation_run.Customer_Boarding(**self.__dict__)
            simulation_run.Customer_Arrival(**self.__dict__)

            # 绘图
            if int(self._config_.get('SWITCH', 'display')) == 1:
                visualize.Cardata_Layer(self._config_, self._now_time_,
                                        self._fig_, self._ax_,
                                        self._log_, self._cursor_)

            # 日志记录
            time_list.append(time.perf_counter())
            self._log_.pop_now_tip()
            self._log_.write_data(f'{tip} @ 耗时 {time_list[-1] - time_list[-2]:.2f}s')
        self._log_.write_data(f'模拟器共计耗时 {time_list[-1] - time_list[0]:.2f}s')

    def Relord(self):
        simulation_relord.Relord_Data(**self.__dict__)


if __name__ == '__main__':
    import configparser

    # import data_lord

    config_file = r"config.ini"
    # 进行文件读取和参数判断的初始化
    config = configparser.ConfigParser()
    # READ CONFIG FILE
    config.read(config_file, encoding="utf-8")
    # data_lord.Lord(config)
    obj = TaxiSimulation(config)
    obj.Relord()
    obj.Run()
