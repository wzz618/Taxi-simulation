import time

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
import database
import log_management

_name_ = 'visualize'

line_style = {
    'maxspeed': {
        50: {'color': '#2b4490', 'linewide': 3.5},
        40: {'color': '#0072E3', 'linewide': 2.2},
        35: {'color': '#ACD6FF', 'linewide': 2.2},
        0: {'color': '#B5B5B5', 'linewide': 1}
    }
}
# color pakette from:
# https://colors.muz.li/palette/e74645/fb7756/facd60/fdfa66/1ac0c6
car_style = {
    'CAR_STATE': {
        0: {'color': '#1ac0c6'},
        1: {'color': '#fdfa66'},
        2: {'color': '#facd60'},
        3: {'color': '#fb7756'},
        4: {'color': '#e74645'},
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
    plt.style.use('fast')
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 7), canvas='agg')
    plt.ion()  # 将画图模式改为交互模式，程序遇到plt.show不会暂停，而是继续执行
    # 但是效率比plt.show(block=False)低下
    plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置向内
    plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度线方向设置向内
    plt.axis('equal')  # x与y轴单位长度相同

    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')
    return fig, ax


def Mapdata_Layer(config, fig=None, ax=None, _cursor_=None):
    if fig is None and ax is None:
        fig, ax = Creat_Layer(config)
    if _cursor_ is None:
        conn = database.MySQLCONNECTION(config)
        cursor = conn.cursor()
    else:
        cursor = _cursor_
    operation_name = '地图数据图层生成'
    time_list = [time.perf_counter()]
    # 初始参数读入
    log_dir = config.get('LOG', 'dir_path')
    maptable = config.get('MYSQL', 'map_data')
    log = log_management.log_management(log_dir, _name_)
    log.write_tip(operation_name, scale=2)

    for key, values in line_style['maxspeed'].items():
        if key != 0:
            query = f"SELECT start_x, start_y, end_x, end_y FROM {maptable} WHERE maxspeed = {key}"
        else:
            maxspeed_values = [key for key in line_style['maxspeed'].keys() if key != 0]
            maxspeed_values_str = ', '.join(str(value) for value in maxspeed_values)
            query = f"SELECT start_x, start_y, end_x, end_y FROM map_data WHERE maxspeed NOT IN ({maxspeed_values_str})"

        cursor.execute(query)
        result = cursor.fetchall()

        start_x = [row[0] for row in result]
        start_y = [row[1] for row in result]
        end_x = [row[2] for row in result]
        end_y = [row[3] for row in result]
        ax.plot([start_x, end_x], [start_y, end_y],
                ls='-', lw=values['linewide'], alpha=1, zorder=1, c=values['color'],
                mfc='#EA6B55',
                mec=None,
                ms=2.5)

    if _cursor_ is None:
        cursor.close()

    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')
    return fig, ax


def Cardata_Layer(config, now_time=0, fig=None, ax=None, _log_=None, _cursor_=None):
    if fig is None and ax is None:
        fig, ax = Mapdata_Layer(config)
    if _cursor_ is None:
        conn = database.MySQLCONNECTION(config)
        cursor = conn.cursor()
    else:
        cursor = _cursor_
    if _log_ is None:
        log_dir = config.get('LOG', 'dir_path')
        log = log_management.log_management(log_dir, _name_)
    else:
        log = _log_
    operation_name = '车辆数据图层绘制'
    time_list = [time.perf_counter()]
    # 初始参数读入

    cartable = config.get('MYSQL', 'car_data')

    sql = f"SELECT LON, LAT, CAR_STATE FROM {cartable}"
    cursor.execute(sql)
    result = cursor.fetchall()

    on_lon = [row[0] for row in result]
    on_lat = [row[1] for row in result]
    colors = [car_style['CAR_STATE'][row[2]]['color'] for row in result]

    car_layer = ax.scatter(on_lon, on_lat, s=3, c=colors, alpha=0.5, zorder=2)

    if _cursor_ is None:
        cursor.close()

    if int(config.get('SWITCH', 'saveplay')) == 1:
        name = config.get('OUTPUT', 'fig_putput') + str(now_time) + '.jpg'
        plt.savefig(name, format='jpeg', dpi=300, bbox_inches='tight')
        time_list.append(time.perf_counter())
        time_dis_save = time_list[-1] - time_list[-2]

    if int(config.get('SWITCH', 'showplay')) == 1:
        # 刷新的速度
        # plt.pause(5)
        plt.show(block=False)
        time_list.append(time.perf_counter())
        time_dis_show = time_list[-1] - time_list[-2]
    # 移除图层保证清洁
    car_layer.remove()
    time_list.append(time.perf_counter())
    log.write_tip(operation_name, scale=3)
    log.write_data(f'当前时刻{now_time}')
    log.write_data(f'绘制图层耗时 {time_list[1] - time_list[0]:.2f} s')
    if int(config.get('SWITCH', 'showplay')) == 1:
        log.write_data(f'渲染展示耗时 {time_dis_show:.2f} s')
    if int(config.get('SWITCH', 'saveplay')) == 1:
        log.write_data(f'保存绘图耗时 {time_dis_save:.2f} s')
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[0]:.2f} s')
    log.pop_now_tip()
    return fig, ax, car_layer


if __name__ == '__main__':
    import configparser

    config_file = r"config.ini"
    # 进行文件读取和参数判断的初始化
    config = configparser.ConfigParser()
    # READ CONFIG FILE
    config.read(config_file, encoding="utf-8")
    fig, ax, carlayer = Cardata_Layer(config)
    fig.savefig('11.png')
