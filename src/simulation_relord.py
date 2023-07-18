"""
该模块主要是把运行后中断的数据，进行重新加载。
"""

import time

import simulation_G


def Relord_Data(**kwargs):
    """

    """
    log = kwargs['_log_']

    operation_name = '数据重加载'
    log.write_tip(tip=operation_name, scale=2)
    time_list = [time.perf_counter()]

    # 需要重新加载的数据
    Relord_G(**kwargs)

    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，共计耗时 {time_list[-1] - time_list[0]:.2f} s')
    log.pop_now_tip()


def Relord_G(**kwargs):
    """
    在道路G数据上，重新加载乘客和车辆的点
    """
    cartable = kwargs['_config_'].get('MYSQL', 'car_data')
    ordertable = kwargs['_config_'].get('MYSQL', 'order_data')
    log = kwargs['_log_']
    cursor = kwargs['_cursor_']
    prefix_car = kwargs['_config_'].get('G', 'prefix_car')
    prefix_cus_O = kwargs['_config_'].get('G', 'prefix_cus_O')
    prefix_cus_D = kwargs['_config_'].get('G', 'prefix_cus_D')

    operation_name = '图数据重加载'
    log.write_tip(tip=operation_name, scale=3)
    time_list = [time.perf_counter()]

    # 寻找需要乘车的乘客
    # 之所以全部都加，是因为不知道哪个会炸雷，之前每个状态都炸雷一次
    sql = f"SELECT CUS_ID, ON_FIR_PT_N, ON_LST_PT_N, ON_LON, ON_LAT FROM {ordertable} " \
          f"WHERE CUS_STATE IN (1, 2, 3, 4)"
    cursor.execute(sql)
    cus = cursor.fetchall()
    # 如果乘车乘客不为0，则添加乘客信息
    if cus:
        simulation_G.Updata_G_nodes(nodes_data=cus, nodes_notes=prefix_cus_O, **kwargs)
    time_list.append(time.perf_counter())
    log.write_data(f'打车(1)/等车(2)/导航(3)/下车(4)乘客O点添加完成，数量 {len(cus)} ，耗时 {time_list[-1] - time_list[-2]:.2f}')

    # 需要上车，但还没指路的乘客
    sql = f"SELECT CUS_ID, OFF_FIR_PT_N, OFF_LST_PT_N, OFF_LON, OFF_LAT FROM {ordertable} " \
          f"WHERE CUS_STATE = 3"
    cursor.execute(sql)
    cus = cursor.fetchall()
    # 如果乘车乘客不为0，则添加乘客信息
    if cus:
        simulation_G.Updata_G_nodes(nodes_data=cus, nodes_notes=prefix_cus_D, **kwargs)
    time_list.append(time.perf_counter())
    log.write_data(f'导航乘客D点添加完成，数量 {len(cus)} ，耗时 {time_list[-1] - time_list[-2]:.2f}')

    # 空车
    sql = f"SELECT CAR_ID, FIR_PT_N, LST_PT_N, LON, LAT FROM {cartable} WHERE CAR_STATE = 0"
    cursor.execute(sql)
    car = cursor.fetchall()
    simulation_G.Updata_G_nodes(nodes_data=car, nodes_notes=prefix_car, **kwargs)
    time_list.append(time.perf_counter())

    log.write_data(f'空车车辆位置添加完成，数量 {len(cus)} ，耗时 {time_list[-1] - time_list[-2]:.2f}')
    log.write_data(f'{operation_name}完成，共计耗时 {time_list[-1] - time_list[0]:.2f} s')
    log.pop_now_tip()
