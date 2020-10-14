import requests
import re
import time
import urllib3
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from poplib import POP3


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
# ordertimes = 8
while True:
    # 通过邮件检测暂停下单并获取提现
    p = POP3('pop.163.com')
    p.user('18655109810@163.com')
    p.pass_('hai214810')
    all_message = p.list()
    for message in all_message[1]:
        num = message.decode()[0]
        detaillist = p.retr(num)[1]
        for email in detaillist:
            if '18758277138' in email.decode():
                print('需要提现,暂停运行一小时')
                p.dele(num)
                time.sleep(3600)
                break
        break

    try:
        # 获取下单列表记录
        orderrecord = tg.get('https://m3.tg6666.net/orderinfo.php', verify=False)
        orderrecordsoup = BeautifulSoup(orderrecord.text, 'html.parser')

        # 异常结束
        if '请输入帐号' in orderrecord.text:
            raise

        # 获取余额
        balance = float(orderrecordsoup.select('.money')[0].text)

        # 交易金额
        if orderrecordsoup.select('.trade_amount_num')[0].text != '':
            trading = float(orderrecordsoup.select('.trade_amount_num')[0].text)
        else:
            trading = 0
        # 获取是否存在下单项
        is_order = orderrecordsoup.select('.game_list.v1')
        # 获得下单列表
        order_list = []
        for order in is_order:
            guest_name = re.findall('.*vs(.*)', order.text.strip())[0].strip()
            order_list.append(guest_name)

        # 如果没有余额并且没有订单记录则退出程序，如果有订单记录继续s
        if balance + trading >= 200:
            # 发送邮件
            try:
                # 邮件发送代码
                ############################################################################
                receivers = ['18758277138@163.com']
                msg = MIMEText('余额满200,可发起提现. 等待一小时后继续执行！/n 发送时间:{}'.format(datetime.now().strftime('%y-%m-%d %H:%M:%S')))  # 邮件内容
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
            time.sleep(3600)
            continue
        if len(is_order) > 0 and balance < 100:
            print('待结算，等待10分钟...{}'.format(datetime.now().strftime('%y-%m-%d %H:%M:%S')))
            time.sleep(600)
            continue
        # 结束执行
        if balance < 100 and len(is_order) == 0:
            print('gameover,等待拯救！{}'.format(datetime.now().strftime('%y-%m-%d %H:%M:%S')))
            time.sleep(600)
            continue

        # 久赌必输
        # if ordertimes == 0:
        #     print('不能有赌徒心里，休息一下！{}'.format(datetime.now().strftime('%y-%m-%d %H:%M:%S')))
        #     # 发送邮件
        #     try:
        #         # 邮件发送代码
        #         ############################################################################
        #         receivers = ['18758277138@163.com']
        #         msg = MIMEText('完成8场，休息一下！')  # 邮件内容
        #         msg['Subject'] = '完成任务提醒'  # 邮件主题
        #         msg['From'] = '18655109810@163.com'  # 发送者账号
        #         msg['To'] = '18758277138@163.com'  # 接收者账号列表
        #         smtObj = smtplib.SMTP('smtp.163.com')
        #         smtObj.login('18655109810@163.com', 'hai214810')
        #         smtObj.sendmail('18655109810@163.com', receivers, msg.as_string())
        #         print('邮件发送成功')
        #     ###########################################################################
        #     except smtplib.SMTPException:
        #         print('邮件发送失败')
        #     time.sleep(28800)
        #     ordertimes = 8
        #     continue

        # 活动市场列表
        market = tg.get('https://m3.tg6666.net/market.php', verify=False)
        marketsoup = BeautifulSoup(market.text, 'html.parser')
        marketlist = marketsoup.select('.content-2 li')
        if len(marketlist) == 0:
            print('无法获取列表抛出异常')
            raise

        # 预定义胜出球队
        winner = ''
        # 所有比赛赔率数据字符串
        score_odds_txt = ''
        # 预购比赛
        gamev = ''
        # 定义购买比分
        goumai = ''
        # 定义有效的比赛购买值
        effective = False
        # 获取比赛请求链接
        for market in marketlist:
            game_name = re.findall('.*VS(.*)', market.text.strip().replace('\n', ''))[0]
            if game_name in order_list:
                continue
            parameter = []
            for para in re.findall("\((.*)\)", market.attrs['onclick'])[0].split(','):
                parameter.append(para[1:-1])
            gamev = parameter[3]
            gamedetail = tg.get(
                'https://m3.tg6666.net/marketorder.php?gc12={}&gameid={}&time={}&name={}&competitionname={}&status_id={}'.format(
                    parameter[0], parameter[1], parameter[2], parameter[3], parameter[4], parameter[5]))
            gamedetailsoup = BeautifulSoup(gamedetail.text, 'html.parser')
            # 判断购买过程中是否任有余额，没有则终止循环
            nowbalance = float(gamedetailsoup.select('.money')[0].text)
            if nowbalance < 100:
                break
            # 记录当前比赛所有赔率
            scorelist = gamedetailsoup.select('.content-1 .content_row .content_cell.table_option')
            if len(scorelist) == 0 or len(scorelist) < 16:
                time.sleep(5)
                continue
            oddslist = gamedetailsoup.select('.content-1 .content_row .content_cell.cell_red.table_rate')
            for i in range(len(scorelist)):
                score_odds_txt = score_odds_txt + scorelist[i].text.strip() + ':' + oddslist[i].text + ','

            # 近期比分数据
            pkrecord = tg.get(
                'https://m3.tg6666.net/pkRecords.php?gametime={}&gamename={}'.format(parameter[2], parameter[3]),
                verify=False)
            pkrecordsoup = BeautifulSoup(pkrecord.text, 'html.parser')

            # 获取近年的比赛记录并记录
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
                if allpower > 0 and halfpower >= 0:
                    winner = home_team
                else:
                    winner = away_team
            else:
                time.sleep(5)
                continue
            # 分解数据
            odds_list = score_odds_txt.split(',')
            for i in range(len(odds_list)):
                for j in range(i + 1, len(odds_list)):
                    try:
                        cone = re.findall(':(.*)%', odds_list[i])[0]
                        ctwo = re.findall(':(.*)%', odds_list[j])[0]
                    except:
                        pass
                    else:
                        if float(cone) > float(ctwo):
                            odds_list[i], odds_list[j] = odds_list[j], odds_list[i]

            # 下单比分
            goumai = re.findall('(.*):.*', odds_list[2])[0]
            if '进球' in goumai:
                continue

            # 判断预购买比分是否与是否与历史数据相反
            nowhome = re.findall('(.*)v.*',gamev)[0].strip()
            nowguest = re.findall('.*v(.*)',gamev)[0].strip()
            if int(goumai[0]) - int(goumai[-1]) > 0:
                orderwinner = nowhome
            else:
                orderwinner = nowguest

            # 如果预定义购买何分析数据购买相反则继续
            if orderwinner != winner:
                effective = True
            else:
                time.sleep(5)
                continue


            # 获取购买数据并下单操作
            if goumai != '' and effective:
                allodds = gamedetailsoup.select('.content-1 .content_row')
                for odd in allodds:
                    if goumai in odd.text:
                        nextgetdata = odd.attrs['onclick']
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
                        get_order = tg.post('https://m3.tg6666.net/order.php', data=orderdata)
                        ordersoup = BeautifulSoup(get_order.text, 'html.parser')
                        createdata = {} # 定义订单请求数组
                        createdata['c2betorder[0][handicap]'] = ordersoup.select('#handicap')[0].attrs['value']
                        createdata['c2betorder[0][inplay]'] = ordersoup.select('#inplay')[0].attrs['value']
                        createdata['c2betorder[0][selectname]'] = ordersoup.select('#selectname')[0].attrs['value']
                        createdata['c2betorder[0][time]'] = ordersoup.select('#time')[0].attrs['value']
                        createdata['c2betorder[0][gameid]'] = ordersoup.select('#gameid')[0].attrs['value']
                        createdata['c2betorder[0][markettype]'] = ordersoup.select('#markettype')[0].attrs['value']
                        createdata['c2betorder[0][gamename]'] = ordersoup.select('#gamename')[0].attrs['value']
                        createdata['c2betorder[0][marketname]'] = ordersoup.select('#marketname_st')[0].attrs['value']
                        createdata['c2betorder[0][Rate]'] = ordersoup.select('#Rate')[0].attrs['value']
                        createdata['c2betorder[0][Bet]'] = '{}'.format(balance)
                        createdata['c2betorder[0][BetType]'] = ordersoup.select('#BetType')[0].attrs['value']
                        createdata['c2betorder[0][MarketId]'] = ordersoup.select('#MarketId')[0].attrs['value']
                        createdata['c2betorder[0][SelectionId]'] = ordersoup.select('#SelectionId')[0].attrs['value']
                        createdata['c2betorder[0][betfairori]'] = ordersoup.select('#betfairori')[0].attrs['value']
                        createdata['c2betorder[0][percent]'] = ordersoup.select('#percent')[0].attrs['value']
                        createdata['c2betorder[0][chk]'] = 'order'
                        createdata['c2betorder[0][selectrateL1]'] = ordersoup.select('#selectrateL1')[0].attrs['value']
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
                        createorder = tg.post('https://m3.tg6666.net/order_finish.php', data=createdata)
                        if '下注成功' in createorder.text:
                            print('购买成功! 5分钟后继续... {}'.format(datetime.now().strftime('%y-%m-%d %H:%M:%S')))
                            time.sleep(300)
                            # ordertimes -= 1
                            break
                        else:
                            print('购买失败！问题： {}'.format(createorder.text))
            else:
                print('当前无可购买比赛,等待5秒..{}'.format(datetime.now().strftime('%y-%m-%d %H:%M:%S')))
                time.sleep(5)
    except:
        # 等待五分钟后重新登录
        print('异常5分钟后重新登录 {}'.format(datetime.now().strftime('%y-%m-%d %H:%M:%S')))
        time.sleep(300)
        # 登录系统
        login_page = tg.get('https://m3.tg6666.net/login.php', verify=False)
        login = tg.post('https://m3.tg6666.net/other/login.php', data={'account': account, 'pwd': pwd},
                        verify=False)
