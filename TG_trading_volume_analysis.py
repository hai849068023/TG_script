import pymysql
import re

# 创建数据库链接
db = pymysql.connect('localhost', 'root', 'root', 'TGanalysis')
cursor = db.cursor()

# 获取比分数据并生成可读行展示效果
sql = "select gamename,trading_volume,halfscore_odds,resultscore from tradingdata"
cursor.execute(sql)
datacontent = cursor.fetchall()
times = 0
for gamecontent in datacontent:
    if gamecontent[3] == '2-1':
        # if int(gamecontent[3][0]) == 2 and int(gamecontent[3][-1]) == 2:
        # 根据购买量
        trading_volume = gamecontent[1].split(',')[:-1]
        trading_volumed = sorted(trading_volume, key=lambda x:int(re.findall('.*:(.*)', x)[0]), reverse=True)
        print(trading_volumed)
