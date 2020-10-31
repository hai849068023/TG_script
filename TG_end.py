import requests
import re
import time
import urllib3
import datetime
import random
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
    try:
        # 获取下单列表记录
        orderrecord = tg.get('https://m1.tg6000.net/orderinfo.php', verify=False)
        orderrecordsoup = BeautifulSoup(orderrecord.text, 'html.parser')

        # 获取余额
        balance = float(orderrecordsoup.select('.money')[0].text)

        # 交易金额
        if orderrecordsoup.select('.trade_amount_num')[0].text != '':
            trading = float(orderrecordsoup.select('.trade_amount_num')[0].text)
        else:
            trading = 0

        # 获取是否存在下单项
        is_order = orderrecordsoup.select('.game_list.v1')

        # 如果没有余额并且没有订单记录则退出程序，如果有订单记录继续s
        if balance + trading >= 200:
            # 发送邮件
            try:
                # 邮件发送代码
                ############################################################################
                receivers = ['18758277138@163.com']
                msg = MIMEText('当前账户余额{},可发起提现！/n 发送时间:{}'.format(balance + trading, datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))  # 邮件内容
                msg['Subject'] = '提现提醒'  # 邮件主题
                msg['From'] = '18655109810@163.com'  # 发送者账号
                msg['To'] = '18758277138@163.com'  # 接收者账号列表
                smtObj = smtplib.SMTP('smtp.163.com')
                smtObj.login('18655109810@163.com', 'hai214810')
                smtObj.sendmail('18655109810@163.com', receivers, msg.as_string())
                print('邮件发送成功')
            ###########################################################################
            except smtplib.SMTPException:
                print('邮件发送失败')

        if len(is_order) > 0 and balance < 100:
            print('待结算，等待10分钟...{}'.format(datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))
            time.sleep(600)
            continue
        # 结束执行
        if balance < 100 and len(is_order) == 0:
            print('gameover,等待拯救！{}'.format(datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))
            time.sleep(600)
            continue

        # 活动市场列表
        market = tg.get('https://m1.tg6000.net/market.php', verify=False)
        marketsoup = BeautifulSoup(market.text, 'html.parser')
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

        # 天命选择
        choicegame = random.choice(marketlist[:5])

        # 获取比赛请求链接
        parameter = []
        for para in re.findall("\((.*)\)", choicegame.attrs['onclick'])[0].split(','):
            parameter.append(para[1:-1])
        gamedetail = tg.get(
            'https://m1.tg6000.net/marketorder.php?gc12={}&gameid={}&time={}&name={}&competitionname={}&status_id={}'.format(
                parameter[0], parameter[1], parameter[2], parameter[3], parameter[4], parameter[5]))
        gamedetailsoup = BeautifulSoup(gamedetail.text, 'html.parser')

        # 获取购买数据并下单操作
        allodds = gamedetailsoup.select('.content-1 .content_row')
        nextgetdata = allodds[15].attrs['onclick']
        allurldata = nextgetdata.split(',')
        allurldatalist = []  # order接口参数列表
        for d in allurldata:
            allurlvalue = re.search("'(.*)'", d).group(1)
            allurldatalist.append(allurlvalue)
        # 定义一个参数字典
        orderdata = {}
        orderdata['c2betorder[0][selectname]'] = allurldatalist[0]
        orderdata['c2betorder[0][time]'] = allurldatalist[1]
        orderdata['c2betorder[0][gameid]'] = allurldatalist[2]
        orderdata['c2betorder[0][markettype]'] = allurldatalist[3]
        orderdata['c2betorder[0][gamename]'] = allurldatalist[4]
        orderdata['c2betorder[0][marketname]'] = allurldatalist[6]
        orderdata['c2betorder[0][Rate]'] = allurldatalist[7]
        orderdata['c2betorder[0][Bet]'] = allurldatalist[8]
        orderdata['c2betorder[0][BetType]'] = 'L'
        orderdata['c2betorder[0][MarketId]'] = allurldatalist[5]
        orderdata['c2betorder[0][SelectionId]'] = allurldatalist[12]
        orderdata['c2betorder[0][betfairori]'] = allurldatalist[13]
        orderdata['c2betorder[0][percent]'] = allurldatalist[14]
        orderdata['c2betorder[0][chk]'] = 'order'
        orderdata['c2betorder[0][category]'] = allurldatalist[15]
        orderdata['c2betorder[0][selectrateL1]'] = allurldatalist[9]
        orderdata['c2betorder[0][sel]'] = ''
        orderdata['c2betorder[0][gc12]'] = allurldatalist[11]
        orderdata['c2betorder[0][pawben]'] = allurldatalist[16]
        orderdata['c2betorder[0][selectmoneyL1]'] = allurldatalist[17]
        # 请求订单接口
        get_order = tg.post('https://m1.tg6000.net/order.php', data=orderdata)
        ordersoup = BeautifulSoup(get_order.text, 'html.parser')
        createdata = {}  # 定义订单请求数组
        createdata['c2betorder[0][handicap]'] = ordersoup.select('#handicap')[0].attrs['value']
        createdata['c2betorder[0][inplay]'] = ordersoup.select('#inplay')[0].attrs['value']
        createdata['c2betorder[0][selectname]'] = ordersoup.select('#selectname')[0].attrs['value']
        createdata['c2betorder[0][time]'] = ordersoup.select('#time')[0].attrs['value']
        createdata['c2betorder[0][gameid]'] = ordersoup.select('#gameid')[0].attrs['value']
        createdata['c2betorder[0][markettype]'] = ordersoup.select('#markettype')[0].attrs['value']
        createdata['c2betorder[0][gamename]'] = ordersoup.select('#gamename')[0].attrs['value']
        createdata['c2betorder[0][marketname]'] = ordersoup.select('#marketname_st')[0].attrs[
            'value']
        createdata['c2betorder[0][Rate]'] = ordersoup.select('#Rate')[0].attrs['value']
        if balance >= 200:
            createdata['c2betorder[0][Bet]'] = '{}'.format(100)
        else:
            createdata['c2betorder[0][Bet]'] = '{}'.format(balance)
        createdata['c2betorder[0][BetType]'] = ordersoup.select('#BetType')[0].attrs['value']
        createdata['c2betorder[0][MarketId]'] = ordersoup.select('#MarketId')[0].attrs['value']
        createdata['c2betorder[0][SelectionId]'] = ordersoup.select('#SelectionId')[0].attrs[
            'value']
        createdata['c2betorder[0][betfairori]'] = ordersoup.select('#betfairori')[0].attrs['value']
        createdata['c2betorder[0][percent]'] = ordersoup.select('#percent')[0].attrs['value']
        createdata['c2betorder[0][chk]'] = 'order'
        createdata['c2betorder[0][selectrateL1]'] = ordersoup.select('#selectrateL1')[0].attrs[
            'value']
        createdata['c2betorder[0][category]'] = ordersoup.select('#category')[0].attrs['value']
        createdata['c2betorder[0][sel]'] = ordersoup.select('#sel')[0].attrs['value']
        createdata['c2betorder[0][gc12]'] = ordersoup.select('#gc12')[0].attrs['value']

        # 　佛祖保佑
        #                             _ooOoo_
        #                            o8888888o
        #                            88" . "88
        #                            (| -_- |)
        #                            O\  =  /O
        #                         ____/`---'\____
        #                       .'  \\|     |//  `.
        #                      /  \\|||  :  |||//  \
        #                     /  _||||| -:- |||||-  \
        #                     |   | \\\  -  /// |   |
        #                     | \_|  ''\---/''  |   |
        #                     \  .-\__  `-`  ___/-. /
        #                   ___`. .'  /--.--\  `. . __
        #                ."" '<  `.___\_<|>_/___.'  >'"".
        #               | | :  `- \`.;`\ _ /`;.`/ - ` : | |
        #               \  \ `-.   \_ __\ /__ _/   .-` /  /
        #          ======`-.____`-.___\_____/___.-`____.-'======
        #                             `=---='
        #         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #                       　　　拈花一指定乾坤
        createorder = tg.post('https://m1.tg6000.net/order_finish.php', data=createdata)
        if '下注成功' in createorder.text:
            print('购买成功! 10分钟后继续... {}'.format(datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))
            time.sleep(600)
        else:
            print('购买失败！问题： {}'.format(createorder.text))

    except:
        # 等待五分钟后重新登录
        print('异常5分钟后重新登录 {}'.format(datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))
        time.sleep(300)
        # 登录系统
        login_page = tg.get('https://m1.tg6000.net/login.php', verify=False)
        login = tg.post('https://m1.tg6000.net/other/login.php', data={'account': account, 'pwd': pwd},
                        verify=False)
