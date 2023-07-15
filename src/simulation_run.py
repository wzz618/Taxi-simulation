import time

import datatype
import simulation_G

_name_ = 'simulation_run'


def Customer_Appear(**kwargs):
    """
        从orderdata中检索当前时间出现的新乘客，如果有则更新orderdata，模拟器的G
    :param kwargs:
    :return:
    """
    operation_name = '出现乘客数据更新'
    time_list = [time.perf_counter()]
    ordertable = kwargs['_config_'].get('MYSQL', 'order_data')
    prefix_cus_O = kwargs['_config_'].get('G', 'prefix_cus_O')
    unit_time = int(kwargs['_config_'].get('PARAMETERS', 'unit_time'))
    log = kwargs['_log_']
    conn = kwargs['_conn_']
    cursor = kwargs['_cursor_']
    now_time = kwargs['_now_time_']

    # 执行更新语句
    sql = f"UPDATE {ordertable} SET CUS_STATE = 1 WHERE APPEARANCE_TIME <= {now_time} AND APPEARANCE_TIME > {now_time - unit_time}"
    cursor.execute(sql)
    # 提交更改
    conn.commit()
    # 寻找需要乘车的乘客
    sql = f"SELECT CUS_ID, ON_FIR_PT_N, ON_LST_PT_N, ON_LON, ON_LAT FROM {ordertable} WHERE CUS_STATE = 1"
    cursor.execute(sql)
    cus = cursor.fetchall()
    # 如果乘车乘客不为0，则添加乘客信息
    if cus:
        simulation_G.Updata_G_nodes(nodes_data=cus, nodes_notes=prefix_cus_O, **kwargs)
    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，乘客出现人数{len(cus)}， 耗时 {time_list[-1] - time_list[-2]:.2f} s')


def Customer_Boarding(**kwargs):
    """
        乘客上车，并且告诉司机D点，司机进行路径规划
        对模拟器中的乘客进行车辆分配
        :param kwargs:
        :return:
        """
    operation_name = '乘客上车数据更新'
    time_list = [time.perf_counter()]
    G = kwargs['_G_']
    now_time = kwargs['_now_time_']
    log = kwargs['_log_']
    conn = kwargs['_conn_']
    cursor = kwargs['_cursor_']
    ordertable = kwargs['_config_'].get('MYSQL', 'order_data')
    cartable = kwargs['_config_'].get('MYSQL', 'car_data')
    prefix_cus_O = kwargs['_config_'].get('G', 'prefix_cus_O')
    prefix_cus_D = kwargs['_config_'].get('G', 'prefix_cus_D')
    weight_limit = float(kwargs['_config_'].get('PARAMETERS', 'search_length'))
    # CAR_ID, LON, LAT
    sql = f"SELECT TASK_CUS_ID FROM {cartable} WHERE CAR_STATE = 3"
    cursor.execute(sql)
    cus_ids = cursor.fetchall()
    if cus_ids:
        # 结果非空
        # 提取 cus_ids 的值
        cus_id_values = [row[0] for row in cus_ids]

        # 构建参数化查询语句
        sql = f"SELECT CUS_ID, OFF_FIR_PT_N, OFF_LST_PT_N, OFF_LON, OFF_LAT, CAR_ID FROM {ordertable} WHERE CUS_ID IN ({', '.join(['%s'] * len(cus_id_values))})"
        cursor.execute(sql, cus_id_values)
        cus_data = cursor.fetchall()
        cus = tuple(tuple(item[:-1]) for item in cus_data)
        # 如果有乘客可以登车则进行登车
        update_cus_values = []
        update_car_values = []
        for row in cus_data:
            # 把乘客目的地输入到图数据中
            cus_id = row[0]
            car_id = row[5]
            cus_id_G_O = prefix_cus_O + cus_id
            car_id_G_D = prefix_cus_D + row[5]
            simulation_G.Updata_G_nodes(nodes_data=cus, nodes_notes=prefix_cus_D, **kwargs)
            length, task_path = simulation_G.Get_Shortest_Car_To_Cus_Path(
                G=G,
                car_names=[cus_id_G_O],  # 符合条件的车辆编号们
                cus_name=car_id_G_D,  # 目标乘客 cusa_name
                weight='shape_len',  # 计算最短路径的权重名称，有三类（weight， shape_len， wgs84_length）
                weight_limit=weight_limit,  # 计算最短路径的权重名称，有三类（weight， shape_len， wgs84_length）
                **kwargs
            )
            # 有效载客距离
            _, task_pmtd = task_path['shape_len'][-1]
            _, task_time = task_path['time_len'][-1]
            # 元组形式更新
            # mysql table: orderdata cols
            # CUS_STATE, GET_ON_TIME, DH_MILEAGE, CUS_ID
            update_cus_values.append((3, now_time, task_pmtd, cus_id))
            # mysql table: cardata cols
            # CAR_STATE, TASK_PMTD, TASK_GET_ON_TIME, GET_OFF_TIME,TASK_PATH_ID, TASK_PATH, CAR_ID
            update_car_values.append((2, task_pmtd, now_time, now_time + task_time, 0, task_path, car_id))
        # orderdata
        sql_update = f"UPDATE {ordertable} SET CUS_STATE = %s, GET_ON_TIME = %s, GET_OFF_TIME = %s, PMTD = %s WHERE CUS_ID = %s"
        cursor.executemany(sql_update, update_cus_values)
        conn.commit()
        # cardata
        sql_update = f"UPDATE {cartable} SET CAR_STATE = %s, TASK_PMTD = %s, TASK_GET_ON_TIME = %s, " \
                     f"TASK_PATH_ID = %s, TASK_PATH = %s WHERE CAR_ID = %s"
        cursor.executemany(sql_update, update_car_values)
        conn.commit()
    else:
        pass
    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，乘客上车人数{len(cus_ids)}， 耗时 {time_list[-1] - time_list[-2]:.2f} s')


def Customer_Arrival(**kwargs):
    """
        乘客抵达目的地，结算当前订单
        对模拟器中的到达乘客的订单数据进行修改，对车辆的数据继续修改
    :param kwargs:
    :return:
    """
    operation_name = '乘客下车数据更新'
    time_list = [time.perf_counter()]
    G = kwargs['_G_']
    now_time = kwargs['_now_time_']
    log = kwargs['_log_']
    conn = kwargs['_conn_']
    cursor = kwargs['_cursor_']
    ordertable = kwargs['_config_'].get('MYSQL', 'order_data')
    cartable = kwargs['_config_'].get('MYSQL', 'car_data')

    # 构建参数化查询语句
    # orderdata_table:
    # TASK_CUS_ID, TASK_ALL_MILEAGE, TASK_PMTD, TASK_DH_MILEAGE, TASK_NOW_MILEAGE
    # TASK_ACCEPTANCE_TIME, TASK_GET_ON_TIME
    sql = f"""SELECT TASK_CUS_ID, TASK_PMTD, TASK_DH_MILEAGE, LOG_TIME FROM {cartable} WHERE CAR_STATE = 4"""
    cursor.execute(sql)
    car_records = cursor.fetchall()
    if car_records:
        # 结果非空

        # 参数化查询语句
        # orderdata_table:
        # CUS_STATE, APPEARANCE_TIME, ACCEPTANCE_TIME, GET_ON_TIME, GET_OFF_TIME, DH_MILEAGE, PMTD
        # TASK_ACCEPTANCE_TIME, TASK_GET_ON_TIME
        update_cus_values = []
        for row in car_records:
            # 把乘客目的地输入到图数据中
            cus_id = row[0]
            pmtd = row[1]
            dh_mileage = row[2]
            log_time = row[3]

            # 元组形式更新
            # mysql table: orderdata cols
            # CUS_STATE, GET_OFF_TIME, DH_MILEAGE, PMTD, CUS_ID
            update_cus_values.append((4, log_time, dh_mileage, pmtd, cus_id))
        # orderdata
        sql_update = f"UPDATE {ordertable} " \
                     f"SET CUS_STATE = %s, GET_OFF_TIME = %s, DH_MILEAGE = %s, PMTD = %s " \
                     f"WHERE CUS_ID = %s"
        cursor.executemany(sql_update, update_cus_values)
        conn.commit()
        # cardata
        # CAR_STATE, TASK_CUS_ID, TASK_ALL_MILEAGE,
        # TASK_PMTD, TASK_DH_MILEAGE, TASK_NOW_MILEAGE
        # TASK_ACCEPTANCE_TIME, TASK_GET_ON_TIME, TASK_GET_OFF_TIME, TASK_PATH_ID, TASK_PATH
        sql_update = f"""
                    UPDATE {cartable} 
                    SET CAR_STATE = 0, TASK_CUS_ID=0, TASK_ALL_MILEAGE = 0, 
                        TASK_PMTD = 0, TASK_DH_MILEAGE=0, TASK_NOW_MILEAGE = 0, 
                        TASK_ACCEPTANCE_TIME = 0, TASK_GET_ON_TIME=0, TASK_GET_OFF_TIME = 0, 
                        TASK_PATH_ID = 0, TASK_GET_OFF_TIME = NULL 
                    WHERE CAR_STATE = 4
                """
        cursor.execute(sql_update)
        conn.commit()
    else:
        pass
    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，乘客下车人数{len(car_records)}， 耗时 {time_list[-1] - time_list[-2]:.2f} s')


def Customer_Destribution(**kwargs):
    """
    判断当前下需要乘车的乘客，以及等待分配的空车
    对模拟器中的乘客进行车辆分配
    :param kwargs:
    :return:
    """
    operation_name = '司机接单数据更新'
    time_list = [time.perf_counter()]
    G = kwargs['_G_']
    now_time = kwargs['_now_time_']
    log = kwargs['_log_']
    conn = kwargs['_conn_']
    cursor = kwargs['_cursor_']
    ordertable = kwargs['_config_'].get('MYSQL', 'order_data')
    cartable = kwargs['_config_'].get('MYSQL', 'car_data')
    prefix_car = kwargs['_config_'].get('G', 'prefix_car')
    prefix_cus_O = kwargs['_config_'].get('G', 'prefix_cus_O')
    weight_limit = float(kwargs['_config_'].get('PARAMETERS', 'search_length'))

    # 等待更新的数据初始化
    update_car_values = []
    update_cus_values = []
    # 查询当前的等待乘客
    sql = f"SELECT CUS_ID FROM {ordertable} WHERE CUS_STATE = 1"
    cursor.execute(sql)
    cus_ids = cursor.fetchall()
    # 当前空余的车辆
    # 如果当前为初始状态，则初始话G中的车辆
    if now_time == 0:
        sql = f"SELECT CAR_ID, FIR_PT_N, LST_PT_N, LON, LAT FROM {cartable} WHERE CAR_STATE = 0"
        cursor.execute(sql)
        car = cursor.fetchall()
        simulation_G.Updata_G_nodes(nodes_data=car, nodes_notes=prefix_car, **kwargs)
    sql = f"SELECT CAR_ID FROM {cartable} WHERE CAR_STATE = 0"
    cursor.execute(sql)
    car_ids = cursor.fetchall()
    car_ids_G = [prefix_car + str(car_id) for car_id in car_ids]
    # 如果有乘客并且有空车则进行分配
    while len(cus_ids) != 0 and len(car_ids_G) != 0:
        # 对每一位乘客分配车辆
        for cus_id in cus_ids:
            cus_id_G = prefix_cus_O + str(cus_id)
            length, task_path = simulation_G.Get_Shortest_Car_To_Cus_Path(
                G=G,
                car_names=car_ids_G,  # 符合条件的车辆编号们
                cus_name=cus_id_G,  # 目标乘客 cusa_name
                weight='shape_len',  # 计算最短路径的权重名称，有三类（weight， shape_len， wgs84_length）
                weight_limit=weight_limit,  # 计算最短路径的权重名称，有三类（weight， shape_len， wgs84_length）
                **kwargs
            )
            # 如果距离该乘客的最近距离超过weight_limit，则意味着该乘客无人可接
            if length is None:
                cus_ids.pop(cus_id)
                continue
            else:
                # 如果不是则更新车辆的形式距离task_path
                car_id_G, task_dh_mileage = task_path['shape_len'][-1]
                car_id = int(car_id_G.replace(prefix_car, ''))  # 从图中提出车辆的序列号
                # 元组形式更新
                # mysql table: orderdata cols
                # CAR_ID , US_STATE, ACCEPTANCE_TIME, DH_MILEAGE, CUS_ID
                update_cus_values.append((car_id, 2, now_time, task_dh_mileage, cus_id))
                # mysql table: cardata cols
                # CAR_STATE, TASK_CUS_ID, TASK_DH_MILEAGE, TASK_ACCEPTANCE_TIME, TASK_PATH_ID, TASK_PATH, CAR_ID
                update_car_values.append((1, cus_id, task_dh_mileage, now_time, 0, task_path, car_id))
                car_ids_G.pop(car_id_G)
                cus_ids.pop(cus_id)
    # 如果存在可以更新的数据：
    if len(update_cus_values) != 0:
        # orderdata
        sql_update = f"UPDATE {ordertable} SET CAR_ID = %s, CUS_STATE = %s, ACCEPTANCE_TIME = %s, DH_MILEAGE = %s WHERE CUS_ID = %s"
        cursor.executemany(sql_update, update_cus_values)
        conn.commit()
        # cardata
        sql_update = f"UPDATE {cartable} SET CAR_STATE = %s, TASK_CUS_ID = %s, TASK_DH_MILEAGE = %s, " \
                     f"TASK_ACCEPTANCE_TIME = %s, TASK_PATH_ID = %s, TASK_PATH = %s WHERE CAR_ID = %s"
        cursor.executemany(sql_update, update_car_values)
        conn.commit()
    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，乘客人数{len(update_cus_values)}， 耗时 {time_list[-1] - time_list[-2]:.2f} s')


def Vehicle_Operation(**kwargs):
    """
        对当前数据库中运行车辆进行数据更新
        |---------------runtime-------------->
        |-nowtime-|---------unit_time--------|
        |-nowtime-|-used_time-|-unused_time--|
        计算完后更新
    :param kwargs:
    :return:
    """
    operation_name = '模拟器车辆运行'
    time_list = [time.perf_counter()]
    G = kwargs['_G_']
    now_time = kwargs['_now_time_']
    log = kwargs['_log_']
    conn = kwargs['_conn_']
    cursor = kwargs['_cursor_']
    cartable = kwargs['_config_'].get('MYSQL', 'car_data')
    unit_time = kwargs['_config_'].get('PARAMETERS', 'unit_time')

    # 更新驶向乘客所在地的车辆信息，如果车辆到达则更新信息
    # CAR_ID, LON, LAT, FIR_PT_N, LST_PT_N, TASK_GET_ON_TIME, TASK_PATH_ID, TASK_PATH
    cols = ['CAR_ID', 'LON', 'LAT',
            'FIR_PT_N', 'LST_PT_N',
            'TASK_ACCEPTANCE_TIME', 'TASK_GET_ON_TIME', 'TASK_PATH_ID', 'TASK_PATH']
    car_states = [1, 2]
    # 三种车辆状态
    # 因为车辆数据相对较少，采用分步查询能够降低内存使用，增加重复查询时间忽略不计算
    for car_state in car_states:
        sql = f"SELECT {', '.join(cols)} FROM {cartable} WHERE CAR_STATE = {car_state}"
        cursor.execute(sql)
        car_records = cursor.fetchall()
        # 仅仅只需要更新坐标的车辆数据信息
        car_records_updata_loc = []
        # 还需要更新所在道路的车辆数据信息
        car_records_updata_road = []
        # 获得了新任务的车辆数据信息
        car_records_updata_task = []
        for row in car_records:
            # 信息解析
            car_id = row[0]  # CAR_ID
            fir_pt_n = row[3]
            lst_pt_n = row[4]
            if car_state == 1:
                runtime = now_time + unit_time - row[5]
            else:
                runtime = now_time + unit_time - row[6]
            task_path_id = row[7]
            task_path = row[8]
            # 更新车辆位置
            # 到达路径终点位置所需时间，必须转化为整型，因为最小计量单位为s
            # Estimated Time of Arrival
            # 如果不是第一段路(O -> nodes1)
            # 最后一个任务的序号
            task_path_id_end = len(task_path['path']) - 1
            new_task_path_id = task_path_id
            # 本次车辆运行的所剩时间、距离、耗时
            travel = {
                'unused_time': unit_time,
                'dis': 0,
                'time': 0
            }
            while new_task_path_id < task_path_id_end:
                # 如果不是最后一段路(noden -> D)
                # 则说明当前是OD中间的道路节点
                new_task_path_id += 1
                # 抵达下一段路口(nodes)必须行驶的总时间为eta
                # Estimated Time of Arrival
                eta1 = task_path['time_len'][new_task_path_id - 1]
                eta2 = task_path['time_len'][new_task_path_id]
                # 完成该段道路的移动所需时间为move_time
                required_time_of_path = eta2 - eta1
                if runtime < eta2:
                    """车辆未更新道路
                    如果小于该段路的行驶总时间，则意味着车辆还在任务路径上
                    radio意味着node1 -> new_car_loc占据node1 -> node2的比例
                    时间关系如下:
                        O--------->node1----->car------------>node2
                        O---eta1--|--required_time_of_path---|
                        O--------------eta2------------------|
                    剩余时间/该段时间 = 比例
                    """
                    #
                    radio = travel['unused_time'] / required_time_of_path
                    # 移动的多少
                    travel['time'] += travel['unused_time']
                    travel['dis'] += travel['unused_time'] / required_time_of_path * (
                            task_path['shape_len'][new_task_path_id] - task_path['shape_len'][new_task_path_id - 1])
                    # 如果当前时间小于行驶到路口的总时间，则意味着在该道路中间
                    # 判断当前车辆是否更换道路
                    # node1 -> car_new_loc -> node2
                    if new_task_path_id == task_path_id + 1:
                        # node1 -> car_old_loc -> car_new_loc -> node2
                        # 如果的路径id没有变，则说明该车辆未变更道路
                        # 意味着只需要更新车辆的位置即car_records_updata_loc
                        if new_task_path_id == 1:
                            # 意味着第一个点刚刚好是O点
                            fir_loc = task_path['OD_loc'][0]
                        else:
                            # 否则意味着第一个点和车辆的第一个点一样
                            fir_node = G.nodes[fir_pt_n]
                            fir_loc = [fir_node['x'], fir_node['y']]
                        if new_task_path_id == task_path_id_end:
                            # 意味着最后一个点刚刚好是坐标
                            # car_new_loc -> D
                            lst_loc = task_path['OD_loc'][-1]
                        else:
                            # 略
                            lst_nodes = G.nodes[lst_pt_n]
                            lst_loc = [lst_nodes['x'], lst_nodes['y']]
                        # 计算更新后的坐标
                        new_lon, new_lat = simulation_G.Get_middle_nodes_location(fir_loc=fir_loc, lst_loc=lst_loc,
                                                                                  radio=radio)
                        if car_state == 1:
                            # (+)意味着在原有数值上面更改，否则是替换
                            # LON, LAT, LOG_TIME,
                            # ALL_RUN_MILEAGE(+), ALL_DH_MILEAGE_P(+), ALL_RUN_TIME(+),
                            # ALL_DH_TIME_P(+), TASK_ALL_MILEAGE(+), TASK_DH_MILEAGE(+), TASK_NOW_MILEAGE(+),
                            # CAR_ID
                            new_data = (new_lon, new_lat, now_time + unit_time,
                                        travel['dis'], travel['dis'], travel['time'],
                                        travel['time'], travel['dis'], travel['dis'], travel['dis'],
                                        car_id)
                        else:
                            # LON, LAT, LOG_TIME,
                            # ALL_RUN_MILEAGE(+), ALL_PMTD(+), ALL_RUN_TIME(+),
                            # TASK_ALL_MILEAGE(+), TASK_PMTD(+), TASK_NOW_MILEAGE(+),
                            # CAR_ID
                            new_data = (new_lon, new_lat, now_time + unit_time,
                                        travel['dis'], travel['dis'], travel['time'],
                                        travel['dis'], travel['dis'], travel['dis'],
                                        car_id)
                        car_records_updata_loc.append(new_data)
                        # 更新完成，结束循环
                        break
                    else:
                        # 否则意味着该车辆变更了道路
                        # car_old_loc -> node1 -> ... ->car_new_loc -> noden
                        # 此时car_new_loc的第一个点始终是道路上面的点
                        if new_task_path_id == task_path_id_end:
                            # 意味着最后一个点刚刚好是D点（临时点）
                            lst_loc = task_path['OD_loc'][1]
                            # 意味着进入到最后一条道路
                            # 由于最后一条道路的终点是临时点（非地图上的道路节点），所以需要找到真实的道路节点
                            # 临时节点和道路节点有且仅有两个节点连接
                            # car_new_loc -> D -> lst_node
                            lst_node = task_path['OD_neighbors'][-1][-1]
                        else:
                            # 意味着刚刚好是道路上的点（恒定点）
                            lst_node_name = task_path['path'][new_task_path_id]
                            lst_node = G.nodes[lst_node_name]
                            lst_loc = [lst_node['x'], lst_node['y']]
                        fir_node_name = task_path['path'][new_task_path_id - 1]
                        fir_node = G.nodes[fir_node_name]
                        fir_loc = [fir_node['x'], fir_node['y']]
                        # 计算新的坐标
                        new_lon, new_lat = simulation_G.Get_middle_nodes_location(fir_loc=fir_loc, lst_loc=lst_loc,
                                                                                  radio=radio)
                        # LON, LAT, FIR_PT_N, LST_PT_N,
                        if car_state == 1:
                            # (+)意味着在原有数值上面更改，否则是替换
                            # FIR_PT_N, LST_PT_N
                            # LON, LAT, LOG_TIME,
                            # ALL_RUN_MILEAGE(+), ALL_DH_MILEAGE_P(+), ALL_RUN_TIME(+),
                            # ALL_DH_TIME_P(+), TASK_ALL_MILEAGE(+), TASK_DH_MILEAGE(+), TASK_NOW_MILEAGE(+),
                            # TASK_PATH_ID, CAR_ID
                            new_data = (fir_node, lst_node,
                                        new_lon, new_lat, now_time + unit_time,
                                        travel['dis'], travel['dis'], travel['time'],
                                        travel['time'], travel['dis'], travel['dis'], travel['dis'],
                                        new_task_path_id - 1, car_id)
                        else:
                            # FIR_PT_N, LST_PT_N
                            # LON, LAT, LOG_TIME, ALL_RUN_MILEAGE(+), ALL_PMTD(+), ALL_RUN_TIME(+),
                            # TASK_ALL_MILEAGE(+), TASK_PMTD(+), TASK_NOW_MILEAGE(+),
                            # TASK_PATH_ID, CAR_ID
                            new_data = (fir_node, lst_node,
                                        new_lon, new_lat, now_time + unit_time,
                                        travel['dis'], travel['dis'], travel['time'],
                                        travel['dis'], travel['dis'], travel['dis'],
                                        new_task_path_id - 1, car_id)
                        car_records_updata_road.append(new_data)
                        # 更新完成，结束循环
                        break
                else:
                    """
                    意味着此时车辆已经驶过路段节点
                    时间关系如下
                        O--------------runtime--------------->car(new)
                        O---->car(old)---->node1------------->car(new)
                        O-------eta2------|
                        O----|---------unused_time-----------|
                        O----|-used_time--|
                    """
                    used_time = eta2 - (runtime - travel['unused_time'])
                    #  如果大于等于该段路的行驶总时间，则意味着车辆离开该段路
                    if new_task_path_id == task_path_id_end:
                        # 如果此时刚刚好处于最后一个路径，则意味着车辆已经抵达目的地
                        radio = used_time / required_time_of_path
                        travel['unused_time'] -= used_time
                        # 移动的多少
                        travel['time'] += used_time
                        travel['dis'] += radio * (task_path['shape_len'][new_task_path_id] -
                                                  task_path['shape_len'][new_task_path_id - 1])
                        x = task_path['OD_loc'][-1][0]
                        y = task_path['OD_loc'][-1][1]
                        fir_node = task_path['OD_neighbors'][-1][0]
                        lst_node = task_path['OD_neighbors'][-1][1]
                        # 如果当前时间小于行驶到路口的总时间，则意味着在该道路中间
                        # 判断当前车辆是否更换道路
                        if car_state == 1:
                            # (+)意味着在原有数值上面更改，否则是替换
                            # 意味着此时车辆抵达的目的地是乘客所在地
                            # cardata:
                            # CAR_STATE, LON, LAT,
                            # FIR_PT_N, LST_PT_N, LOG_TIME,
                            # ALL_RUN_MILEAGE(+), ALL_DH_MILEAGE_P(+),
                            # ALL_RUN_TIME(+), ALL_DH_TIME_P(+),
                            # TASK_ALL_MILEAGE(+), TASK_DH_MILEAGE(+), TASK_NOW_MILEAGE(+)
                            # CAR_ID
                            new_data = (3, x, y,
                                        fir_node, lst_node, now_time + travel['time'],
                                        travel['dis'], travel['dis'],
                                        travel['time'], travel['time'],
                                        travel['dis'], travel['dis'], travel['dis'],
                                        car_id)
                            # 此时循环结束，弹出
                        else:
                            # 意味着此时车辆抵达了乘客目的地
                            # car_data
                            # CAR_STATE， LON, LAT,
                            # FIR_PT_N, LST_PT_N, LOG_TIME,
                            # ALL_RUN_MILEAGE(+), ALL_PMTD(+),
                            # ALL_RUN_TIME(+), TASK_ALL_MILEAGE(+),
                            # TASK_PMTD(+), TASK_NOW_MILEAGE(+)
                            # CAR_ID
                            new_data = (4, x, y,
                                        fir_node, lst_node, now_time + travel['time'],
                                        travel['dis'], travel['dis'],
                                        travel['time'], travel['dis'],
                                        travel['dis'], travel['dis'],
                                        car_id)
                        car_records_updata_task.append(new_data)
                        break
                    else:
                        # 意味着此时车辆达到了任务路径的下一段道路
                        pass
        # 更新位置
        sql = datatype.sql_vehicle_operation(cartable, 'updata_loc', car_state)
        cursor.executemany(sql, car_records_updata_loc)
        conn.commit()
        # 更新道路
        sql = datatype.sql_vehicle_operation(cartable, 'updata_road', car_state)
        cursor.executemany(sql, car_records_updata_road)
        conn.commit()
        # 更新任务
        sql = datatype.sql_vehicle_operation(cartable, 'updata_task', car_state)
        cursor.executemany(sql, car_records_updata_task)
        conn.commit()
    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')
