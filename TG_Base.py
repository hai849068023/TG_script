#　这是一个基类文件

class TG_base:

    def Login(self, tg):
        # 登录系统
        login_page = tg.get('https://m3.tg6666.net/login.php', verify=False)
        login = tg.post('https://m3.tg6666.net/other/login.php', data={'account': 'GFE778', 'pwd': 'hai214810'},
                        verify=False)