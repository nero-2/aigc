import pymysql
from config import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, DATABASES, MYSQL_PORT, db_config, db_config2
import datetime
import traceback
from buaa_log import Logger

#connection = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USERNAME, password=MYSQL_PASSWORD,
 #                            database=DATABASES)

log = Logger('logs/get_key.log', level='debug')


# 插入数据
def insert_generated_content(task_id, context, table_name):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO {} (`task_id`,`content`,`generated_time`) VALUES (%s,%s,%s)".format(table_name)
            create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(sql, (task_id, context, create_time))
            connection.commit()
            return {"code": 200, "msg": "插入成功"}
    except Exception:
        traceback.print_exc()
        return {"code": 400, "msg": "插入失败"}
    finally:
        connection.close()



def update_task_schedule(task_id):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE t_task SET schedule= schedule + 1  WHERE task_id = %s"
            cursor.execute(sql, [task_id])
            connection.commit()
            return {"code": 200, "msg": "更新成功"}
    except Exception:
        return {"code": 400, "msg": "更新失败"}
    finally:
        connection.close()

"""
def get_unique_key():
    connection = pymysql.connect(**db_config2)
    unique_key = None
    try:
        # 开启事务
        connection.begin()
        # 获取游标
        with connection.cursor() as cursor:
            # 使用悲观锁查询未使用的 key（status = 0 表示未使用）
            sql = "SELECT id, `key` FROM car_key WHERE active_status = 0 ORDER BY active_time ASC, token_size ASC LIMIT 1 FOR UPDATE"
            cursor.execute(sql)
            result = cursor.fetchone()
            if not result:
                log.logger.info("============当前数据库中没有可使用的key,请稍后尝试============")
                connection.rollback()  # 回滚事务
            else:
                key_id, unique_key = result
                # 将 key 标记为已使用（例如，将 status 设置为 1）
                update_query = "UPDATE car_key SET active_status = 1, active_time = %s WHERE id = %s"
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(update_query, (current_time, key_id))
                # 提交事务，释放锁
                connection.commit()
    except Exception as e:
        log.logger.error(e)
        connection.rollback()  # 回滚事务

    finally:
        # 关闭连接
        connection.close()

    return unique_key

"""

def get_unique_key():
    return "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"

def update_token_size(key, string_length):
    connection = pymysql.connect(**db_config2)
    try:
        with connection.cursor() as cursor:
            # 更新 token_size
            sql = "UPDATE car_key SET token_size = token_size + %s WHERE `key` = %s"
            cursor.execute(sql, (string_length, key))
        # 提交更改
        connection.commit()
    except Exception as e:
        print(f"Error updating token_size: {e}")
    finally:
        connection.close()



def get_task_table_count(task_id, table_name):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = "select count from {} where task_id = {}".format(table_name, task_id)
            cursor.execute(sql)
            result = cursor.fetchone()[0]
            return result
    except Exception as e:
        print(f"Error get task table count: {e}")
    finally:
        connection.close()
