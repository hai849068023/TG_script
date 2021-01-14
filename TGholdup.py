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
login_page = tg.get('https://m1.tg6666.net/login.php', verify=False)
login = tg.post('https://m1.tg6666.net/other/login.php', data={'account': account, 'pwd': pwd},
                verify=False)

while True:
    try:
        # 获得当前时间并判断是否大于八点
        nowtimehour = time.localtime().tm_hour
        if nowtimehour >= 8:
            # 获取当前时间前一天的时间
            nowtimeday = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')

            # 连接数据库
            db = pymysql.connect("localhost", "root", "root", "TGanalysis")
            cursor = db.cursor()

            # 检查历史结果
            cursor.execute("select id,gamename from muli_buy where result='' or result is null")
            noresultgame = cursor.fetchall()

            overgame = tg.get('https://m1.tg6666.net/gameresult.php?day={}'.format(nowtimeday), verify=False)
            gameresultsoup = BeautifulSoup(overgame.text, 'html.parser')
            gameresultlist = gameresultsoup.select('.game_list.v1')
            gamescorelist = gameresultsoup.select('.trade_detail')
            # 获取已结束比赛列表并对比拿到比赛数据
            for gamesodd in noresultgame:
                gamename1 = re.findall('(.*)v', gamesodd[1])[0].strip()
                gamename2 = re.findall('v(.*)', gamesodd[1])[0].strip()
                for game in gameresultlist:
                    index = gameresultlist.index(game)
                    if gamename1 in game.text and gamename2 in game.text:
                        # 全场结果
                        allresult = gamescorelist[index].select('.trade_cell.trade_border_bottom.color_red')[0].text
                        # 结果写入
                        cursor.execute(
                            "update muli_buy set result='{}' where id={}".format(allresult, gamesodd[0]))
                        db.commit()

        # # 获取下单列表记录
        # orderrecord = tg.get('https://m1.tg6666.net/orderinfo.php', verify=False)
        # orderrecordsoup = BeautifulSoup(orderrecord.text, 'html.parser')
        #
        # # 获取余额
        # balance = float(orderrecordsoup.select('.money')[0].text)
        #
        # # 交易金额
        # if orderrecordsoup.select('.trade_amount_num')[0].text != '':
        #     trading = float(orderrecordsoup.select('.trade_amount_num')[0].text)
        # else:
        #     trading = 0
        #
        # # 获取是否存在下单项
        # is_order = orderrecordsoup.select('.game_list.v1')
        #
        # # 如果没有余额并且没有订单记录则退出程序，如果有订单记录继续s
        # if balance + trading >= 200:
        #     # 发送邮件
        #     try:
        #         # 邮件发送代码
        #         ############################################################################
        #         receivers = ['18758277138@163.com']
        #         msg = MIMEText('当前账户余额{},可发起提现！/n 发送时间:{}'.format(balance + trading, datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))  # 邮件内容
        #         msg['Subject'] = '提现提醒'  # 邮件主题
        #         msg['From'] = '18655109810@163.com'  # 发送者账号
        #         msg['To'] = '18758277138@163.com'  # 接收者账号列表
        #         smtObj = smtplib.SMTP('smtp.163.com')
        #         smtObj.login('18655109810@163.com', 'hai214810')
        #         smtObj.sendmail('18655109810@163.com', receivers, msg.as_string())
        #         print('邮件发送成功')
        #     ###########################################################################
        #     except smtplib.SMTPException:
        #         print('邮件发送失败')
        #
        # if len(is_order) > 0 and balance < 100:
        #     print('待结算，等待10分钟...{}'.format(datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))
        #     time.sleep(600)
        #     continue
        # # 结束执行
        # if balance < 100 and len(is_order) == 0:
        #     print('gameover,等待拯救！{}'.format(datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))
        #     time.sleep(600)
        #     continue

        # 活动市场列表
        markets = tg.get('https://m1.tg6666.net/market.php', verify=False)
        marketsoup = BeautifulSoup(markets.text, 'html.parser')
        marketlist = marketsoup.select('.content-1 li')

        # 如果当前比赛为空，则异常等待稍后继续
        if len(marketlist) == 0:
            print('维护或故障等待5分钟后继续执行...-nowtime:{}'.format(datetime.datetime.now().strftime(
                '%y-%m-%d %H:%M:%S')))
            time.sleep(300)
            # 登录系统
            login_page = tg.get('https://m1.tg6666.net/login.php', verify=False)
            login = tg.post('https://m1.tg6666.net/other/login.php', data={'account': account, 'pwd': pwd},
                            verify=False)
            continue

        # 检索合适的比赛数据
        # market = random.choice(marketlist[:5])
        for market in marketlist[:5]:
            # 获取比赛请求链接
            parameter = []
            for para in re.findall("\((.*)\)", market.attrs['onclick'])[0].split(','):
                parameter.append(para[1:-1])
            gamedetail = tg.get(
                'https://m1.tg6666.net/marketorder.php?gc12={}&gameid={}&time={}&name={}&competitionname={}&status_id={}'.format(
                    parameter[0], parameter[1], parameter[2], parameter[3], parameter[4], parameter[5]))
            gamedetailsoup = BeautifulSoup(gamedetail.text, 'html.parser')

            # 获取当前比赛的赔率
            allbodan = gamedetailsoup.select('.content-1 .content_row')
            try:
                b0_0 = allbodan[0].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
                b0_1 = allbodan[1].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
                b0_2 = allbodan[2].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
                b0_3 = allbodan[3].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
                b1_0 = allbodan[4].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
                b1_1 = allbodan[5].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
                b1_2 = allbodan[6].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
                b1_3 = allbodan[7].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
                b2_0 = allbodan[8].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
                b2_1 = allbodan[9].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
                b2_2 = allbodan[10].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
                b2_3 = allbodan[11].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
                b3_0 = allbodan[12].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
                b3_1 = allbodan[13].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
                b3_2 = allbodan[14].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
                b3_3 = allbodan[15].select('.content_cell.cell_red.table_rate')[0].text.strip()[:-1]
            except:
                continue
            else:
                blist = {}
                blist['0-0'] = float(b0_0) if b0_0 != '' else 0
                blist['0-1'] = float(b0_1) if b0_1 != '' else 0
                blist['0-2'] = float(b0_2) if b0_2 != '' else 0
                blist['0-3'] = float(b0_3) if b0_3 != '' else 0
                blist['1-0'] = float(b1_0) if b1_0 != '' else 0
                blist['1-1'] = float(b1_1) if b1_1 != '' else 0
                blist['1-2'] = float(b1_2) if b1_2 != '' else 0
                blist['1-3'] = float(b1_3) if b1_3 != '' else 0
                blist['2-0'] = float(b2_0) if b2_0 != '' else 0
                blist['2-1'] = float(b2_1) if b2_1 != '' else 0
                blist['2-2'] = float(b2_2) if b2_2 != '' else 0
                blist['2-3'] = float(b2_3) if b2_3 != '' else 0
                blist['3-0'] = float(b3_0) if b3_0 != '' else 0
                blist['3-1'] = float(b3_1) if b3_1 != '' else 0
                blist['3-2'] = float(b3_2) if b3_2 != '' else 0
                blist['3-3'] = float(b3_3) if b3_3 != '' else 0

                blistsort = sorted(blist.items(), key=lambda item: item[1])

                # 近期比分数据
                winner = '' # home表示主队强 guest表示客队强
                pkrecord = tg.get(
                    'https://m1.tg6666.net/pkRecords.php?gametime={}&gamename={}'.format(parameter[2], parameter[3]),
                    verify=False)
                pkrecordsoup = BeautifulSoup(pkrecord.text, 'html.parser')
                # 获取今年的比赛记录并记录
                pklists = pkrecordsoup.select('.table_body_row.battle_record.type4')
                if len(pklists) > 0 and '2020' in pklists[0].text:
                    home_team = pklists[0].select('.home_team')[0].text
                    away_team = pklists[0].select('.away_team')[0].text
                    allbifen1 = pklists[0].select('.score')[0].text[0]
                    allbifen2 = pklists[0].select('.score')[0].text[2]
                    halfbifen1 = pklists[0].select('.score')[0].text[-3]
                    halfbifen2 = pklists[0].select('.score')[0].text[-1]
                    allpower = int(allbifen1) - int(allbifen2)
                    halfpower = int(halfbifen1) - int(halfbifen2)
                    if allpower > 0 and halfpower >= 0:
                        winner = 'home'
                    else:
                       winner = 'guest'
                else:
                    continue

                # 购买比分
                buyscore = blistsort[3]
                buywin = int(buyscore[0][0]) - int(buyscore[0][-1])
                if buyscore[1] != 0 and ((winner == 'home' and buywin < 0) or (winner == 'guest' and buywin > 0)):
                    # buglist = {'0-3':2, '1-3':5, '3-0':6, '3-1':7}
                    # # 获取购买数据并下单操作
                    # allodds = gamedetailsoup.select('.content-1 .content_row')
                    # nextgetdata = allodds[buglist[buyscore[0]]].attrs['onclick']
                    # allurldata = nextgetdata.split(',')
                    # allurldatalist = []  # order接口参数列表
                    # for d in allurldata:
                    #     allurlvalue = re.search("'(.*)'", d).group(1)
                    #     allurldatalist.append(allurlvalue)
                    # # 定义一个参数字典
                    # orderdata = {}
                    # orderdata['c2betorder[0][selectname]'] = allurldatalist[0]
                    # orderdata['c2betorder[0][time]'] = allurldatalist[1]
                    # orderdata['c2betorder[0][gameid]'] = allurldatalist[2]
                    # orderdata['c2betorder[0][markettype]'] = allurldatalist[3]
                    # orderdata['c2betorder[0][gamename]'] = allurldatalist[4]
                    # orderdata['c2betorder[0][marketname]'] = allurldatalist[6]
                    # orderdata['c2betorder[0][Rate]'] = allurldatalist[7]
                    # orderdata['c2betorder[0][Bet]'] = allurldatalist[8]
                    # orderdata['c2betorder[0][BetType]'] = 'L'
                    # orderdata['c2betorder[0][MarketId]'] = allurldatalist[5]
                    # orderdata['c2betorder[0][SelectionId]'] = allurldatalist[12]
                    # orderdata['c2betorder[0][betfairori]'] = allurldatalist[13]
                    # orderdata['c2betorder[0][percent]'] = allurldatalist[14]
                    # orderdata['c2betorder[0][chk]'] = 'order'
                    # orderdata['c2betorder[0][category]'] = allurldatalist[15]
                    # orderdata['c2betorder[0][selectrateL1]'] = allurldatalist[9]
                    # orderdata['c2betorder[0][sel]'] = ''
                    # orderdata['c2betorder[0][gc12]'] = allurldatalist[11]
                    # orderdata['c2betorder[0][pawben]'] = allurldatalist[16]
                    # orderdata['c2betorder[0][selectmoneyL1]'] = allurldatalist[17]
                    # # 请求订单接口
                    # get_order = tg.post('https://m1.tg6666.net/order.php', data=orderdata)
                    # ordersoup = BeautifulSoup(get_order.text, 'html.parser')
                    # createdata = {}  # 定义订单请求数组
                    # createdata['c2betorder[0][handicap]'] = ordersoup.select('#handicap')[0].attrs['value']
                    # createdata['c2betorder[0][inplay]'] = ordersoup.select('#inplay')[0].attrs['value']
                    # createdata['c2betorder[0][selectname]'] = ordersoup.select('#selectname')[0].attrs['value']
                    # createdata['c2betorder[0][time]'] = ordersoup.select('#time')[0].attrs['value']
                    # createdata['c2betorder[0][gameid]'] = ordersoup.select('#gameid')[0].attrs['value']
                    # createdata['c2betorder[0][markettype]'] = ordersoup.select('#markettype')[0].attrs['value']
                    # createdata['c2betorder[0][gamename]'] = ordersoup.select('#gamename')[0].attrs['value']
                    # createdata['c2betorder[0][marketname]'] = ordersoup.select('#marketname_st')[0].attrs[
                    #     'value']
                    # createdata['c2betorder[0][Rate]'] = ordersoup.select('#Rate')[0].attrs['value']
                    # createdata['c2betorder[0][Bet]'] = '{}'.format(balance)
                    # createdata['c2betorder[0][BetType]'] = ordersoup.select('#BetType')[0].attrs['value']
                    # createdata['c2betorder[0][MarketId]'] = ordersoup.select('#MarketId')[0].attrs['value']
                    # createdata['c2betorder[0][SelectionId]'] = ordersoup.select('#SelectionId')[0].attrs[
                    #     'value']
                    # createdata['c2betorder[0][betfairori]'] = ordersoup.select('#betfairori')[0].attrs['value']
                    # createdata['c2betorder[0][percent]'] = ordersoup.select('#percent')[0].attrs['value']
                    # createdata['c2betorder[0][chk]'] = 'order'
                    # createdata['c2betorder[0][selectrateL1]'] = ordersoup.select('#selectrateL1')[0].attrs[
                    #     'value']
                    # createdata['c2betorder[0][category]'] = ordersoup.select('#category')[0].attrs['value']
                    # createdata['c2betorder[0][sel]'] = ordersoup.select('#sel')[0].attrs['value']
                    # createdata['c2betorder[0][gc12]'] = ordersoup.select('#gc12')[0].attrs['value']
                    #
                    # # 　佛祖保佑
                    # #                             _ooOoo_
                    # #                            o8888888o
                    # #                            88" . "88
                    # #                            (| -_- |)
                    # #                            O\  =  /O
                    # #                         ____/`---'\____
                    # #                       .'  \\|     |//  `.
                    # #                      /  \\|||  :  |||//  \
                    # #                     /  _||||| -:- |||||-  \
                    # #                     |   | \\\  -  /// |   |
                    # #                     | \_|  ''\---/''  |   |
                    # #                     \  .-\__  `-`  ___/-. /
                    # #                   ___`. .'  /--.--\  `. . __
                    # #                ."" '<  `.___\_<|>_/___.'  >'"".
                    # #               | | :  `- \`.;`\ _ /`;.`/ - ` : | |
                    # #               \  \ `-.   \_ __\ /__ _/   .-` /  /
                    # #          ======`-.____`-.___\_____/___.-`____.-'======
                    # #                             `=---='
                    # #         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                    # #                       　　　拈花一指定乾坤
                    # createorder = tg.post('https://m1.tg6666.net/order_finish.php', data=createdata)
                    # if '下注成功' in createorder.text:
                    #     print('购买成功! 10分钟后继续... {}'.format(datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))
                    #     time.sleep(600)
                    # else:
                    #     print('购买失败！问题： {}'.format(createorder.text))

                    # 检查是否存在重复内容，不导入重复内容
                    cursor.execute("select id from muli_buy where gamename='{}'".format(parameter[3]))
                    is_exist = cursor.fetchall()
                    if len(is_exist) == 0:
                        cursor.execute(
                            "insert into muli_buy(gamename, b0_0, b0_1, b0_2, b0_3, b1_0, b1_1, b1_2, b1_3, b2_0, b2_1, b2_2, b2_3, b3_0, b3_1, b3_2, b3_3, buyscore, odd) value ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}') ".format(
                                parameter[3], b0_0, b0_1, b0_2, b0_3, b1_0, b1_1, b1_2, b1_3, b2_0, b2_1, b2_2, b2_3, b3_0,
                                b3_1, b3_2, b3_3, buyscore[0], buyscore[1]))
                        db.commit()
                else:
                    continue
        db.close()

        # 　十分钟一次循环
        print('完成记录，10分钟后继续... {}'.format(datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))
        time.sleep(600)

    except Exception as f:
        print(f)
        print('故障等待5分钟后继续执行...-nowtime:{}'.format(datetime.datetime.now().strftime(
            '%y-%m-%d %H:%M:%S')))
        time.sleep(300)
        # 登录系统
        login_page = tg.get('https://m1.tg6666.net/login.php', verify=False)
        login = tg.post('https://m1.tg6666.net/other/login.php', data={'account': account, 'pwd': pwd},
                        verify=False)
        continue
