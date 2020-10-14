import requests
import re
import time
import pymysql
import urllib3
import datetime
from bs4 import BeautifulSoup

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
    try:
        # 创建数据库链接
        db = pymysql.connect('localhost', 'tg', '123456', 'TGanalysis')
        cursor = db.cursor()

        # 查询已结束的比赛数据并记录结果
        cursor.execute("select * from halfdata where resultscore is null or resultscore=''")
        allgamesodds = cursor.fetchall()


        # 获取当前时间
        nowtimeday = (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
        # 根据结果检查当前列表并导出数据
        overgame = tg.get('https://m3.tg6666.net/gameresult.php?day={}'.format(nowtimeday), verify=False)
        # overgame = tg.get('https://m3.tg6666.net/gameresult.php?day=2020-07-17', verify=False)
        gameresultlistsoup = BeautifulSoup(overgame.text, 'html.parser')
        gameresultlist = gameresultlistsoup.select('.game_list.v1')
        gamescorelist = gameresultlistsoup.select('.trade_detail')
        # 获取已结束比赛列表并对比拿到比赛数据
        for gamesodd in allgamesodds:
            gamename1 = re.findall('(.*)v', gamesodd[1])[0].strip()
            gamename2 = re.findall('v(.*)', gamesodd[1])[0].strip()
            for game in gameresultlist:
                index = gameresultlist.index(game)
                if gamename1 in game.text and gamename2 in game.text:
                    # 半场结果
                    halfresult = gamescorelist[index].select('.trade_cell.trade_border_bottom.color_red')[1].text
                    # 结果写入
                    cursor.execute(
                        "update halfdata set resultscore='{}' where id={}".format(halfresult,gamesodd[0]))
                    db.commit()


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
            login = tg.post('https://m3.tg6666.net/other/login.php', data={'account': account, 'pwd': pwd},
                            verify=False)
            continue


        for market in marketlist[:5]:
            # 获取比赛请求链接
            parameter = []
            for para in re.findall("\((.*)\)", market.attrs['onclick'])[0].split(','):
                parameter.append(para[1:-1])
            gamedetail = tg.get(
                'https://m3.tg6666.net/marketorder.php?gc12={}&gameid={}&time={}&name={}&competitionname={}&status_id={}'.format(
                    parameter[0], parameter[1], parameter[2], parameter[3], parameter[4], parameter[5]))
            gamedetailsoup = BeautifulSoup(gamedetail.text, 'html.parser')

            # 记录当前比赛所有半场赔率数据
            halfscore_odds_txt = ''
            halfscorelist = gamedetailsoup.select('.content-2 .content_row .content_cell.table_option')
            halfoddslist = gamedetailsoup.select('.content-2 .content_row .content_cell.cell_red.table_rate')
            for i in range(len(halfscorelist)):
                halfscore_odds_txt = halfscore_odds_txt + halfscorelist[i].text.strip() + ':' + halfoddslist[
                    i].text + ','

            # 近期比分数据
            pkrecord = tg.get('https://m3.tg6666.net/pkRecords.php?gametime={}&gamename={}'.format(parameter[2], parameter[3]),
                              verify=False)
            pkrecordsoup = BeautifulSoup(pkrecord.text, 'html.parser')
            pklists = pkrecordsoup.select('.table_body_row.battle_record.type4')
            pkhalf = False  # 是否符合需求，半场比分总值大于2
            for pklist in pklists:
                if '2020' in pklist.text or '2019' in pklist.text:
                    halfbifen = pklist.select('.score')[0].text
                    halfbifenadd = int(halfbifen[-3]) - int(halfbifen[-1])
                    if halfbifenadd >= 2:  # 判断是否半场比分总值始终大于等于2
                        pkhalf = True
                    else:
                        pkhalf = False
                        break
            # 检查是否存在重复内容，不导入重复内容
            cursor.execute("select id from halfdata where gamename='{}'".format(parameter[3]))
            is_exist = cursor.fetchall()
            if pkhalf and len(is_exist) == 0:
                cursor.execute(
                    "insert into halfdata(gamename, buyscore) value ('{}', '{}') ".format(parameter[3],'0-0'))
                db.commit()
        db.close()
        # 完成一次记录等待
        print('等待10分钟后继续执行...-nowtime:{}'.format(datetime.datetime.now().strftime(
                    '%y-%m-%d %H:%M:%S')))
        time.sleep(600)
    except:
        print('故障等待5分钟后继续执行...-nowtime:{}'.format(datetime.datetime.now().strftime(
            '%y-%m-%d %H:%M:%S')))
        time.sleep(300)
        # 登录系统
        login_page = tg.get('https://m3.tg6666.net/login.php', verify=False)
        login = tg.post('https://m3.tg6666.net/other/login.php', data={'account': account, 'pwd': pwd},
                        verify=False)
        continue