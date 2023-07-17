import warnings

import networkx as nx

_name_ = 'simulation_G'
_accuracy_ = 6


def Updata_G_nodes(
        nodes_data: tuple = None,
        nodes_notes: str = '',
        **kwargs
):
    """
    为图数据中更新出现的乘客点
    :param nodes_data: list[tuple], # CUS_ID, FIR_L_N, LST_L_N, ON_LON, ON_LAT
    :param nodes_notes: 实现 point_name=nodes_notes + CUS_ID
    :param kwargs: 模拟器的属性
    :return:
    """
    G = kwargs['_G_']
    log = kwargs['_log_']

    # 逐一为插入的乘客增加边属性信息
    for row in nodes_data:
        # row 0 -> 4
        # cardata ||
        # cusdata || CUS_ID, FIR_PT_N, LST_PT_N, ON_LON, ON_LAT
        # 更新点
        x = row[3]
        y = row[4]
        node_name = nodes_notes + str(row[0])
        if G.has_node(node_name):
            # 移除节点
            G.remove_node(node_name)
        G.add_node(node_name, x=x, y=y)
        # 更新边
        edge_attrs_1, edge_attrs_2 = Compute_new_edges_attrs(
            G=G,
            point_loc=[x, y],
            point_name=nodes_notes + str(row[0]),
            fir_point_name=row[1],
            lst_point_name=row[2],
            log=log,
        )
        G.add_edge(edge_attrs_1['fir_pt_n'], edge_attrs_1['lst_pt_n'], **edge_attrs_1)
        G.add_edge(edge_attrs_2['fir_pt_n'], edge_attrs_2['lst_pt_n'], **edge_attrs_2)
    return G


def Compute_new_edges_attrs(
        G,
        point_loc: list,  # 节点的坐标
        point_name: str,  # 节点的名称
        fir_point_name,  # 端点名1，必须是node
        lst_point_name,  # 端点名2，必须是node
        log: object
):
    """
        计算新加入节点后，新增两台边的属性信息
    :param G: 图数据
    :param point_loc: 节点的坐标
    :param point_name:  节点的命名
    :param fir_point_name: 插入的边第一个节点
    :param lst_point_name: 插入的边第二个节点
    :param log: 日志对象
    :return: dict, 属性
    """
    if fir_point_name == lst_point_name:
        warnings.warn(f"fir_point_name‘{fir_point_name}’ can’t be same with lst_point_name‘{lst_point_name}’")
    fir_point = [G.nodes[fir_point_name]['x'],
                 G.nodes[fir_point_name]['y']]
    lst_point = [G.nodes[lst_point_name]['x'],
                 G.nodes[lst_point_name]['y']]
    radio = Get_middle_nodes_radio(fir_point=fir_point, lst_point=lst_point,
                                   mid_point=point_loc, accuracy=6, log=log)
    """
    'shape_len', 'wgs84_len', 'fir_pt_n', 'lst_pt_n', 'line_n', 'weight', 'geometry'
    # 1: fst -> mid
    # 2: mid -> mid
    """
    line_attrs = G[fir_point_name][lst_point_name]
    shape_len1 = line_attrs['shape_len'] * radio
    shape_len2 = line_attrs['shape_len'] - shape_len1
    time_len1 = line_attrs['time_len'] * radio
    time_len2 = line_attrs['time_len'] - time_len1
    wgs84_len1 = line_attrs['wgs84_len'] * radio
    wgs84_len2 = line_attrs['wgs84_len'] - wgs84_len1
    weight1 = line_attrs['weight'] * radio
    weight2 = line_attrs['weight'] - shape_len1
    edge_attrs_1 = {
        'shape_len': shape_len1,
        'time_len': time_len1,
        'wgs84_len': wgs84_len1,
        'fir_pt_n': fir_point_name,
        'lst_pt_n': point_name,
        'line_n': 'temp',
        'weight': weight1,
    }
    edge_attrs_2 = {
        'shape_len': shape_len2,
        'time_len': time_len2,
        'wgs84_len': wgs84_len2,
        'fir_pt_n': point_name,
        'lst_pt_n': lst_point_name,
        'line_n': 'temp',
        'weight': weight2,
    }
    return edge_attrs_1, edge_attrs_2


def Get_middle_nodes_radio(
        fir_point: list,
        lst_point: list,
        mid_point: list,
        accuracy: int = _accuracy_,
        log: object = None
):
    """
        获得中间点相对于首位两点的位置比例，用作计算图中新边的属性分配比例
    :param fir_point: list, x,y
    :param lst_point: list, x,y
    :param mid_point: list, x,y
    :param accuracy: 小数点后几位
    :return: int
    """
    if round(lst_point[0] - fir_point[0], accuracy) != 0:
        # 按照横坐标求比例
        a = mid_point[0] - fir_point[0]
        b = lst_point[0] - fir_point[0]
        radio = round(a / b, accuracy)
    else:
        # 按照纵坐标坐标求比例
        a = mid_point[1] - fir_point[1]
        b = lst_point[1] - fir_point[1]
        radio = round(a / b, accuracy)
    if radio < 0 or radio > 1:
        error = f"radio value is out of range! right values should belong [0, 1], not {radio}"
        warnings.warn(error)
        if log is not None:
            try:
                log.write_data(error)
            except Exception as E:
                warnings.warn(f"log object error, {E}")
        else:
            pass
    return radio


def Get_middle_nodes_location(
        fir_loc: list,
        lst_loc: list,
        radio: float,
        accuracy: int = _accuracy_,
):
    """

    :param fir_loc: list, [lon, lat]
    :param lst_loc: list, [lon, lat]
    :param radio: float, 中间点位于首位两点的比例
    :param accuracy: int, 结果保留的小数
    :return: (mid_x, mid_y)
    """
    dis_x = lst_loc[0] - fir_loc[0]
    dis_y = lst_loc[1] - fir_loc[1]
    mid_x = round(fir_loc[0] + radio * dis_x, accuracy)
    mid_y = fir_loc[1] + radio * dis_y
    return mid_x, mid_y


def Get_Shortest_Car_To_Cus_Path(
        car_names,  # 符合条件的车辆编号们 (就算单个pd.data对象也没事)
        cus_name,  # 目标乘客
        weight: str = 'shape_len',  # 计算最短路径的权重名称，有三类（weight， shape_len， wgs84_length）
        weight_limit: float = 3000,
        **kwargs
):
    G = kwargs['_G_']
    try:
        length, old_path = nx.multi_source_dijkstra(G=G, sources=set(car_names), target=cus_name,
                                                    weight=weight, cutoff=weight_limit)
    except nx.NetworkXNoPath:
        length, old_path = None, None

    if length is not None:
        new_path = [old_path[0]] + [x for x in old_path[1:-1] if isinstance(x, (int, float))] + [old_path[-1]]
        task_path = Path_To_Task_path(G, new_path, weights=['shape_len', 'time_len'])
    else:
        task_path = None
    return length, task_path


def Path_To_Task_path(G, path: list, weights: list):
    """
        从一条给的道路中，获得对应的道路累加权值，作为道路的任务路径
    :param G: Graph, 图数据
    :param path: list, 形如[node1, node2, ...]，是一条通路
    :param weights: list, list[str, ..., str]传入的权重
    :return: task_path, dict, 形如{path:[start_pt, node1, node2, ..., end_pt],
                                weight1:[0, weight1_sum1, weight1_sum2, ...., weight1_sumn],
                                weight2:[0, weight2_sum1, weight2_sum2, ...., weight2_sumn],
                                OD_loc:[[start_pt.x, start_pt.y], [end_pt.x, end_pt.y]],
                                OD_neighbors:[[start_pt.fir_pt_n, start_pt.lst_pt_n],
                                                [end_pt.fir_pt_n, end_pt.lst_pt_n]]}
                其中，start_pt.fir_pt_n -> start_pt -> start_pt.lst_pt_n ->
                    node1 -> ... -> end_pt.fir_pt_n -> end_pt -> end_pt.lst_pt_n
    """
    # path
    task_path = {'path': path}
    # weights
    for weight in weights:
        # 对每种类型的权重累积进行计算
        task_path[weight] = [0]
        for i in range(len(path) - 1):
            point1_name = path[i]
            point2_name = path[i + 1]
            # 获取对应的边对象
            try:
                edge = G.edges[point1_name, point2_name]
            except:
                print('a')
            task_path[weight].append(task_path[weight][-1] + edge[weight])
        # 保证最后一个为整数
        task_path[weight][-1] = int(task_path[weight][-1])
    # OD_loc
    start_pt = G.nodes[path[0]]
    end_pt = G.nodes[path[-1]]
    task_path['OD_loc'] = [[start_pt['x'], start_pt['y']],
                           [end_pt['x'], end_pt['y']]]

    # OD_neighbors
    task_path['OD_neighbors'] = [list(G.neighbors(path[0])), list(G.neighbors(path[-1]))]

    # 检查正确顺序
    if path[1] != task_path['OD_neighbors'][0][-1]:
        task_path['OD_neighbors'][0] = task_path['OD_neighbors'][0][::-1]
    if path[-2] != task_path['OD_neighbors'][1][-1]:
        task_path['OD_neighbors'][1] = task_path['OD_neighbors'][1][::-1]
    return task_path
