import time

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
    sql = f"UPDATE {ordertable} SET CUS_STATE = 1 WHERE APPEARANCE_TIME <= {now_time} AND APPEARANCE_TIME > {now_time - unit_time} AND"
    cursor.execute(sql)
    # 提交更改
    conn.commit()
    # 寻找需要乘车的乘客
    sql = f"SELECT CAR_ID, FIR_PT_N, LST_PT_N, LON, LAT FROM {ordertable} WHERE CUS_STATE = 1"
    cursor.execute(sql)
    cus = cursor.fetchall()
    cus_num = len(cus)
    # 如果乘车乘客不为0，则添加乘客信息
    if cus_num != 0:
        simulation_G.Updata_G_nodes(nodes_data=cus, nodes_notes=prefix_cus_O, **kwargs)
    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，乘客人数{cus_num}， 耗时 {time_list[-1] - time_list[-2]:.2f} s')


def Customer_Destribution(**kwargs):
    """
    判断当前下需要乘车的乘客，以及等待分配的空车
    对模拟器中的乘客进行车辆分配
    :param kwargs:
    :return:
    """
    G = kwargs['_G_']
    now_time = kwargs['_now_time_']
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
                # CUS_STATE, ACCEPTANCE_TIME, DH_MILEAGE, CUS_ID
                update_cus_values.append((2, now_time, task_dh_mileage, cus_id))
                # mysql table: cardata cols
                # CAR_STATE, TASK_CUS_ID, TASK_DH_MILEAGE, TASK_ACCEPTANCE_TIME, TASK_PATH_ID, TASK_PATH, CAR_ID
                update_cus_values.append((2, cus_id, task_dh_mileage, now_time, 0, task_path, car_id))
                car_ids_G.pop(car_id_G)
                cus_ids.pop(cus_id)
    # 如果存在可以更新的数据：
    if len(update_cus_values) != 0:
        # orderdata
        sql_update = f"UPDATE {ordertable} SET CUS_STATE = %s, ACCEPTANCE_TIME = %s, DH_MILEAGE = %s WHERE CUS_ID = %s"
        cursor.executemany(sql_update, update_cus_values)
        conn.commit()
        # cardata
        sql_update = f"UPDATE {cartable} SET CAR_STATE = %s, TASK_CUS_ID = %s, TASK_DH_MILEAGE = %s, " \
                     f"TASK_ACCEPTANCE_TIME = %s, TASK_PATH_ID = %s, TASK_PATH = %s WHERE CAR_ID = %s"
        cursor.executemany(sql_update, update_car_values)
        conn.commit()


def Vehicle_Operation(**kwargs):
    G = kwargs['_G_']
    now_time = kwargs['_now_time_']
    conn = kwargs['_conn_']
    cursor = kwargs['_cursor_']
    ordertable = kwargs['_config_'].get('MYSQL', 'order_data')
    cartable = kwargs['_config_'].get('MYSQL', 'car_data')
    prefix_car = kwargs['_config_'].get('G', 'prefix_car')
    prefix_cus_O = kwargs['_config_'].get('G', 'prefix_cus_O')
    unit_time = kwargs['_config_'].get('PARAMETERS', 'unit_time')

    # 更新驶向乘客所在地的车辆信息，如果车辆到达则更新信息
    task_path = 0
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
            enr_car_id = row[0]
            lon = row[1]
            lat = row[2]
            fir_pt_n = row[3]
            lst_pt_n = row[4]
            if car_states == 1:
                runtime = now_time - row[5]
            else:
                runtime = now_time - row[6]
            task_path_id = row[7]
            task_path = row[8]
            # 更新车辆位置
            # 到达路径终点位置所需时间，必须转化为整型，因为最小计量单位为s
            # Estimated Time of Arrival
            if task_path_id != 0:
                # 如果不是第一段路(O -> nodes1)
                task_path_id_end = len(task_path['path']) - 1
                new_task_path_id = task_path_id
                while new_task_path_id < task_path_id_end:
                    # 如果也不是最后一段路(nodesn -> D)
                    # 则说明当前是OD中间的道路节点
                    # 抵达下一段路口(nodes)必须行驶的总时间为eta
                    # # Estimated Time of Arrival
                    new_task_path_id += 1
                    eta = task_path['path'][new_task_path_id][1]
                    if runtime < eta:
                        # 如果小于必须行驶总时间，则意味着车辆还在任务路径上
                        radio = (eta - runtime) / \
                                (task_path['time_len'][new_task_path_id] - task_path['time_len'][new_task_path_id - 1])
                        # 如果当前时间小于行驶到路口的总时间，则意味着在该道路中间
                        if new_task_path_id == task_path_id + 1:
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
                                lst_loc = task_path['OD_loc'][-1]
                            else:
                                # 略
                                lst_nodes = G.nodes[lst_pt_n]
                                lst_loc = [lst_nodes['x'], lst_nodes['y']]
                            # 计算更新后的坐标
                            new_lon, new_lat = simulation_G.Get_middle_nodes_location(fir_loc=fir_loc, lst_loc=lst_loc,
                                                                                      radio=radio)
                            # (+)意味着在原有数值上面更改，否则是替换
                            # LON, LAT, LOG_TIME, ALL_RUN_MILEAGE(+), ALL_DH_MILEAGE_P(+), ALL_RUN_TIME(+),
                            # ALL_DH_TIME_D(+), TASK_ALL_MILEAGE(+), TASK_DH_MILEAGE(+), TASK_NOW_MILEAGE(+),
                            # TASK_PATH_ID, CAR_ID
                            car_records_updata_loc.append((new_lon, new_lat, enr_car_id))
                            # 更新完成，结束循环
                            break
                        else:
                            # 否则意味着该车辆变更了道路
                            # 此时第一个点始终是道路上面的点
                            if new_task_path_id == task_path_id_end:
                                # 意味着最后一个点刚刚好是D点（临时点）
                                lst_loc = task_path['OD_loc'][1]
                                # 意味着进入到最后一条道路
                                # 由于最后一条道路的终点是临时点（非地图上的道路节点），所以需要找到真实的道路节点
                                # 临时节点和道路节点有且仅有两个节点连接
                            else:
                                # 意味着上一个点是道路上的点（恒定点）
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
                            car_records_updata_road.append((new_lon, new_lat, enr_car_id))
                            print()
