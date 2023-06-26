import pickle
import time
import warnings

import geopandas as gpd
import networkx as nx
import pandas as pd

import log_management

name = 'data_generate'


def Ceodata_Clean(config):
    """
        把地图文件进行清洗操作，并且保存清洗后的配置文件和图结构到原来的地址
        传入的地图需要包含的字段：OBJECTID，maxspeed
    :param config: 传入的配置文件
    :return:
    """
    crs_degree = config.get('MAP', 'crs_degree')  # 单位：度
    crs_metre = config.get('MAP', 'crs_metre')  # 单位：米
    Gepdata_path = config.get('MAP', 'map_path')
    G_path = config.get('MAP', 'G_path')
    weigh_propertion = float(config.get('MAP', 'weigh_propertion'))
    log_dir = config.get('LOG', 'dir_path')

    log = log_management.log_management(log_dir, name)
    log.write_tip('地图地理数据处理')
    # ------------------------------- 读取地图 ---------------------------
    operation_name = '读取地图'
    time_list = [time.perf_counter()]
    gdf_geodata = gpd.read_file(filename=Gepdata_path).to_crs(crs_degree)  # 读入数据
    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')

    # ------------------------------- 信息增添 ---------------------------
    operation_name = 'WGS_84信息处理'
    time_list.append(time.perf_counter())

    gdf_geodata['start_x'] = gdf_geodata.geometry.apply(lambda geom: geom.coords.xy[0][0])
    gdf_geodata['end_x'] = gdf_geodata.geometry.apply(lambda geom: geom.coords.xy[0][1])
    gdf_geodata['start_y'] = gdf_geodata.geometry.apply(lambda geom: geom.coords.xy[1][0])
    gdf_geodata['end_y'] = gdf_geodata.geometry.apply(lambda geom: geom.coords.xy[1][1])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        gdf_geodata['wgs84_len'] = gdf_geodata.length
    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')

    operation_name = 'WGS_84投影信息处理'
    time_list.append(time.perf_counter())
    df_crs_metre = gdf_geodata.to_crs(crs=crs_metre)
    gdf_geodata['shape_len'] = df_crs_metre.length  # 投影后的几何长度（单位是m）
    gdf_geodata['weight'] = round(gdf_geodata['shape_len'] / gdf_geodata['maxspeed'] * weigh_propertion)
    del df_crs_metre

    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')
    # -------------------------------连通性检查---------------------------
    operation_name = '连通性检查'
    time_list.append(time.perf_counter())

    # 构造无向图
    Undirected_graph = nx.Graph()
    edges = [(row['geometry'].coords[0], row['geometry'].coords[-1], dict(row)) for _, row in gdf_geodata.iterrows()]
    Undirected_graph.add_edges_from(edges)
    # 删除不连通组件
    if nx.number_connected_components(Undirected_graph) > 1:
        print('\t发现不连通网络共计{}个，正在删除'.format(nx.number_connected_components(Undirected_graph)), end=':')
        largest_cc = max(nx.connected_components(Undirected_graph), key=len)  # 获得最大组件
        for cc in nx.connected_components(Undirected_graph):  # 寻找组件
            if cc != largest_cc:
                # 如果不是最大的组件就删除
                invalid_G = Undirected_graph.subgraph(cc).copy().to_directed()  # 利用组件生成图
                for edge in invalid_G.edges:
                    line_name = invalid_G.edges[edge]['OBJECTID']  # 获得路段的名字
                    gdf_geodata.drop(
                        index=gdf_geodata.loc[gdf_geodata['OBJECTID'] == line_name].index, inplace=True)
                    print('已经删除线段{}'.format(line_name), end=",")
        gdf_geodata = gdf_geodata.reset_index()
    else:
        print('\t网络已经完全连通，不需要删除')
    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')

    # -------------------------------道路命名---------------------------
    operation_name = '道路节点名称格式化'
    time_list.append(time.perf_counter())

    # 根据索引重命名道路
    gdf_geodata['line_n'] = gdf_geodata.index

    # 根据无向图的节点重命名节点
    attrs = dict(zip([i_node for i_node in Undirected_graph.nodes],
                     [name_num for name_num in range(len(Undirected_graph.nodes))]))  # 创建nodes坐标和名字对应的数组
    nx.set_node_attributes(Undirected_graph, attrs, name='point_n')  # 为G的nodes增加字段point_n，根据字典赋值
    # 根据地理信息索引赋值
    gdf_geodata['fir_p_n'] = gdf_geodata['geometry'].apply(
        lambda geom: Undirected_graph.nodes[geom.coords[0]]['point_n'])
    gdf_geodata['lst_p_n'] = gdf_geodata['geometry'].apply(
        lambda geom: Undirected_graph.nodes[geom.coords[1]]['point_n'])

    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')

    # ------------------------------- 文件保存 ---------------------------
    operation_name = '道路节点名称格式化'
    time_list.append(time.perf_counter())
    gdf_geodata.to_file(filename=Gepdata_path, driver='ESRI Shapefile', encoding='utf-8')
    # 重新构造图结构
    Undirected_graph = nx.Graph()
    edges = [(row['geometry'].coords[0], row['geometry'].coords[-1], dict(row)) for _, row in gdf_geodata.iterrows()]
    Undirected_graph.add_edges_from(edges)
    with open(G_path, 'wb') as f:
        pickle.dump(Undirected_graph, f)
    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')


def Orderdata_Clean(config):
    Gepdata_path = config.get('MAP', 'map_path')
    crs_degree = config.get('MAP', 'crs_degree')  # 单位：度
    crs_metre = config.get('MAP', 'crs_metre')  # 单位：米
    dis_mate = float(config.get('MAP', 'dis_mate'))  # 单位：米
    Orderdata_path = config.get('ORDERSHEET', 'path')
    log_dir = config.get('LOG', 'dir_path')

    log = log_management.log_management(log_dir, name)
    log.write_tip('订单数据处理')

    # ------------------------------- 数据读入 ---------------------------
    operation_name = '数据读入'
    time_list = [time.perf_counter()]
    gdf_geodata = gpd.read_file(filename=Gepdata_path).to_crs(crs_metre)  # 道路地图数据
    df_orderdata = pd.read_csv(Orderdata_path)  # 乘客订单数据
    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')

    # ------------------------------- 订单道路拟合 ---------------------------
    operation_name = '订单道路拟合'
    time_list.append(time.perf_counter())

    # 创建空间索引
    lines_sindex = gdf_geodata.sindex

    # 分类
    x_list = ['ON_LON', 'OFF_LON']
    y_list = ['ON_LAT', 'OFF_LAT']
    road_list = ['fir_l_n', 'lst_l_n']

    for i in range(2):
        # 提取坐标列
        x_col = x_list[i]
        y_col = y_list[i]

        geometry = gpd.points_from_xy(x=df_orderdata[x_list[i]], y=df_orderdata[y_list[i]], crs=crs_degree) \
            .to_crs(crs_metre)
        points = gpd.GeoDataFrame(geometry=geometry)
        # 为每个点找到最近的线
        indices, distances = lines_sindex.nearest(points.geometry, return_distance=True, return_all=False)

        # 将最近的线的line_n添加到点的属性中
        distance_mask = distances.T <= dis_mate
        df_orderdata.loc[indices.T[distance_mask, 0], road_list[i]] = [gdf_geodata.loc[road_idx, 'line_n'] for road_idx
                                                                       in indices.T[distance_mask, 1]]
        points[road_list[i]] = df_orderdata[road_list[i]]
        # 删除找不到匹配项的点
        df_orderdata = df_orderdata[df_orderdata[road_list[i]].notna()]
        points = points[points[road_list[i]].notna()]
        df_orderdata.reset_index(inplace=True, drop=True)
        points.reset_index(inplace=True, drop=True)
        # 计算拟合坐标
        interpolated_points = [gdf_geodata.loc[row[road_list[i]], 'geometry'].interpolate(
            gdf_geodata.loc[row[road_list[i]], 'geometry'].project(row['geometry'])) for _, row in
            points[[road_list[i], 'geometry']].iterrows()]

        # 投影回经纬度坐标
        points = gpd.GeoSeries(interpolated_points, crs=crs_metre).to_crs(crs_degree)
        df_orderdata[x_list[i]] = points.x
        df_orderdata[y_list[i]] = points.y

    df_orderdata.to_csv(Orderdata_path, encoding='utf_8_sig', index=False)
    time_list.append(time.perf_counter())
    log.write_data(f'{operation_name}完成，耗时 {time_list[-1] - time_list[-2]:.2f} s')


if __name__ == '__main__':
    import configparser

    config_file = r"config.ini"
    # 进行文件读取和参数判断的初始化
    config = configparser.ConfigParser()
    # READ CONFIG FILE
    config.read(config_file, encoding="utf-8")
    Orderdata_Clean(config)
