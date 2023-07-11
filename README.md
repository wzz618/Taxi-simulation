# Taxi-simulation

## Data

## mapdata

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
- **CAR_STATE** 车辆状态，0空车，1正在驶向乘客，2是正在运送乘客
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
- **TASK_PATH_ID** 当前所处的巡航规划ID
- **TASK_PATH** 当前任务的任务路径

### orderdata

订单数据信息

- **CUS_ID** 乘客的编号，与 *orderdata* 的 *RN* 相同，如果没有则为0
- **CUS_STATE** *0* 未出现， *1* 等待车辆接单， *2* 已被车辆接单, *3* 已上车
- **ON_LON** 上车点的x
- **ON_LAT** 上车点的y
- **OFF_LON** 下车点
- **OFF_LAT** 下车点
- **FIR_PT_N** 乘客所处道路的第一个端点的序号
- **LST_PT_N** 乘客所处道路的第二个端点的序号
- **APPEARANCE_TIME** 订单出现的时间
- **ACCEPTANCE_TIME** 订单接受的时间
- **GET_ON_TIME** 订单乘客上车的时间
- **GET_OFF_TIME** 订单乘客下车的时间
- **DH_MILEAGE** 该任务接客空驶距离
- **PMTD** 该任务有效送客距离