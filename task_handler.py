import pymysql
from contextlib import contextmanager
import threading
import time
from config import db_config
import openai
from mysql_util import update_task_schedule, update_token_size, get_unique_key
from context_generator import ContentGenerator
import json
from buaa_log import Logger

log = Logger('logs/task_handler.log', level='debug')
#记录任务错误次数的字典，主键为task_id，值为回退次数
task_error_count = {}

# 创建一个数据库连接管理器
@contextmanager
def get_connection():
    connection = pymysql.connect(**db_config)
    try:
        yield connection
    finally:
        connection.close()


def get_task_details_by_id(task_id):
    """
    通过任务id获取任务详细数据
    :param task_id: 任务id
    :return: response
    """
    try:
        details = {}
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # 获取任务基础信息
                cursor.execute(
                    "SELECT t.task_id, p.platform_name, t.gmt_created FROM t_task t JOIN t_platform p ON t.platform_id = p.platform_id WHERE t.task_id = %s",
                    [task_id])
                task_info = cursor.fetchone()
                if not task_info:
                    raise Exception(f"Task with ID '{task_id}' not found.")
                details['task_id'] = task_info[0]
                details['platform_name'] = task_info[1]
                details['gmt_created'] = str(task_info[2])
                details['task_data'] = {}

                # 获取与任务关联的参数和参数值
                cursor.execute("""
                    SELECT pa.param_name, tpv.value 
                    FROM t_task_parameter_value tpv 
                    JOIN t_parameter pa ON tpv.param_id = pa.param_id 
                    WHERE tpv.task_id = %s
                """, [task_id])

                for param_name, param_value in cursor.fetchall():
                    details['task_data'][param_name] = param_value
            return details
    except Exception as e:
        print(f"Error occurred: {e}")
        return {}


# 加锁获取一条状态为0的记录，并将其状态改为1
def get_and_lock_record():
    #log.logger.info('开始读取状态为0的记录')
    with get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                # 开始事务
                conn.begin()
                # 加锁选取一条状态为0的记录
                cursor.execute("SELECT copy_id,task_id FROM t_generated_text WHERE status = 0 LIMIT 1 FOR UPDATE ;")
                record = cursor.fetchone()
                if not record:
                    # 如果没有找到记录，则回滚事务并返回None
                    #log.logger.info('未读取到状态为0的记录')
                    conn.rollback()
                    return None, None
                copy_id = record[0]
                task_id = record[1]
                log.logger.info('成功读取到状态为0的记录，task_id = {}, copy_id = {}'.format(task_id, copy_id))
                # 将记录状态改为1
                cursor.execute("UPDATE t_generated_text SET status = 1 WHERE copy_id = %s;", (copy_id,))
                conn.commit()
                log.logger.info('修改任务状态为1')
                return copy_id, task_id
            except Exception as e:
                print(f"Error: {e}")
                conn.rollback()


# 更新t_generated_text表中的内容以及状态
def update_status(copy_id, content, status):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE t_generated_text SET status = %s ,content =%s WHERE copy_id = %s;",
                           (status, content, copy_id))
            conn.commit()


def generate_reply(messages, key):
    openai.api_key = key
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=messages
    )
    result = json.loads(
        json.dumps(completion, ensure_ascii=False).encode('utf8').decode())
    return result["choices"][0]["message"]["content"].replace("\"", "").replace("\”", "").replace("\n\n", "\n")


def perform_task(task):
    #try:
    context = ContentGenerator(task)
    log.logger.info("成功实例化ContentGenerator")
    #except:
    #    log.logger.info('ContentGenerator实例化失败，请检查相应的参数输入')
    #try:
    input = context.generate()
    log.logger.info("成功生成相应的input with prompt")
    #print('\nprompt:'+ input)
    #except:
    #    log.logger.info('chatgpt所需的文案生成失败，请检查相应的参数输入')

    log.logger.info("开始获取key")
    key = get_unique_key()
    log.logger.info("成功获取key:{}".format(key))
    # 调用chatgpt
    if isinstance(input, list):
        n = len(input)
        messages = []
        for i in range(n-1):
            messages.append({"role": "user", "content": input[i]})
            messages.append({"role": "assistant", "content": "READ"})
        messages.append({"role": "user", "content": input[n-1]})
    else:
        messages = [{
            "role": "user",
            "content": input
        }]
    log.logger.info("开始调用chatgpt")
    result = generate_reply(messages, key)
    log.logger.info("成功调用chatgpt")
    #print('input:{}\toutput:{}\ttogether:{}'.format(len(input), len(result), len(input) + len(result)))
    # 更新token—size
    log.logger.info("开始更新token")
    update_token_size(key, len(result))
    log.logger.info("成功更新token")
    return result

def process_record(copy_id, task_id):
    try:
        log.logger.info('开始获取task_id = {} 的详细任务信息'.format(task_id))
        task = get_task_details_by_id(task_id)
        # 执行你的计算逻辑
        log.logger.info('开始通过task_id = {} 的详细任务信息生成相应的chatgpt文案'.format(task_id))
        content = perform_task(task)
        log.logger.info('成功获取chatgpt生成的文案')
        # 如果计算成功，将状态改为2
        log.logger.info("开始更新任务状态与内容")
        update_status(copy_id, content, 2)
        log.logger.info("成功插入内容，并更新任务状态为2")
        # 并更新任务的schedule
        log.logger.info("开始更新任务schedule")
        update_task_schedule(task_id)
        log.logger.info("成功更新任务schedule+=1")
        log.logger.info('成功处理copy_id = {}, task_id = {} 的数据'.format(copy_id, task_id))
    except Exception as e:
        print(f"Error in processing record {copy_id}: {e}")

        global task_error_count
        task_error_count[task_id] = task_error_count.get(task_id, 0) + 1
        #如果计算失败次数超过3，停止回退
        if task_error_count[task_id] >= 3:
            update_status(copy_id, "", 3)
            log.logger.info('处理copy_id = {}, task_id = {} 的数据时失败超过3次，将其状态改为3'.format(copy_id, task_id))
        # 如果计算失败，将状态改回0,并休息60s
        else:
            update_status(copy_id, "", 0)
            log.logger.info('处理copy_id = {}, task_id = {} 的数据时失败，将其状态改回为0'.format(copy_id, task_id))
        time.sleep(5) #60

def get_keywords():

    pass

def main():
    while True:
        copy_id, task_id = get_and_lock_record()
        if copy_id and task_id:
            log.logger.info('开始处理copy_id = {}, task_id = {} 的数据'.format(copy_id, task_id))
            process_record(copy_id, task_id)
        time.sleep(10) #10


#创建一个函数，用于启动线程并执行main函数

def run_in_thread():
    t = threading.Thread(target=main)
    t.start()
    return t


def multi_thread_main():
    # 定义线程数量
    thread_count = 10 #3
    threads = []
    for i in range(thread_count):
        threads.append(run_in_thread())
    # 等待所有线程完成
    for t in threads:
        t.join()


if __name__ == '__main__':
    multi_thread_main()


