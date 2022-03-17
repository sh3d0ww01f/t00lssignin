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
    response_sign = requests.post('https://www.t00ls.com/ajax-sign.json', data=sign_data, cookies=t00ls_cookies,headers=req_headers)
    return json.loads(response_sign.text)
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
    response_login = requests.post('https://www.t00ls.com/login.json', data=login_data, headers=req_headers)
    response_login_json = json.loads(response_login.text)

    if response_login_json['status'] != 'success':
        return None
    else:
        print('用户:', username, '登入成功!')
        formhash = response_login_json['formhash']
        t00ls_cookies = response_login.cookies
        return formhash, t00ls_cookies
def t00ls_check_qd(t00ls_hash, t00ls_cookies):
        status=""
        try:
            response_query = requests.post(url="https://www.t00ls.com/members-profile.json", data=query_data, cookies=t00ls_cookies, headers=req_headers)
            raw=json.loads(response_query)
            status=raw["extcredits2"]
        except:
            pass
        return status    
        
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
def main():
    content = ''
    response_login = t00ls_login(username, password, question_num, question_answer)
    if response_login:
        response_sign = t00ls_sign(response_login[0], response_login[1])
        if response_sign['status'] == 'success':
            print('签到成功 TuBi + 1')
            content += '\n签到成功 \n'
            tubi_count=t00ls_check_qd()
            if(tubi_count != ''):
                content += f'\ntubi:{tubi_coin} \n'

            if notice == 0:
                try:
                   dingtalk_send(dingtalk_token,content)
                except Exception:
                    print('请检查钉钉机器人配置是否正确1')                        
        elif response_sign['message'] == 'alreadysign':
            print('已经签到过啦')
            content += '\n已经签到过啦\n'
            tubi_count=t00ls_check_qd()
            if(tubi_count != ''):
                content += f'\ntubi:{tubi_coin} \n'

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
