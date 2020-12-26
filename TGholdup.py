import requests
import re
import time
import urllib3
import datetime
import random
import pymysql
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

urllib3.disable_warnings()
tg = requests.session()


# 登录系统
with open('secret.txt', 'r') as f:
    secret = f.readlines()
    account = secret[0].strip()
    pwd = secret[1]
login_page = tg.get('https://m1.tg6000.net/login.php', verify=False)
login = tg.post('https://m1.tg6000.net/other/login.php', data={'account': account, 'pwd': pwd},
                verify=False)


while True:
    # 活动市场列表
    markets = tg.get('https://m1.tg6000.net/market.php', verify=False)
    marketsoup = BeautifulSoup(markets.text, 'html.parser')
    marketlist = marketsoup.select('.content-1 li')

    # 如果当前比赛为空，则异常等待稍后继续
    if len(marketlist) == 0:
        print('维护或故障等待5分钟后继续执行...-nowtime:{}'.format(datetime.datetime.now().strftime(
            '%y-%m-%d %H:%M:%S')))
        time.sleep(300)
        # 登录系统
        login_page = tg.get('https://m1.tg6000.net/login.php', verify=False)
        login = tg.post('https://m1.tg6000.net/other/login.php', data={'account': account, 'pwd': pwd},
                        verify=False)
        continue

    # 检索合适的比赛数据
    for market in marketlist:
        # 获取比赛请求链接
        parameter = []
        for para in re.findall("\((.*)\)", market.attrs['onclick'])[0].split(','):
            parameter.append(para[1:-1])
        gamedetail = tg.get(
            'https://m1.tg6000.net/marketorder.php?gc12={}&gameid={}&time={}&name={}&competitionname={}&status_id={}'.format(
                parameter[0], parameter[1], parameter[2], parameter[3], parameter[4], parameter[5]))
        gamedetailsoup = BeautifulSoup(gamedetail.text, 'html.parser')

        # 计算当前game情况给出结果

-