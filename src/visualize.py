import time

import matplotlib.pyplot as plt

import database
import log_management

_name_ = 'data_lord'

line_style = {
    'maxspeed': {
        50: {'color': '#2b4490', 'linewide': 3.5},
        40: {'color': '#0072E3', 'linewide': 2.2},
        35: {'color': '#ACD6FF', 'linewide': 2.2},
        0: {'color': '#B5B5B5', 'linewide': 1}
    }
}


def Creat_Layer(config):
    operation_name = '可视化画布生成'
    time_list = [time.perf_counter()]

    # 初始参数读入
    log_dir = config.get('LOG', 'dir_path')
    log = log_management.log_management(log_dir, _name_)
    log.write_tip(operation_name, scale=2)

    plt.rcParams['font.family'] = ['sans-serif']
    plt.rcParams['font.sans-serif'] = ['SimHei']
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 7), canvas='agg')
    plt.ion()  # 将画图模式改为交互模式，程序遇到plt.show不会暂停，而是继续执行
    plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置向内
    plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度线方向设置向内
    plt.axis('equal')  # x与y轴单位长度相同

    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')
    return fig, ax


def Mapdata_Layer(config, fig=None, ax=None):
    if fig is None and ax is None:
        fig, ax = Creat_Layer(config)

    operation_name = '地图数据图层生成'
    time_list = [time.perf_counter()]
    # 初始参数读入
    log_dir = config.get('LOG', 'dir_path')
    log = log_management.log_management(log_dir, _name_)
    log.write_tip(operation_name, scale=2)

    conn = database.MySQLCONNECTION(config)
    for key, values in line_style['maxspeed'].items():
        if key != 0:
            query = f"SELECT start_x, start_y, end_x, end_y FROM map_data WHERE maxspeed = {key}"
        else:
            maxspeed_values = [key for key in line_style['maxspeed'].keys() if key != 0]
            maxspeed_values_str = ', '.join(str(value) for value in maxspeed_values)
            query = f"SELECT start_x, start_y, end_x, end_y FROM map_data WHERE maxspeed NOT IN ({maxspeed_values_str})"

        cursor = conn._cursor_()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()

        start_x = [row[0] for row in result]
        start_y = [row[1] for row in result]
        end_x = [row[2] for row in result]
        end_y = [row[3] for row in result]
        ax.plot([start_x, end_x], [start_y, end_y],
                ls='-', lw=values['linewide'], alpha=1, zorder=1, c=values['color'],
                mfc='#EA6B55',
                mec=None,
                ms=2.5)

    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')
    return fig, ax


if __name__ == '__main__':
    import configparser

    config_file = r"config.ini"
    # 进行文件读取和参数判断的初始化
    config = configparser.ConfigParser()
    # READ CONFIG FILE
    config.read(config_file, encoding="utf-8")
    Mapdata_Layer(config)
