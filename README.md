# Taxi-simulation

## Data

### cardata

- **CAR_ID** 车的序列号，无特定含义，由 *orderdata* 中车辆出现的时间顺序而来
- **CAR_NO** 车的ID号，与 *orderdata* 的 *CAR_NO* 相同
- **LON** 车辆经度
- **LAT** 车辆维度
- **FIR_L_N** 车辆所处道路的第一个端点的序号
- **LST_L_N** 车辆所处道路的第二个端点的序号
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
- **TASK_PATH_ID** 当前所处的巡航规划ID