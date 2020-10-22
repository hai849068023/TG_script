import requests
import re
import time
import urllib3
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
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
    # try:
    #     # 获取下单列表记录
    #     orderrecord = tg.get('https://m3.tg6666.net/orderinfo.php', verify=False)
    #     orderrecordsoup = BeautifulSoup(orderrecord.text, 'html.parser')
    #
    #     # 异常结束
    #     assert '请输入帐号' in orderrecord.text
    #
    #     # 获取余额
    #     balance = float(orderrecordsoup.select('.money')[0].text)
    #
    #     # 交易金额
    #     if orderrecordsoup.select('.trade_amount_num')[0].text != '':
    #         trading = float(orderrecordsoup.select('.trade_amount_num')[0].text)
    #     else:
    #         trading = 0
    #     # 获取是否存在下单项
    #     is_order = orderrecordsoup.select('.game_list.v1')
    #     # 获得下单列表
    #     order_list = []
    #     for order in is_order:
    #         guest_name = re.findall('.*vs(.*)', order.text.strip())[0].strip()
    #         order_list.append(guest_name)
    #
    #     # 如果没有余额并且没有订单记录则退出程序，如果有订单记录继续s
    #     if balance + trading >= 200:
    #         # 发送邮件
    #         try:
    #             # 邮件发送代码
    #             ############################################################################
    #             receivers = ['18758277138@163.com']
    #             msg = MIMEText('余额满200,可发起提现. 等待一小时后继续执行！/n 发送时间:{}'.format(datetime.now().strftime('%y-%m-%d %H:%M:%S')))  # 邮件内容
    #             msg['Subject'] = '提现提醒'  # 邮件主题
    #             msg['From'] = '18655109810@163.com'  # 发送者账号
    #             msg['To'] = '18758277138@163.com'  # 接收者账号列表
    #             smtObj = smtplib.SMTP('smtp.163.com')
    #             smtObj.login('18655109810@163.com', 'hai214810')
    #             smtObj.sendmail('18655109810@163.com', receivers, msg.as_string())
    #             print('邮件发送成功')
    #         ###########################################################################
    #         except smtplib.SMTPException:
    #             print('邮件发送失败')
    #         time.sleep(3600)
    #         continue
    #     if len(is_order) > 0 and balance < 100:
    #         print('待结算，等待10分钟...{}'.format(datetime.now().strftime('%y-%m-%d %H:%M:%S')))
    #         time.sleep(600)
    #         continue
    #     # 结束执行
    #     if balance < 100 and len(is_order) == 0:
    #         print('gameover,等待拯救！{}'.format(datetime.now().strftime('%y-%m-%d %H:%M:%S')))
    #         time.sleep(600)
    #         continue


    '''
        主体业务逻辑,获取时长列表并根据规则下单
    '''
    # 获得市场列表数据
    market = tg.get('https://m3.tg6666.net/market.php', verify=False)
    marketsoup = BeautifulSoup(market.text, 'html.parser')
    marketlist = marketsoup.select('.content-2 li')
    # 如果列表没有抛出异常
    # assert len(marketlist) == 0

    # 循环市场列表前五项完成业务流程
    for market in marketlist[:5]:
        parameter = []
        for para in re.findall("\((.*)\)", market.attrs['onclick'])[0].split(','):
            parameter.append(para[1:-1])
        gamev = parameter[3]
        gamedetail = tg.get(
            'https://m3.tg6666.net/marketorder.php?gc12={}&gameid={}&time={}&name={}&competitionname={}&status_id={}'.format(
                parameter[0], parameter[1], parameter[2], parameter[3], parameter[4], parameter[5]))
        gamedetailsoup = BeautifulSoup(gamedetail.text, 'html.parser')
        # # 判断购买过程中是否任有余额，没有则终止循环
        # nowbalance = float(gamedetailsoup.select('.money')[0].text)
        # if nowbalance < 100:
        #     break

        # 获得半场交易量数据,并获取其他购买数量判断是否可下单
        tradingele = gamedetailsoup.select('.content-2 .chatShowIcon')[0]
        tradingdata = []
        for para in re.findall("\((.*)\)", tradingele.attrs['onclick'])[0].replace("'", '').split(','):
            tradingdata.append(para)
        # 如果半场比分没有则继续下一个
        if len(tradingdata) != 7:
            continue
        tdata = {
            'eventid': tradingdata[3],
            'marketid': tradingdata[4],
            'chartid': tradingdata[1],
            'competitionname': tradingdata[2],
            'gameName': tradingdata[0],
            'totaldealmoney': tradingdata[5] + ',' + tradingdata[6],
        }
        halftrading = tg.post('https://m3.tg6666.net/chatShow.php', data=tdata, verify=False)
        # 其他选项的平台购买数值
        sts = re.findall('.*var st = \[(.*)\].*', halftrading.text)[0].split(',')[9]
        if int(sts) > 3000:
            pass

    # except:
    #     # 等待五分钟后重新登录
    #     print('异常5分钟后重新登录 {}'.format(datetime.now().strftime('%y-%m-%d %H:%M:%S')))
    #     time.sleep(300)
    #     # 登录系统
    #     login_page = tg.get('https://m3.tg6666.net/login.php', verify=False)
    #     login = tg.post('https://m3.tg6666.net/other/login.php', data={'account': account, 'pwd': pwd},
    #                     verify=False)