import time
import json
import random
import smtplib
import requests
import re
from email.mime.text import MIMEText
from email.utils import formataddr
import sys

# t00ls 账号配置

username=sys.argv[1]
password=sys.argv[2]
question_num = 1  # 安全提问 参考下面
question_answer = sys.argv[3]  # 安全提问答案


# 0 = 没有安全提问
# 1 = 母亲的名字
# 2 = 爷爷的名字
# 3 = 父亲出生的城市
# 4 = 您其中一位老师的名字
# 5 = 您个人计算机的型号
# 6 = 您最喜欢的餐馆名称
# 7 = 驾驶执照的最后四位数字

# 选择提醒方式
notice = 0  #  0 = 钉钉机器人 1 = 邮件  2 = 钉钉机器人 + 邮件

dingtalk_token=sys.argv[4]

req_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded'
}

def t00ls_login(u_name, u_pass, q_num, q_ans):
    """
    t00ls 登录函数
    :param u_name: 用户名
    :param u_pass: 密码的 md5 值 32 位小写
    :param q_num: 安全提问类型
    :param q_ans: 安全提问答案
    :return: 签到要用的 hash 和 登录后的 Cookies
    """

    login_data = {
        'action': 'login',
        'username': u_name,
        'password': u_pass,
        'questionid': q_num,
        'answer': q_ans
    }
    response_login = requests.post('https://www.t00ls.net/login.json', data=login_data, headers=req_headers)
    response_login_json = json.loads(response_login.text)

    if response_login_json['status'] != 'success':
        return None
    else:
        print('用户:', username, '登入成功!')
        formhash = response_login_json['formhash']
        t00ls_cookies = response_login.cookies
        return formhash, t00ls_cookies

def dingtalk_send(token,text):
   
    headers = {'Content-Type': 'application/json;charset=utf-8'}  # 请求头
    api_url = f"https://oapi.dingtalk.com/robot/send?access_token={token}"
    json_text = {
        "msgtype": "text",  # 信息格式
        "text": {
            "content": text
        },
    }
    requests.post(api_url, json.dumps(json_text), headers=headers).content
def t00ls_sign(t00ls_hash, t00ls_cookies):
    """
    t00ls 签到函数
    :param t00ls_hash: 签到要用的 hash
    :param t00ls_cookies: 登录后的 Cookies
    :return: 签到后的 JSON 数据
    """
    sign_data = {
        'formhash': t00ls_hash,
        'signsubmit': "true"
    }
    response_sign = requests.post('https://www.t00ls.net/ajax-sign.json', data=sign_data, cookies=t00ls_cookies,headers=req_headers)
    return json.loads(response_sign.text)
def getdomain():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r=requests.get('https://www.beianx.cn',headers)
    a=re.compile('<a href="/bacx/(.*?).com">')
    b=a.findall(r.text)
    return b[random.sample(range(29, len(b)), 1)[0]]+".com"
def t00ls_domain(t00ls_hash, t00ls_cookies):
    """
    t00ls 域名查询函数
    :param t00ls_hash: 签到要用的 hash
    :param t00ls_cookies: 登录后的 Cookies
    :return: 查询相关的日志信息
    """
    content = ''
    # 查询今天注册的域名
    start_time = time.time()

    response_domains=getdomain()
    end_time = time.time()
    print(f'随机找域名耗时: {end_time - start_time:.4f}秒')
    content += f'\n随机找域名耗时: {end_time - start_time:.4f}秒\n\n'

    start_time = time.time()

    query_url = 'https://www.t00ls.net/domain.html'
    query_status = False
    query_count = 0  # 查询重试次数

    # 如果 t00ls 查询没有成功的话 就一直查询
    while not query_status and query_count < 2:

        domain=getdomain()  # 随机抽取一个 幸运儿
        query_data = {
        'domain': domain,
        'formhash': t00ls_hash,
        'querydomainsubmit':'查询'
    }
        try:
            response_query = requests.post(url=query_url, data=query_data, cookies=t00ls_cookies, headers=req_headers)
        except Exception:
            pass
        if domain in response_query.text:
            response_tb = requests.get('https://www.t00ls.net/members-tubilog.json', cookies=t00ls_cookies)
            if domain in response_tb.text:
                print('查询域名成功 TuBi + 1 \n')
                content += '查询域名成功 TuBi + 1\n'
                query_status = True
            else:
                print(f'糟糕 域名查询成功 但是 TuBi 没有增加 可能域名重复了,失败的域名是: {domain}')
                content += f'糟糕 域名查询成功 但是 TuBi 没有增加 可能域名重复了,失败的域名是: {domain}\n'
                query_count += 1
                print(f'随机延时 5-10 秒，继续第 {query_count} 次查询')
                content += f'随机延时 5-10 秒，继续第 {query_count} 次查询\n\n'
                time.sleep(random.randint(5, 10))
        else:
            print(f'查询失败？失败的域名是: {domain}')
            content += f'查询失败？失败的域名是: {domain}\n'
            query_count += 1
            print(f'随机延时 5-10 秒，继续第 {query_count} 次查询')
            content += f'随机延时 5-10 秒，继续第 {query_count} 次查询\n\n'
            time.sleep(random.randint(5, 10))
        if query_count == 5:
            print('重试查询次数已达上限 终止查询')
            content += '重试查询次数已达上限 终止查询\n\n'

    end_time = time.time()
    print(f't00ls 域名查询耗时: {end_time - start_time:.4f}秒')
    content += f't00ls 域名查询耗时: {end_time - start_time:.4f}秒\n'
    return content

def main():
    content = ''
    response_login = t00ls_login(username, password, question_num, question_answer)
    if response_login:
        response_sign = t00ls_sign(response_login[0], response_login[1])
        if response_sign['status'] == 'success':
            print('签到成功 TuBi + 1')
            content += '\n签到成功 TuBi + 1\n'

            verbose_log = t00ls_domain(response_login[0], response_login[1])
            content += verbose_log

            if notice == 0:
                try:
                   dingtalk_send(dingtalk_token,content)
                except Exception:
                    print('请检查钉钉机器人配置是否正确1')                        
        elif response_sign['message'] == 'alreadysign':
            print('已经签到过啦')
            content += '\n已经签到过啦\n'

            verbose_log = t00ls_domain(response_login[0], response_login[1])
            content += verbose_log

            if notice == 0:
                try:
                    dingtalk_send(dingtalk_token,content)
                except Exception:
                    print('请检查钉钉机器人配置是否正确2')                       
        else:
            print('出现玄学问题了 签到失败')
    else:
        print('登入失败 请检查输入资料是否正确')


if __name__ == '__main__':
    main()
