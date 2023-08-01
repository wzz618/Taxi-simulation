# Taxi-simulation

## 项目背景

本项目源于我们小组在研究截单算法时的探索。截单算法是指在订单接受后打破乘客与司机之间的"锁定"
关系，我们希望了解这种算法对服务效率的影响。在初期的研究中，我们尝试了TransCAD、Vissim、Cube等软件，但它们无法满足我们对自定义车辆运行的需求。

因此，我们进行了当前出租车和网约车运行逻辑的分析，并编写了一套能够满足我们仿真需求的自定义仿真器。本项目在此基础上，对之前模拟器的架构进行了优化和重写，使其适用于较大规模的出租车/网约车运行模拟。

经过初步测试，我们的仿真器已能够满足较大规模的仿真需求。具体而言，它可以处理较大路网（例如西安市区的5万个节点），较大规模车辆（6,000辆），较长时间段（24小时）以及较大的订单数据集（26万份订单数据）。

## 项目基本介绍

本项目是一个功能丰富的出租车/网约车仿真模拟器，旨在满足个性化的交通运输研究需求。该模拟器具有自定义添加和修改运行逻辑的能力，使用户能够灵活地调整仿真环境。

通过向该仿真模拟器提供真实订单数据，可自动生成车辆的原始位置信息和原始订单信息。同时，通过使用来自OpenStreetMap的路网文件，自动生成准确的路网图结构，为车辆路径规划提供支持。在获得上述的初始化信息后，模拟器将进行迭代运行，并在每个时间步骤中更新车辆和订单信息。此外，模拟器还能够绘制和保存当前路网内各个车辆的状态，以及订单的信息。这样，用户可以根据需要获取不同时间点的车辆和订单详细信息。

通过这个仿真模拟器，用户可以进行各种交通运输方面的研究。无论是分析交通流量、优化车辆调度、评估截单算法的效果还是进行其他相关研究，该模拟器都提供了丰富的功能和灵活性。用户可以根据自己的需求进行定制化设置，并获得详尽的仿真结果和数据，为交通运输决策和研究提供有力的支持。

## 项目开发环境

以下是本项目开发时候的环境

- Windows 10
- CPU 24GB
- Python 3.9.6
- MySQL 8.2.32

## 项目启动说明

请确保满足下述需求后，把项目**克隆**到本地

- 安装 **Python**
- 安装 **MySQL**
- CPU > **4GB**

**第一步：安装依赖库**

```cmd
pip install -r requirements.txt
```

**第二步：下载原始数据文件**

```cmd
/map/<地理数据文件夹>/<地理数据原始文件>
/order/<订单数据原始文件>
```
你可以选择[demo](https://www.trafficwzz.com/download/taxi_simulation_resourse_demo/)里面的原始数据或者自己下载原始数据

<地理数据原始文件>: 来自[openstreetmap](https://www.openstreetmap.org)上下载的地图文件，注意记录对应的球坐标系和投影坐标系。文件必须包含的字段有：

- OBJECTID, maxspeed

<订单数据原始文件>: 研究区域内的订单数据，可以联系当地的有关部门获得。文件必须包含的字段包括：

- CAR_NO, ON_LON, ON_LAT, OFF_LON, OFF_LAT, GET_ON_TIME

**第三步：填写配置文件的关键内容**

在config_module.ini设置，并且在设置完后保存为 Taxi-simulation/src/config.ini

```config
[PARAMETERS]
now_time = <开始的时间>
run_times = <运行的总时长:s>
unit_time = <时间间隔:s>
search_length = <接单距离限制:m>

[MYSQL]
user = root
password = <你的MYSQL数据密码>

[MAP]
map_path = <地理信息文件(shp)的绝对文件地址>
crs_degree = <球坐标系标识符>
crs_metre = <投影坐标系标识符>

[ORDERSHEET]
path = <订单数据的绝对文件地址>
```

**第四步：初始化数据**

下述文件都应在 Taxi-simulation/src 内创建和运行，日志请查看 Taxi-simulation/log

- 初始化文件配置

```python
import config_initialization
config_initialization.config_initialization()
```

- 清洗原始数据，生成仿真数据

```python
import data_generate
data_generate.Generate()
```

- 把仿真数据导入数据库

```python
import data_lord
data_lord.Lord()
```

**第五步：运行仿真**

下述文件都应在 Taxi-simulation/src 内创建和运行

```python
import Taxi_simulation
import configparser

config_file = r"config.ini"
config = configparser.ConfigParser()
config.read(config_file, encoding="utf-8")
obj = TaxiSimulation(config)
obj.Run()
```

**再次运行仿真**

当你在仿真未结束的时候关闭了程序，但是希望从断点开始运行，你可以根据日志找到最后一次的时间点，然后修改config.ini的 [PARAMETERS] 的 now_time 的值修改，最后运行下述代码，即可从断点开始运行

```python
import Taxi_simulation
import configparser

config_file = r"config.ini"
config = configparser.ConfigParser()
config.read(config_file, encoding="utf-8")
obj = TaxiSimulation(config)
obj.Relord()
obj.Run()
```

**重新运行仿真**
当你想更新数据重新仿真，你需要重新把数据导入到数据库，然后进行第五步。

## 项目贡献者

项目参与者即为贡献者

## 联系方式

github可以私信项目内任一贡献者

## 仿真数据库各参数含义如下

### mapdata

地图数据信息

- **shape_len** 真实的道路长度
- **time_len** 通过时间长度
- **wgs84_len** 绘图长度
- **start_x** 端点坐标
- **start_y** 端点坐标
- **end_x** 端点坐标
- **end_y** 端点坐标
- **maxspeed** km/h 最高时速
- **weight** 权重
- **fir_pt_n** 道路端点
- **lst_pt_n** 道路端点
- **line_n** 道路序号
- **geometry** 道路几何信息

### cardata

车辆数据信息

- **CAR_ID** 车的序列号，无特定含义，由 *orderdata* 中车辆出现的时间顺序而来
- **CAR_NO** 车的ID号，与 *orderdata* 的 *CAR_NO* 相同
- **CAR_STATE** 车辆状态，0空车，1正在驶向乘客，2是正在运送乘客，3是抵达乘客上车点, 4是抵达乘客下车点
- **LON** 车辆经度
- **LAT** 车辆维度
- **FIR_PT_N** 车辆所处道路的第一个端点的序号
- **LST_PT_N** 车辆所处道路的第二个端点的序号
- **LOG_TIME** 最后一次更新记录的时间
- **ALL_RUN_MILEAGE** 行驶总距离
- **ALL_PMTD** Passenger Miles Traveled Driven 有效行驶里程，即载客行驶里程
- **ALL_DH_MILEAGE_P** Deadhead Mileage For Passenger 接客空驶里程
- **ALL_DH_MILEAGE_D** Deadhead Mileage For Dispatch 调度空驶里程
- **ALL_RUN_TIME** 总行驶时间
- **ALL_DH_TIME_P** Deadhead Time For Passenger 接客空驶时间
- **ALL_DH_TIME_D** Deadhead Time For Passenger 接客调度时间
- **ALL_ORDER_COUNT** 接到的订单次数
- **TASK_CUS_ID** 当前任务下，乘客的编号，与 *orderdata* 的 *RN* 相同，如果没有则为0
- **TASK_ALL_MILEAGE** 该任务行驶距离
- **TASK_PMTD** 该任务有效距离
- **TASK_DH_MILEAGE** 该任务接客空驶距离
- **TASK_NOW_MILEAGE** 当前任务行驶距离
- **TASK_ACCEPTANCE_TIME** 订单接受的时间
- **TASK_GET_ON_TIME** 订单乘客上车的时间
- **TASK_GET_OFF_TIME** 订单乘客下车的时间
- **TASK_PATH_ID** 当前所处的巡航规划ID
- **TASK_PATH** 当前任务的任务路径

### orderdata

订单数据信息

- **CUS_ID** 乘客的编号，与 *orderdata* 的 *RN* 相同，如果没有则为0
- **CAR_ID** 车的序列号，代表由该车接单
- **CUS_STATE** *0* 未出现， *1* 等待车辆接单， *2* 已被车辆接单, *3* 已上车, *4*已到达
- **ON_LON** 上车点的x
- **ON_LAT** 上车点的y
- **ON_FIR_PT_N** 乘客所处道路的第一个端点的序号
- **ON_LST_PT_N** 乘客所处道路的第二个端点的序号
- **OFF_LON** 下车点
- **OFF_LAT** 下车点
- **OFF_FIR_PT_N** 乘客目标道路的第一个端点的序号
- **OFF_LST_PT_N** 乘客目标道路的第二个端点的序号
- **FIR_L_N** 乘客所处道路
- **LST_L_N** 乘客目标道路
- **APPEARANCE_TIME** 订单出现的时间
- **ACCEPTANCE_TIME** 订单接受的时间
- **GET_ON_TIME** 订单乘客上车的时间
- **GET_OFF_TIME** 订单乘客下车的时间
- **DH_MILEAGE** 该任务接客空驶距离
- **PMTD** 该任务有效送客距离
