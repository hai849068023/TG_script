import pymysql
import re

# 创建数据库链接
db = pymysql.connect('localhost', 'tg', '123456', 'TGanalysis')
cursor = db.cursor()

# 获取比分数据并生成可读行展示效果
sql = "select gamename,gameodds,gamehalfodds,gameresult,gamehalfresult,morepower from gamedata"
cursor.execute(sql)
datacontent = cursor.fetchall()
is_allsmile = True
is_halfsmile = True
for data in datacontent:
    if data[3] and data[4] and data[5]:
        game_odds = data[1]
        game_halfodds = data[2]

        # 定义变量
        goumai_all = ''
        goumai_half = ''
        # 容错处理
        # if len(game_odds) > 0:
        #     # 分解数据
        #     odds_list = game_odds.split(',')
        #     for i in range(len(odds_list)):
        #         for j in range(i+1, len(odds_list)):
        #             try:
        #                 cone = re.findall(':(.*)%', odds_list[i])[0]
        #                 ctwo = re.findall(':(.*)%', odds_list[j])[0]
        #             except:
        #                 pass
        #             else:
        #                 if float(cone) > float(ctwo):
        #                     odds_list[i], odds_list[j] = odds_list[j], odds_list[i]
        #     # 预设购买
        #     goumai_all = re.findall('(.*):.*', odds_list[1])[0]
        if len(game_halfodds) > 0:
            # 分解半场数据
            halfodds_list = game_halfodds.split(',')
            for i in range(len(halfodds_list)):
                for j in range(i + 1, len(halfodds_list)):
                    try:
                        cone = re.findall(':(.*)%', halfodds_list[i])[0]
                        ctwo = re.findall(':(.*)%', halfodds_list[j])[0]
                    except:
                        pass
                    else:
                        if float(cone) < float(ctwo):
                            halfodds_list[i], halfodds_list[j] = halfodds_list[j], halfodds_list[i]
            # 预设购买
            goumai_half = re.findall('(.*):.*', halfodds_list[0])[0]
        # new_odds_list = ''
        # hit_odd = ''
        # for odd in odds_list:
        #     if ' '.join(data[2]) in odd:
        #         hit_odd = re.findall('.*:(.*)%', odd)[0]
        #     new_odds_list += '\n{}'.format(odd)



        # allresult = ' '.join(data[3])
        halfresult = ' '.join(data[4])
        # if goumai_all == allresult:
        #     is_allsmile = False
        #     print('全场命中一次')
        if goumai_half == halfresult:
            is_halfsmile = False
            print('半场命中一次')
        elif goumai_half and halfresult:
            print('未命中')

# if is_allsmile:
#     print('全场完美避开:)')
# else:
#     print('全场不幸中招-_-')
if is_halfsmile:
    print('半场完美避开:)')
else:
    print('半场不幸中招-_-')