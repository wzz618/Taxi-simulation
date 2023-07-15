cardata = {
    'CAR_ID': int,
    'CAR_NO': str,
    'CAR_STATE': int,
    'LON': float,
    'LAT': float,
    'FIR_PT_N': int,
    'LST_PT_N': int,
    'LOG_TIME': float,
    'ALL_RUN_MILEAGE': float,
    'ALL_PMTD': float,
    'ALL_DH_MILEAGE_P': float,
    'ALL_DH_MILEAGE_D': float,
    'ALL_RUN_TIME': float,
    'ALL_DH_TIME_P': float,
    'ALL_DH_TIME_D': float,
    'ALL_ORDER_COUNT': int,
    'TASK_CUS_ID': int,
    'TASK_ALL_MILEAGE': float,
    'TASK_PMTD': float,
    'TASK_DH_MILEAGE': float,
    'TASK_NOW_MILEAGE': float,
    'TASK_ACCEPTANCE_TIME': int,
    'TASK_GET_ON_TIME': int,
    'TASK_GET_OFF_TIME': int,
    'TASK_PATH_ID': int,
}

orderdata = {
    'CUS_ID': int,
    'CAR_ID': int,
    'CUS_STATE': int,
    'ON_LON': float,
    'ON_LAT': float,
    'ON_FIR_PT_N': int,
    'ON_LST_PT_N': int,
    'OFF_LON': float,
    'OFF_LAT': float,
    'OFF_FIR_PT_N': int,
    'OFF_LST_PT_N': int,
    'FIR_L_N': int,
    'LST_L_N': int,
    'APPEARANCE_TIME': int,
    'ACCEPTANCE_TIME': int,
    'GET_ON_TIME': int,
    'GET_OFF_TIME': int,
    'DH_MILEAGE': float,
    'PMTD': float,
}

SQL_Index = {
    'car_data': ['CAR_ID', 'CAR_STATE'],
    'order_data': ['CUS_ID', 'CAR_ID', 'CUS_STATE', 'APPEARANCE_TIME'],
    'map_data': []
}


def sql_vehicle_operation(sql_table: str, updata_type: str, car_state: int) -> str:
    """
        获得对应的sql查询语句
        :param sql_table:
        :param updata_type: updata_loc/updata_road/updata_task
        :param car_state:
    """
    if updata_type == 'updata_loc':
        # 仅仅更新车辆的坐标
        if car_state == 1:
            # 空驶里程
            # (+)意味着在原有数值上面更改，否则是替换
            # LON, LAT, LOG_TIME,
            # ALL_RUN_MILEAGE(+), ALL_DH_MILEAGE_P(+), ALL_RUN_TIME(+),
            # ALL_DH_TIME_P(+), TASK_ALL_MILEAGE(+), TASK_DH_MILEAGE(+), TASK_NOW_MILEAGE(+),
            # CAR_ID
            sql = f"""
                UPDATE {sql_table}
                SET LON = %s, LAT = %s, LOG_TIME = %s,
                    ALL_RUN_MILEAGE = ALL_RUN_MILEAGE + %s, ALL_DH_MILEAGE_P = ALL_DH_MILEAGE_P + %s, ALL_RUN_TIME = ALL_RUN_TIME + %s,
                    ALL_DH_TIME_P = ALL_DH_TIME_P + %s, TASK_ALL_MILEAGE = TASK_ALL_MILEAGE + %s, TASK_DH_MILEAGE = TASK_DH_MILEAGE + %s,
                    TASK_NOW_MILEAGE = TASK_NOW_MILEAGE + %s
                WHERE CAR_ID = %s
            """
        else:
            # 有效载客里程
            # LON, LAT, LOG_TIME, ALL_RUN_MILEAGE(+), ALL_PMTD(+), ALL_RUN_TIME(+),
            # TASK_ALL_MILEAGE(+), TASK_PMTD(+), TASK_NOW_MILEAGE(+),
            # CAR_ID
            sql = f"""
                UPDATE {sql_table}
                SET LON = %s, LAT = %s, LOG_TIME = %s,
                    ALL_RUN_MILEAGE = ALL_RUN_MILEAGE + %s, ALL_PMTD = ALL_PMTD + %s, ALL_RUN_TIME = ALL_RUN_TIME + %s,
                    TASK_ALL_MILEAGE = TASK_ALL_MILEAGE + %s, TASK_PMTD = TASK_PMTD + %s, TASK_NOW_MILEAGE = TASK_NOW_MILEAGE + %s
                WHERE CAR_ID = %s
            """
    elif updata_type == 'updata_road':
        # 更新道路
        if car_state == 1:
            # FIR_PT_N, LST_PT_N
            # LON, LAT, LOG_TIME,
            # ALL_RUN_MILEAGE(+), ALL_DH_MILEAGE_P(+), ALL_RUN_TIME(+),
            # ALL_DH_TIME_P(+), TASK_ALL_MILEAGE(+), TASK_DH_MILEAGE(+), TASK_NOW_MILEAGE(+),
            # TASK_PATH_ID, CAR_ID
            sql = f"""
                UPDATE {sql_table}
                SET FIR_PT_N = %s, LST_PT_N = %s, 
                    LON = %s, LAT = %s, LOG_TIME = %s, 
                    ALL_RUN_MILEAGE = ALL_RUN_MILEAGE + %s, ALL_DH_MILEAGE_P = ALL_DH_MILEAGE_P + %s, ALL_RUN_TIME = ALL_RUN_TIME + %s, 
                    ALL_DH_TIME_P = ALL_DH_TIME_P + %s, TASK_ALL_MILEAGE = TASK_ALL_MILEAGE + %s, TASK_DH_MILEAGE = TASK_DH_MILEAGE + %s, TASK_NOW_MILEAGE = TASK_NOW_MILEAGE + %s, TASK_PATH_ID=%s 
                WHERE CAR_ID = %s
                """
        else:
            # FIR_PT_N, LST_PT_N
            # LON, LAT, LOG_TIME,
            # ALL_RUN_MILEAGE(+), ALL_PMTD(+), ALL_RUN_TIME(+),
            # TASK_ALL_MILEAGE(+), TASK_PMTD(+), TASK_NOW_MILEAGE(+),
            # TASK_PATH_ID, CAR_ID
            sql = f"""
                UPDATE {sql_table}
                SET FIR_PT_N = %s, LST_PT_N = %s, 
                    LON = %s, LAT = %s, LOG_TIME = %s, 
                    ALL_RUN_MILEAGE = ALL_RUN_MILEAGE + %s, ALL_PMTD = ALL_PMTD + %s, ALL_RUN_TIME = ALL_RUN_TIME + %s,
                    TASK_ALL_MILEAGE = TASK_ALL_MILEAGE + %s, TASK_PMTD = TASK_PMTD + %s, TASK_NOW_MILEAGE = TASK_NOW_MILEAGE + %s, TASK_PATH_ID = %s 
                WHERE CAR_ID = %s
                """
    else:
        # 抵达该任务终点
        if car_state == 1:
            # # (+)意味着在原有数值上面更改，否则是替换
            # CAR_STATE, LON, LAT,
            # FIR_PT_N, LST_PT_N, LOG_TIME,
            # ALL_RUN_MILEAGE(+), ALL_DH_MILEAGE_P(+),
            # ALL_RUN_TIME(+), ALL_DH_TIME_P(+),
            # TASK_ALL_MILEAGE(+), TASK_DH_MILEAGE(+),
            # TASK_NOW_MILEAGE(+), TASK_GET_ON_TIME
            # CAR_ID
            sql = f"""
                UPDATE {sql_table}
                SET CAR_STATE = %s, LON = %s, LAT = %s,
                    FIR_PT_N = %s, LST_PT_N = %s, LOG_TIME = %s,
                    ALL_RUN_MILEAGE = ALL_RUN_MILEAGE + %s, ALL_DH_MILEAGE_P = ALL_DH_MILEAGE_P + %s,
                    ALL_RUN_TIME = ALL_RUN_TIME + %s, ALL_DH_TIME_P = ALL_DH_TIME_P + %s,
                    TASK_ALL_MILEAGE = TASK_ALL_MILEAGE + %s, TASK_DH_MILEAGE = TASK_DH_MILEAGE + %s, 
                    TASK_NOW_MILEAGE = TASK_NOW_MILEAGE + %s, TASK_GET_ON_TIME = %s 
                WHERE CAR_ID = %s
            """
        else:
            # CAR_STATE， LON, LAT,
            # FIR_PT_N, LST_PT_N, LOG_TIME,
            # ALL_RUN_MILEAGE(+), ALL_PMTD(+),
            # ALL_RUN_TIME(+), TASK_ALL_MILEAGE(+),
            # TASK_PMTD(+), TASK_NOW_MILEAGE(+),
            # TASK_GET_OFF_TIME
            # CAR_ID
            sql = f"""
                UPDATE {sql_table}
                SET CAR_STATE = %s, LON = %s, LAT = %s,
                    FIR_PT_N = %s, LST_PT_N = %s, LOG_TIME = %s,
                    ALL_RUN_MILEAGE = ALL_RUN_MILEAGE + %s, ALL_PMTD = ALL_PMTD + %s,
                    ALL_RUN_TIME = ALL_RUN_TIME + %s, TASK_ALL_MILEAGE = TASK_ALL_MILEAGE + %s,
                    TASK_PMTD = TASK_PMTD + %s, TASK_NOW_MILEAGE = TASK_NOW_MILEAGE + %s, 
                    TASK_GET_OFF_TIME = %s
                WHERE CAR_ID = %s
            """
    return sql
