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
        cursor.execute("select * from gamedata where gameresult is null or gameresult=''")
        allgamesodds = cursor.fetchall()

        # 获取当前时间
        nowtimeday = (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime('%Y-%m-%d')

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
                    allresult = gamescorelist[index].select('.trade_cell.trade_border_bottom.color_red')[0].text
                    # 半场结果
                    halfresult = gamescorelist[index].select('.trade_cell.trade_border_bottom.color_red')[1].text
                    # 结果写入
                    cursor.execute(
                        "update gamedata set gameresult='{}', gamehalfresult='{}' where id={}".format(allresult, halfresult,
                                                                                                      gamesodd[0]))
                    db.commit()

        # 活动市场列表
        market = tg.get('https://m3.tg6666.net/market.php', verify=False)
        marketsoup = BeautifulSoup(market.text, 'html.parser')
        marketlist = marketsoup.select('.content-2 li')
        if len(marketlist) == 0:
            print('故障等待5分钟后继续执行...-nowtime:{}'.format(datetime.datetime.now().strftime(
                '%y-%m-%d %H:%M:%S')))
            time.sleep(300)
            # 登录系统
            login_page = tg.get('https://m3.tg6666.net/login.php', verify=False)
            login = tg.post('https://m3.tg6666.net/other/login.php', data={'account': 'GFE778', 'pwd': 'hai214810'},
                            verify=False)
            continue

        # 所有比赛赔率信息记录与近期比分
        run_times = 0
        for market in marketlist:
            if run_times >= 5:
                break
            # 获取比赛请求链接
            parameter = []
            for para in re.findall("\((.*)\)", market.attrs['onclick'])[0].split(','):
                parameter.append(para[1:-1])
            gamedetail = tg.get(
                'https://m3.tg6666.net/marketorder.php?gc12={}&gameid={}&time={}&name={}&competitionname={}&status_id={}'.format(
                    parameter[0], parameter[1], parameter[2], parameter[3], parameter[4], parameter[5]))
            gamedetailsoup = BeautifulSoup(gamedetail.text, 'html.parser')

            # 记录当前比赛所有赔率
            score_odds_txt = ''
            scorelist = gamedetailsoup.select('.content-1 .content_row .content_cell.table_option')
            oddslist = gamedetailsoup.select('.content-1 .content_row .content_cell.cell_red.table_rate')

            # 记录当前比赛所有半场赔率数据
            halfscore_odds_txt = ''
            halfscorelist = gamedetailsoup.select('.content-2 .content_row .content_cell.table_option')
            halfoddslist = gamedetailsoup.select('.content-2 .content_row .content_cell.cell_red.table_rate')

            for i in range(len(scorelist)):
                score_odds_txt = score_odds_txt + scorelist[i].text.strip() + ':' + oddslist[i].text + ','
            for i in range(len(halfscorelist)):
                halfscore_odds_txt = halfscore_odds_txt + halfscorelist[i].text.strip() + ':' + halfoddslist[
                    i].text + ','

            # 近期比分数据
            pkrecord = tg.get('https://m3.tg6666.net/pkRecords.php?gametime={}&gamename={}'.format(parameter[2], parameter[3]), verify=False)
            pkrecordsoup = BeautifulSoup(pkrecord.text, 'html.parser')
            # 获取今年的比赛记录并记录
            pklists = pkrecordsoup.select('.table_body_row.battle_record.type4')
            if len(pklists) > 0 and ('2020' in pklists[0].text or '2019' in pklists[0].text):
                home_team = pklists[0].select('.home_team')[0].text
                away_team = pklists[0].select('.away_team')[0].text
                allbifen1 = pklists[0].select('.score')[0].text[0]
                allbifen2 = pklists[0].select('.score')[0].text[2]
                halfbifen1 = pklists[0].select('.score')[0].text[-3]
                halfbifen2 = pklists[0].select('.score')[0].text[-1]
                allpower = int(allbifen1) - int(allbifen2)
                halfpower = int(halfbifen1) - int(halfbifen2)
                # 检查是否存在重复内容，不导入重复内容
                cursor.execute("select id from gamedata where gamename='{}'".format(parameter[3]))
                is_exist = cursor.fetchall()
                if len(is_exist) == 0:
                    if allpower > 0 and halfpower > 0:
                        cursor.execute(
                            "insert into gamedata(gamename, gameodds, gamehalfodds, gamestarttime, morepower, add_time) value ('{}', '{}', '{}','{}','{}', '{}') ".format(
                                parameter[3],
                                score_odds_txt, halfscore_odds_txt, parameter[2], home_team,
                                datetime.datetime.now().strftime(
                                    '%y-%m-%d %H:%M:%S')))
                    else:
                        cursor.execute(
                            "insert into gamedata(gamename, gameodds, gamehalfodds, gamestarttime, morepower, add_time) value ('{}', '{}', '{}','{}','{}', '{}') ".format(
                                parameter[3],
                                score_odds_txt, halfscore_odds_txt, parameter[2], away_team,
                                datetime.datetime.now().strftime(
                                    '%y-%m-%d %H:%M:%S')))
            else:
                # 检查是否存在重复内容，不导入重复内容
                cursor.execute("select id from gamedata where gamename='{}'".format(parameter[3]))
                is_exist = cursor.fetchall()
                if len(is_exist) == 0:
                    cursor.execute(
                            "insert into gamedata(gamename, gameodds, gamehalfodds, gamestarttime, add_time) value ('{}', '{}', '{}','{}', '{}') ".format(
                                parameter[3],
                                score_odds_txt, halfscore_odds_txt, parameter[2],
                                datetime.datetime.now().strftime(
                                    '%y-%m-%d %H:%M:%S')))
            db.commit()
            run_times += 1
        db.close()
        print('等待10分钟后继续执行...-nowtime:{}'.format(datetime.datetime.now().strftime(
            '%y-%m-%d %H:%M:%S')))
        time.sleep(600)
    except:
        print('故障等待5分钟后继续执行...-nowtime:{}'.format(datetime.datetime.now().strftime(
            '%y-%m-%d %H:%M:%S')))
        time.sleep(300)
        # 登录系统
        login_page = tg.get('https://m3.tg6666.net/login.php', verify=False)
        login = tg.post('https://m3.tg6666.net/other/login.php', data={'account': 'GFE778', 'pwd': 'hai214810'},
                        verify=False)
        continue