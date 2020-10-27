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
        db = pymysql.connect('localhost', 'root', 'root', 'TGanalysis')
        cursor = db.cursor()

        # 查询已结束的比赛数据并记录结果
        cursor.execute("select * from tradingdata where resultscore is null or resultscore=''")
        allgamesodds = cursor.fetchall()

        # 获取当前时间
        nowtimeday = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
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
                    # 全场结果
                    allresult = gamescorelist[index].select('.trade_cell.trade_border_bottom.color_red')[0].text
                    # 半场结果
                    halfresult = gamescorelist[index].select('.trade_cell.trade_border_bottom.color_red')[1].text
                    # 结果写入
                    cursor.execute(
                        "update tradingdata set resultscore='{}' where id={}".format(allresult, gamesodd[0]))
                    db.commit()

        # 获取所有比赛记录并分析记录
        market = tg.get('https://m3.tg6666.net/market.php', verify=False)
        marketsoup = BeautifulSoup(market.text, 'html.parser')
        marketlist = marketsoup.select('.content-1 li')

        # 如果当前比赛为空，则异常等待稍后继续
        if len(marketlist) == 0:
            print('维护或故障等待5分钟后继续执行...-nowtime:{}'.format(datetime.datetime.now().strftime(
                '%y-%m-%d %H:%M:%S')))
            time.sleep(300)
            # 登录系统
            login_page = tg.get('https://m3.tg6666.net/login.php', verify=False)
            login = tg.post('https://m3.tg6666.net/other/login.php', data={'account': account, 'pwd': pwd},
                            verify=False)
            continue

        # 遍历列表
        for market in marketlist:
            # # 获取保本元素
            # try:
            #     baoben = market.select('.guaranteedNomo')[0].text
            # except:
            #     continue
            # else:
            #     # 获取比赛请求链接
            #     parameter = []
            #     for para in re.findall("\((.*)\)", market.attrs['onclick'])[0].split(','):
            #         parameter.append(para[1:-1])
            #     gamedetail = tg.get(
            #         'https://m3.tg6666.net/marketorder.php?gc12={}&gameid={}&time={}&name={}&competitionname={}&status_id={}'.format(
            #             parameter[0], parameter[1], parameter[2], parameter[3], parameter[4], parameter[5]))
            #     gamedetailsoup = BeautifulSoup(gamedetail.text, 'html.parser')
            #
            #     is_baoben = gamedetailsoup.select('.guaranteed_detailNomo')[0].attrs['style']
            #     if is_baoben:
            #
            #     pass


            # 获取比赛请求链接
            parameter = []
            for para in re.findall("\((.*)\)", market.attrs['onclick'])[0].split(','):
                parameter.append(para[1:-1])
            gamedetail = tg.get(
                'https://m3.tg6666.net/marketorder.php?gc12={}&gameid={}&time={}&name={}&competitionname={}&status_id={}'.format(
                    parameter[0], parameter[1], parameter[2], parameter[3], parameter[4], parameter[5]))
            gamedetailsoup = BeautifulSoup(gamedetail.text, 'html.parser')

            # 获得全场场交易量数据
            tradingele = gamedetailsoup.select('.content-1 .chatShowIcon')[0]
            tradingdata = []
            for para in re.findall("\((.*)\)", tradingele.attrs['onclick'])[0].replace("'", '').split(','):
                tradingdata.append(para)
            # 如果全场比分没有则继续下一个
            if len(tradingdata) != 8:
                continue
            tdata = {
                'eventid': tradingdata[3],
                'marketid': tradingdata[4],
                'chartid': tradingdata[1],
                'competitionname': tradingdata[2],
                'gameName': tradingdata[0],
                'totaldealmoney': tradingdata[5] + ',' + tradingdata[6],
            }
            alltrading = tg.post('https://m3.tg6666.net/chatShow.php', data=tdata, verify=False)
            sts = re.findall('.*var st = \[(.*)\].*', alltrading.text)[0].split(',')
            stChartValues = re.findall('.*var stChartValue = \[(.*)\].*', alltrading.text)[0].split(',')
            # 　构建交易量数据结构
            trading_volume = ''
            for stChartValue in stChartValues:
                index = stChartValues.index(stChartValue)
                st = sts[index]
                score_st = stChartValue.replace("'", '') + ':' + st
                trading_volume += score_st + ','

            # 记录当前比赛所有全场场赔率数据
            allscore_odds = ''
            allscorelist = gamedetailsoup.select('.content-1 .content_row .content_cell.table_option')
            alloddslist = gamedetailsoup.select('.content-1 .content_row .content_cell.cell_red.table_rate')
            for i in range(len(allscorelist)):
                allscore_odds += allscorelist[i].text.strip() + ':' + alloddslist[
                    i].text + ','

            # 检查是否存在重复内容，不导入重复内容
            cursor.execute("select id from tradingdata where gamename='{}'".format(parameter[3]))
            is_exist = cursor.fetchall()
            if len(is_exist) == 0:
                cursor.execute(
                    "insert into tradingdata(gamename, trading_volume, allscore_odds) value ('{}', '{}', '{}')".format(
                        parameter[3],
                        trading_volume, allscore_odds))
            else:
                cursor.execute(
                    "update tradingdata set trading_volume='{}', allscore_odds='{}' where gamename='{}'".format(
                        trading_volume, allscore_odds, parameter[3]))
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
        