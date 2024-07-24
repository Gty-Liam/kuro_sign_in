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
    # 随机睡眠一段时间
    with open('conf/data.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
    sleep_start = data['sleep_start']
    sleep_end = data['sleep_end']
    sleep_time = random.randint(sleep_start, sleep_end)
    print("开始sleep: ", (sleep_time / 60), " 分钟")
    time.sleep(sleep_time)

    msg = check_in()

    with open('conf/data.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
    serverKey = data['serverKey']
    # 发送server酱通知
    log_message(sc_send("签到", msg, key=serverKey))
    log_message("=====================================")

def check_in():
    now = datetime.now()
    month = now.strftime("%m")

    # 从JSON文件中读取数据
    with open('conf/data.json', 'r', encoding="utf-8") as f:
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
    with open('conf/data.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
    start_hour = data['start_hour']

    # 8点执行脚本
    start_time = datetime.now().replace(hour=start_hour, minute=0, second=0, microsecond=0)
    print(f"任务将在每日 {start_time.strftime('%H:%M:%S')} 执行")

    # 在生成的随机时间调度任务
    schedule_time = start_time.strftime('%H:%M')
    schedule.every().day.at(schedule_time).do(job)


if __name__ == "__main__":
    print("job start")
    # 立即运行一次以设置当天的任务
    schedule_random_task()
    while True:
        schedule.run_pending()
        time.sleep(1)
