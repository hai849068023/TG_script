import requests
import re
import time
import pymysql
import urllib3
import datetime
from bs4 import BeautifulSoup
from TG_Base import TG_base

urllib3.disable_warnings()
tg = requests.session()

# 登录系统
with open('secret.txt', 'r') as f:
    secret = f.readlines()
    account = secret[0].strip()
    pwd = secret[1]
login_page = tg.get('https://m3.tg6666.net/login.php', verify=False)
login = tg.post('https://m3.tg6666.net/other/login.php', data={'account': account, 'pwd': pwd},
                verify=False)
while True:

    # 获取所有比赛记录并分析记录
    market = tg.get('https://m3.tg6666.net/market.php', verify=False)
    marketsoup = BeautifulSoup(market.text, 'html.parser')
    marketlist = marketsoup.select('.content-1 li')

    # 如果当前比赛为空，则异常等待稍后继续
    if len(marketlist) == 0:
        print('故障等待5分钟后继续执行...-nowtime:{}'.format(datetime.datetime.now().strftime(
            '%y-%m-%d %H:%M:%S')))
        time.sleep(300)
        # 登录系统
        login_page = tg.get('https://m3.tg6666.net/login.php', verify=False)
        login = tg.post('https://m3.tg6666.net/other/login.php', data={'account': 'GFE778', 'pwd': 'hai214810'},
                        verify=False)
        continue

    # 遍历列表
    for market in marketlist[:5]:
        # 获取比赛请求链接
        parameter = []
        for para in re.findall("\((.*)\)", market.attrs['onclick'])[0].split(','):
            parameter.append(para[1:-1])
        gamedetail = tg.get(
            'https://m3.tg6666.net/marketorder.php?gc12={}&gameid={}&time={}&name={}&competitionname={}&status_id={}'.format(
                parameter[0], parameter[1], parameter[2], parameter[3], parameter[4], parameter[5]))
        gamedetailsoup = BeautifulSoup(gamedetail.text, 'html.parser')

        # 获得半场交易量数据
