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
    # 连接数据库
    db = pymysql.connect("localhost", "root", "root", "TGanalysis")
    cursor = db.cursor()

    # 检查历史结果
    cursor.execute("select id,gamename from muli_buy where result='' or result is null")
    noresultgame = cursor.fetchall()

    gameresult = tg.get('https://m1.tg6000.net/gameresult.php', verify=False)
    gameresultsoup = BeautifulSoup(gameresult.text, 'html.parser')
    gameresultlist = gameresultsoup.select('.game_list.v1')
    gamescorelist = gameresultsoup.select('.trade_detail')
    # 获取已结束比赛列表并对比拿到比赛数据
    for gamesodd in noresultgame:
        gamename1 = re.findall('(.*)v', gamesodd[1])[0].strip()
        gamename2 = re.findall('v(.*)', gamesodd[1])[0].strip()
        for game in gameresultlist:
            index = gameresultlist.index(game)
            if gamename1 in game.text and gamename2 in game.text:
                # 半场结果
                halfresult = gamescorelist[index].select('.trade_cell.trade_border_bottom.color_red')[1].text
                # 结果写入
                cursor.execute(
                    "update muli_buy set result='{}' where id={}".format(halfresult, gamesodd[0]))
                db.commit()

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
    for market in marketlist[:5]:
        # 获取比赛请求链接
        parameter = []
        for para in re.findall("\((.*)\)", market.attrs['onclick'])[0].split(','):
            parameter.append(para[1:-1])
        gamedetail = tg.get(
            'https://m1.tg6000.net/marketorder.php?gc12={}&gameid={}&time={}&name={}&competitionname={}&status_id={}'.format(
                parameter[0], parameter[1], parameter[2], parameter[3], parameter[4], parameter[5]))
        gamedetailsoup = BeautifulSoup(gamedetail.text, 'html.parser')

        # 获取当前比赛的赔率
        allbodan = gamedetailsoup.select('.content-1 .content_row')
        b0_3 = allbodan[3].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
        b1_3 = allbodan[7].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
        b3_0 = allbodan[12].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
        b3_1 = allbodan[13].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
        blist = {}
        blist['0-3'] = float(b0_3) if b0_3 != '' else 0
        blist['1-3'] = float(b1_3) if b1_3 != '' else 0
        blist['3-0'] = float(b3_0) if b3_0 != '' else 0
        blist['3-1'] = float(b3_1) if b3_1 != '' else 0
        blistsort = sorted(blist.items(), key=lambda item: item[1])

        # 购买比分
        buyscore = blistsort[1]
        if buyscore[1] != 0:
            # 检查是否存在重复内容，不导入重复内容
            cursor.execute("select id from muli_buy where gamename='{}'".format(parameter[3]))
            is_exist = cursor.fetchall()
            if len(is_exist) == 0:
                cursor.execute(
                    "insert into muli_buy(gamename, buyscore, odd) value ('{}', '{}', '{}') ".format(parameter[3],
                                                                                                     buyscore[0], buyscore[1]))
                db.commit()
            db.close()
        else:
            continue
    #　十分钟一次循环
    print('完成记录，10分钟后继续... {}'.format(datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))
    time.sleep(600)


        pass
