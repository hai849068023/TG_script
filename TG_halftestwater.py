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
login_page = tg.get('https://m3.tg6666.net/login.php', verify=False)
login = tg.post('https://m3.tg6666.net/other/login.php', data={'account': account, 'pwd': pwd},
                verify=False)

# 循环列表
while True:
    # try:
    # # 获取下单列表记录
    # orderrecord = tg.get('https://m3.tg6666.net/orderinfo.php', verify=False)
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
    # # 获取是否存在下单项
    # is_order = orderrecordsoup.select('.game_list.v1')
    # # 获得下单列表
    # order_list = []
    # for order in is_order:
    #     guest_name = re.findall('.*vs(.*)', order.text.strip())[0].strip()
    #     order_list.append(guest_name)
    #
    # # 如果没有余额并且没有订单记录则退出程序，如果有订单记录继续s
    # if balance + trading >= 200:
    #     # 发送邮件
    #     try:
    #         # 邮件发送代码
    #         ############################################################################
    #         receivers = ['18758277138@163.com']
    #         msg = MIMEText('余额满200,可发起提现. 等待一小时后继续执行！/n 发送时间:{}'.format(datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))  # 邮件内容
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
    #     time.sleep(3600)
    #     continue
    # if len(is_order) > 0 and balance < 100:
    #     print('待结算，等待10分钟...{}'.format(datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))
    #     time.sleep(600)
    #     continue
    # # 结束执行
    # if balance < 100 and len(is_order) == 0:
    #     print('gameover,等待拯救！{}'.format(datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))
    #     time.sleep(600)
    #     continue

    # 创建数据库链接
    db = pymysql.connect('localhost', 'root', 'root', 'TGanalysis')
    cursor = db.cursor()

    # 查询已结束的比赛数据并记录结果
    cursor.execute("select * from half_testwater where result_score is null or result_score=''")
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
                halfresult = gamescorelist[index].select('.trade_cell.trade_border_bottom.color_red')[0].text
                # 半场结果
                halfresult = gamescorelist[index].select('.trade_cell.trade_border_bottom.color_red')[1].text
                # 结果写入
                if halfresult:
                    nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute(
                        "update half_testwater set result_score='{}',updatetime='{}' where id={}".format(halfresult,
                                                                                                         nowtime,
                                                                                                         gamesodd[
                                                                                                             0]))
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
        halfscore_odds_txt = halfscore_odds_txt.split(',')[:-1]
        halfscore_odds_txted = sorted(halfscore_odds_txt,
                                      key=lambda x: float(re.findall('.*:(.*)', x.replace('\n', ''))[0][:-1]),
                                      reverse=True)
        number = random.choice(halfscore_odds_txted[:4]).replace('\n', '')
        buy_score = number[:5]
        gameodds = re.findall('.*:(.*)', number)[0]
        # 检查是否存在重复内容，不导入重复内容
        cursor.execute("select id from half_testwater where gamename='{}'".format(parameter[3]))
        is_exist = cursor.fetchall()
        if len(is_exist) == 0:
            nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "insert into half_testwater(gamename, buy_score, gameodds, updatetime) value ('{}', '{}', '{}', '{}')".format(
                    parameter[3],
                    buy_score, gameodds, nowtime))
            db.commit()

        # # 获取购买数据并下单操作
        # if buy_score != '':
        #     allodds = gamedetailsoup.select('.content-2 .content_row')
        #     for odd in allodds:
        #         if buy_score in odd.text:
        #             nextgetdata = odd.attrs['onclick']
        #             allurldata = nextgetdata.split(',')
        #             allurldatalist = []  # order接口参数列表
        #             for d in allurldata:
        #                 allurlvalue = re.search("'(.*)'", d).group(1)
        #                 allurldatalist.append(allurlvalue)
        #             # 定义一个参数字典
        #             orderdata = {}
        #             orderdata['c2betorder[0][selectname]'] = allurldatalist[0]
        #             orderdata['c2betorder[0][time]'] = allurldatalist[1]
        #             orderdata['c2betorder[0][gameid]'] = allurldatalist[2]
        #             orderdata['c2betorder[0][markettype]'] = allurldatalist[3]
        #             orderdata['c2betorder[0][gamename]'] = allurldatalist[4]
        #             orderdata['c2betorder[0][marketname]'] = allurldatalist[6]
        #             orderdata['c2betorder[0][Rate]'] = allurldatalist[7]
        #             orderdata['c2betorder[0][Bet]'] = allurldatalist[8]
        #             orderdata['c2betorder[0][BetType]'] = 'L'
        #             orderdata['c2betorder[0][MarketId]'] = allurldatalist[5]
        #             orderdata['c2betorder[0][SelectionId]'] = allurldatalist[12]
        #             orderdata['c2betorder[0][betfairori]'] = allurldatalist[13]
        #             orderdata['c2betorder[0][percent]'] = allurldatalist[14]
        #             orderdata['c2betorder[0][chk]'] = 'order'
        #             orderdata['c2betorder[0][category]'] = allurldatalist[15]
        #             orderdata['c2betorder[0][selectrateL1]'] = allurldatalist[9]
        #             orderdata['c2betorder[0][sel]'] = ''
        #             orderdata['c2betorder[0][gc12]'] = allurldatalist[11]
        #             orderdata['c2betorder[0][pawben]'] = allurldatalist[16]
        #             orderdata['c2betorder[0][selectmoneyL1]'] = allurldatalist[17]
        #             # 请求订单接口
        #             get_order = tg.post('https://m3.tg6666.net/order.php', data=orderdata)
        #             ordersoup = BeautifulSoup(get_order.text, 'html.parser')
        #             createdata = {}  # 定义订单请求数组
        #             createdata['c2betorder[0][handicap]'] = ordersoup.select('#handicap')[0].attrs['value']
        #             createdata['c2betorder[0][inplay]'] = ordersoup.select('#inplay')[0].attrs['value']
        #             createdata['c2betorder[0][selectname]'] = ordersoup.select('#selectname')[0].attrs['value']
        #             createdata['c2betorder[0][time]'] = ordersoup.select('#time')[0].attrs['value']
        #             createdata['c2betorder[0][gameid]'] = ordersoup.select('#gameid')[0].attrs['value']
        #             createdata['c2betorder[0][markettype]'] = ordersoup.select('#markettype')[0].attrs['value']
        #             createdata['c2betorder[0][gamename]'] = ordersoup.select('#gamename')[0].attrs['value']
        #             createdata['c2betorder[0][marketname]'] = ordersoup.select('#marketname_st')[0].attrs[
        #                 'value']
        #             createdata['c2betorder[0][Rate]'] = ordersoup.select('#Rate')[0].attrs['value']
        #             createdata['c2betorder[0][Bet]'] = '{}'.format(balance)
        #             createdata['c2betorder[0][BetType]'] = ordersoup.select('#BetType')[0].attrs['value']
        #             createdata['c2betorder[0][MarketId]'] = ordersoup.select('#MarketId')[0].attrs['value']
        #             createdata['c2betorder[0][SelectionId]'] = ordersoup.select('#SelectionId')[0].attrs[
        #                 'value']
        #             createdata['c2betorder[0][betfairori]'] = ordersoup.select('#betfairori')[0].attrs['value']
        #             createdata['c2betorder[0][percent]'] = ordersoup.select('#percent')[0].attrs['value']
        #             createdata['c2betorder[0][chk]'] = 'order'
        #             createdata['c2betorder[0][selectrateL1]'] = ordersoup.select('#selectrateL1')[0].attrs[
        #                 'value']
        #             createdata['c2betorder[0][category]'] = ordersoup.select('#category')[0].attrs['value']
        #             createdata['c2betorder[0][sel]'] = ordersoup.select('#sel')[0].attrs['value']
        #             createdata['c2betorder[0][gc12]'] = ordersoup.select('#gc12')[0].attrs['value']
        #
        #             # 　佛祖保佑
        #             #                             _ooOoo_
        #             #                            o8888888o
        #             #                            88" . "88
        #             #                            (| -_- |)
        #             #                            O\  =  /O
        #             #                         ____/`---'\____
        #             #                       .'  \\|     |//  `.
        #             #                      /  \\|||  :  |||//  \
        #             #                     /  _||||| -:- |||||-  \
        #             #                     |   | \\\  -  /// |   |
        #             #                     | \_|  ''\---/''  |   |
        #             #                     \  .-\__  `-`  ___/-. /
        #             #                   ___`. .'  /--.--\  `. . __
        #             #                ."" '<  `.___\_<|>_/___.'  >'"".
        #             #               | | :  `- \`.;`\ _ /`;.`/ - ` : | |
        #             #               \  \ `-.   \_ __\ /__ _/   .-` /  /
        #             #          ======`-.____`-.___\_____/___.-`____.-'======
        #             #                             `=---='
        #             #         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #             #                       　　　拈花一指定乾坤
        #             createorder = tg.post('https://m3.tg6666.net/order_finish.php', data=createdata)
        #             if '下注成功' in createorder.text:
        #                 print('购买成功! 5分钟后继续... {}'.format(datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))
        #                 time.sleep(300)
        #                 # ordertimes -= 1
        #                 break
        #             else:
        #                 print('购买失败！问题： {}'.format(createorder.text))
        # else:
        #     print('当前无可购买比赛,等待5秒..{}'.format(datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))
        #     time.sleep(5)
    db.close()
    # 完成一次记录等待
    print('等待10分钟后继续执行...-nowtime:{}'.format(datetime.datetime.now().strftime(
        '%y-%m-%d %H:%M:%S')))
    time.sleep(600)
    # except:
    #     print('故障等待5分钟后继续执行...-nowtime:{}'.format(datetime.datetime.now().strftime(
    #         '%y-%m-%d %H:%M:%S')))
    #     time.sleep(300)
    #     # 登录系统
    #     login_page = tg.get('https://m3.tg6666.net/login.php', verify=False)
    #     login = tg.post('https://m3.tg6666.net/other/login.php', data={'account': account, 'pwd': pwd},
    #                     verify=False)
    #     continue
