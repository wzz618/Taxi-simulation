import pymysql
from sqlalchemy import create_engine


def MySQLCONNECTION(config):
    try:
        # 如果数据库存在则正常连接
        _conn_ = pymysql.connect(
            host=config.get('MYSQL', 'host'),  # 主机名（或IP地址）
            port=int(config.get('MYSQL', 'port')),
            user=config.get('MYSQL', 'user'),  # 账户名
            password=config.get('MYSQL', 'password'),  # 密码
            database=config.get('MYSQL', 'database')  # 数据库
        )
        return _conn_
    except pymysql.err.OperationalError:
        # 如果数据库不存在则创建
        _conn_ = pymysql.connect(
            host=config.get('MYSQL', 'host'),  # 主机名（或IP地址）
            port=int(config.get('MYSQL', 'port')),
            user=config.get('MYSQL', 'user'),  # 账户名
            password=config.get('MYSQL', 'password'),  # 密码
        )
        _mycursor_ = _conn_.cursor()  # 创建一个连接的游标
        _mycursor_.execute("CREATE DATABASE {}".format(config.get('MYSQL', 'database')))
        _mycursor_.close()  # 关闭该游标
        _conn_.close()  # 关闭该数据库连接
        return MySQLCONNECTION(config)


def MySQLENGINE(config):
    host = config.get('MYSQL', 'host')  # 主机名（或IP地址）
    port = int(config.get('MYSQL', 'port'))
    user = config.get('MYSQL', 'user')  # 账户名
    password = config.get('MYSQL', 'password')  # 密码
    database = config.get('MYSQL', 'database')  # 数据库
    url = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
    engine = create_engine(url)
    return engine

# def Create_Index(config, conn, cursor):
#     sql_index = {
#         'map_data': 'line_n',
#         'car_data': 'CAR_ID',
#         'order_data': 'CUS_ID',
#     }
#
#     for table, col in sql_index:
#         sql = f"CREATE INDEX idx_column1 ON your_table (column1)"
#         cursor.execute(sql)
