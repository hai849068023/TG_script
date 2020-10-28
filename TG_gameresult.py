import requests
import re
import time
import pymysql
import urllib3
import smtplib
import datetime
import random
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

urllib3.disable_warnings()
tg = requests.session()

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

# 循环列表
while True:
    # 创建数据库链接
    db = pymysql.connect('localhost', 'root', 'root', 'TGanalysis')
    cursor = db.cursor()

    # 获取当前时间
    nowtimeday = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
    # 根据结果检查当前列表并导出数据
    overgame = tg.get('https://m1.tg6000.net/gameresult.php?day={}'.format(nowtimeday), verify=False)
    gameresultlistsoup = BeautifulSoup(overgame.text, 'html.parser')
    allgamename = gameresultlistsoup.select('.game_list.v1')
    allgameoresult = gameresultlistsoup.select('.trade_detail')
    for game in allgamename:
        index = allgamename.index(game)
        gamename = game.select('.game_name')[0].text
        gameteam = game.select('.game_team')[0].text
        allscore = allgameoresult[index].select('.trade_cell.trade_border_bottom.color_red')[0].text
        halfscore = allgameoresult[index].select('.trade_cell.trade_border_bottom.color_red')[1].text
        if allscore != '':
            cursor.execute(
                "insert into gameresult(gamename, gameteam, allscore, halfscore) value ('{}', '{}', '{}', '{}') ".format(
                    gamename, gameteam, allscore, halfscore))
            db.commit()
    db.close()
