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
    # 获取所有比赛记录并分析记录
    market = tg.get('https://m3.tg6666.net/market.php', verify=False)
    marketsoup = BeautifulSoup(market.text, 'html.parser')
    marketlist = marketsoup.select('.content-1 li')

    balance = float(marketsoup.select('.money')[0].text)
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
        try:
            baoben = market.select('.guaranteedNomo')[0].text
        except:
            pass
        else:
            if baoben == '保本':
                # 获取比赛请求链接
                parameter = []
                for para in re.findall("\((.*)\)", market.attrs['onclick'])[0].split(','):
                    parameter.append(para[1:-1])
                gamedetail = tg.get(
                    'https://m3.tg6666.net/marketorder.php?gc12={}&gameid={}&time={}&name={}&competitionname={}&status_id={}'.format(
                        parameter[0], parameter[1], parameter[2], parameter[3], parameter[4], parameter[5]))
                gamedetailsoup = BeautifulSoup(gamedetail.text, 'html.parser')

                # 获得保本比赛赔率
                allgameodds = gamedetailsoup.select('.content-1 .content_row')
                for gameodd in allgameodds:
                    is_baoben = gameodd.select('.guaranteed_detailNomo')[0].attrs['style']
                    buy_score = gameodd.select('.content_cell.table_option')[0].text.strip()
                    if is_baoben == 'display: block':
                        has_odd = gameodd.select('.content_cell.cell_red.table_rate')[0].text.strip()
                        if has_odd != '':
                            print('可购买保本,赔率{}'.format(has_odd))
                            # 获取购买数据并下单操作
                            nextgetdata = gameodd.attrs['onclick']
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
                            createdata = {}  # 定义订单请求数组
                            createdata['c2betorder[0][handicap]'] = ordersoup.select('#handicap')[0].attrs[
                                'value']
                            createdata['c2betorder[0][inplay]'] = ordersoup.select('#inplay')[0].attrs[
                                'value']
                            createdata['c2betorder[0][selectname]'] = \
                            ordersoup.select('#selectname')[0].attrs['value']
                            createdata['c2betorder[0][time]'] = ordersoup.select('#time')[0].attrs['value']
                            createdata['c2betorder[0][gameid]'] = ordersoup.select('#gameid')[0].attrs[
                                'value']
                            createdata['c2betorder[0][markettype]'] = \
                            ordersoup.select('#markettype')[0].attrs['value']
                            createdata['c2betorder[0][gamename]'] = ordersoup.select('#gamename')[0].attrs[
                                'value']
                            createdata['c2betorder[0][marketname]'] = \
                            ordersoup.select('#marketname_st')[0].attrs[
                                'value']
                            createdata['c2betorder[0][Rate]'] = ordersoup.select('#Rate')[0].attrs['value']
                            createdata['c2betorder[0][Bet]'] = '{}'.format(balance)
                            createdata['c2betorder[0][BetType]'] = ordersoup.select('#BetType')[0].attrs[
                                'value']
                            createdata['c2betorder[0][MarketId]'] = ordersoup.select('#MarketId')[0].attrs[
                                'value']
                            createdata['c2betorder[0][SelectionId]'] = \
                            ordersoup.select('#SelectionId')[0].attrs[
                                'value']
                            createdata['c2betorder[0][betfairori]'] = \
                            ordersoup.select('#betfairori')[0].attrs['value']
                            createdata['c2betorder[0][percent]'] = ordersoup.select('#percent')[0].attrs[
                                'value']
                            createdata['c2betorder[0][chk]'] = 'order'
                            createdata['c2betorder[0][selectrateL1]'] = \
                            ordersoup.select('#selectrateL1')[0].attrs[
                                'value']
                            createdata['c2betorder[0][category]'] = ordersoup.select('#category')[0].attrs[
                                'value']
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
                                print('购买成功! 90分钟后继续... {}'.format(
                                    datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))
                                time.sleep(5400)
                                # ordertimes -= 1
                                break
                            else:
                                print('购买失败！问题： {}'.format(createorder.text))
                        else:
                            break

    print('本次未找到可购买比赛，10秒后继续...')
    time.sleep(10)
