from config import db_config
import pymysql
from buaa_log import Logger
from contextlib import contextmanager

#log = Logger('aigc-aigc-gpt-bridge/aigc-task/logs/extract_knowledge.log', level='debug')
log = Logger('logs/extract_knowledge.log', level='debug')
@contextmanager
def get_connection():
    connection = pymysql.connect(**db_config)
    try:
        yield connection
    finally:
        connection.close()

# 从数据库中抽取内容
def extract_from_db(cartype):
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            sql = 'select description from car where cartype =%s'
            cursor.execute(sql, cartype)
            msg = cursor.fetchall()[0][0]
            return msg
        except:
            log.logger.info('调用知识库失败，模型:{}未录入知识库'.format(cartype))
            raise
        finally:
            cursor.close()



