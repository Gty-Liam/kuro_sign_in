"""
任务名称
name: 库街区签到任务
定时规则
cron: 1 9 * * *
"""
import time
import json
import requests
from log import log_message
from game_check_in import game_check_in
from bbs_sgin_in import KuroBBS_sign_in
import schedule
import time
import random
from datetime import datetime, timedelta




def sc_send(text, desp, key=''):
    if key == '':
        print("请填写server酱的KEY")
        return
    url = f'https://sctapi.ftqq.com/{key}.send'
    data = {'text': text, 'desp': desp}
    response = requests.post(url, data=data)
    result = response.text
    return result


def job():
    msg = check_in()

    with open('data.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
    serverKey = data['serverKey']
    # 发送server酱通知
    log_message(sc_send("签到", msg, key=serverKey))
    log_message("=====================================")

def check_in():
    now = datetime.now()
    month = now.strftime("%m")

    # 从JSON文件中读取数据
    with open('data.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
    distinct_id = data['distinct_id']
    # 从数据中获取用户数据列表
    users = data['users']

    for user in users:
        server_message = ""
        name = user['name']
        roleId = user['roleId']
        tokenraw = user['tokenraw']
        userId = user['userId']
        devcode = user['devCode']

        log_message(name+"开始签到")
        # 鸣潮签到
        
        server_message = server_message+now.strftime("%Y-%m-%d")+" "+name+"签到\n\n"
        game_message, succ = game_check_in(tokenraw, roleId, userId, month)
        if not succ:
            server_message += "今天的奖励为：" + game_message + "\n\n"
            log_message("签到失败或没有奖励：" + game_message)
            return server_message
        server_message = server_message+"今天的奖励为："+game_message+ "\n\n"
        log_message("鸣潮签到成功，今天的奖励为" + game_message)
        time.sleep(2)

        # 库街区签到
        server_message=server_message+KuroBBS_sign_in(tokenraw, devcode,distinct_id)
        log_message(name+"签到成功")
        return server_message




def schedule_random_task():
    with open('data.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
    start_hour = data['start_hour']
    end_hour = data['end_hour']

    # 生成当天6:00到9:00之间的随机时间
    start_time = datetime.now().replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end_time = datetime.now().replace(hour=end_hour, minute=0, second=0, microsecond=0)
    # test_time = datetime.now() + timedelta(min=15)

    random_seconds = random.randint(0, int((end_time - start_time).total_seconds()))
    random_time = start_time + timedelta(seconds=random_seconds)

    # print(f"今天的任务将在 {test_time.strftime('%H:%M:%S')} 执行")
    print(f"今天的任务将在 {random_time.strftime('%H:%M:%S')} 执行")

    # 在生成的随机时间调度任务
    schedule_time = random_time.strftime('%H:%M')
    # schedule_time = test_time.strftime('%H:%M')
    schedule.every().day.at(schedule_time).do(job)





if __name__ == "__main__":
    print("job start")
    # 每天调用一次 schedule_random_task 来设置第二天的任务
    schedule.every().day.at("00:00").do(schedule_random_task)

    # 立即运行一次以设置当天的任务
    schedule_random_task()
    while True:
        schedule.run_pending()
        time.sleep(1)
