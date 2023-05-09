import json
import os
import time

import requests

#import dingPush

import base64
import hashlib
import hmac

import urllib.parse



class dingpush():

    def __init__(self, title, content, reminders, DD_BOT_TOKEN, DD_BOT_SECRET):
        self.DD_BOT_TOKEN = DD_BOT_TOKEN
        self.DD_BOT_SECRET = DD_BOT_SECRET  #哈希算法验证(可选)

        self.title = title
        self.content = content
        self.reminders = reminders

    def EncryptionPush(self):
        timestamp = str(round(time.time() * 1000))  # 时间戳
        secret_enc = self.DD_BOT_SECRET.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.DD_BOT_SECRET)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc,
                             string_to_sign_enc,
                             digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))  # 签名
        print('开始使用 钉钉机器人 推送消息...')

        url = f'https://oapi.dingtalk.com/robot/send?access_token={self.DD_BOT_TOKEN}&timestamp={timestamp}&sign={sign}'
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        data = {
            'msgtype': 'text',
            'text': {
                'content': f'{self.title}\n\n{self.content}'
            }
        }
        try:
            r = requests.post(url=url,
                              data=json.dumps(data),
                              headers=headers,
                              timeout=15).json()
            if not r['errcode']:
                print('INFO: 钉钉推送成功')
            else:
                print("INFO: 钉钉推送失败", "错误详情：" + r["errmsg"])
        except Exception as e:
            print(f'ERROR: {e}')
            print(' WARNNING: 缺少配置: DD_BOT_TOKEN/DD_BOT_SECRET?')

    def NormalPush(self):
        url = f'https://oapi.dingtalk.com/robot/send?access_token={self.DD_BOT_TOKEN}'
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        data = {
            "msgtype": "text",
            "text": {
                "content": f'{self.title}\n\n{self.content}'
            },
            "at": {
                "atMobiles": [self.reminders],
                "isAtAll": False
            }
        }
        try:
            r = requests.post(url, data=json.dumps(data),
                              headers=headers).json()
            if not r['errcode']:
                print("INFO: 钉钉推送成功")

            else:
                print("INFO: 钉钉推送失败", "错误详情：" + r["errmsg"])
        except Exception as e:
            print("好像发生了什么奇怪的问题", f"ERROR: {e}")

    def SelectAndPush(self):
        if self.DD_BOT_SECRET:
            self.EncryptionPush()
        else:
            self.NormalPush()


def getAccessToken(session, openid):
    time_stamp = str(int(time.time()))  #获取时间戳
    url = "https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/login/we-chat/callback?callback=https%3A%2F%2Fqczj.h5yunban.com%2Fqczj-youth-learning%2Findex.php&scope=snsapi_userinfo&appid=wx56b888a1409a2920&openid=" + openid + "&nickname=ZhangSan&headimg=&time=" + time_stamp + "&source=common&sign=&t=" + time_stamp
    res = session.get(url)
    access_token = res.text[45:81]
    print("INFO: 获取到AccessToken:", access_token)
    return access_token


def getCurrentCourse(session, access_token):
    url = "https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/common-api/course/current?accessToken=" + access_token
    res = session.get(url)
    res_json = json.loads(res.text)
    if (res_json["status"] == 200):
        print("INFO: 获取到最新课程代号:", res_json["result"]["id"])
        return res_json["result"]["id"]
    else:
        raise Exception("INFO: 获取最新课程失败！")


def getJoin(session, access_token, current_course, nid, cardNo):
    data = {
        "course": current_course,  # 大学习期次的代码，如C0046，本脚本已经帮你获取啦
        "subOrg": None,
        "nid": nid,  # 团组织编号，形如N003************
        "cardNo": cardNo  # 打卡昵称
    }
    url = "https://qczj.h5yunban.com/qczj-youth-learning/cgi-bin/user-api/course/join?accessToken=" + access_token
    res = session.post(url, json=data)
    print("INFO: 签到结果:", res.text)
    res_json = json.loads(res.text)
    if (res_json["status"] == 200):
        print("INFO: 签到成功")
        return res.text, True
    else:
        raise Exception("INFO: 签到失败！")


if __name__ == '__main__':
    #作为个人版本使用
    # nid = os.getenv("nid")
    # cardNo = os.getenv("cardNo")
    # openid = os.getenv("openid")
    # DD_BOT_TOKEN = os.getenv("DD_BOT_TOKEN")
    # DD_BOT_SECRET = os.getenv("DD_BOT_SECRET")
    DD_BOT_TOKEN = "c10cac6ad1f4e646508cc9c44b8f89b4f14e9306b9c0135080c0dfb9f805524b"
    DD_BOT_SECRET = "SECcc4b1525e6a2f232b312ea7cf65639c7bf4ea17486a5c5f3f3245550aae6c445"

    #集体打卡使用的学号集合
    classes = ["3210105148",#TQY
               "3210101195",#GKH
               "3210105041",
               "3210105026",
               "3210300376",
               "3210103028",
               "3210101750",
               "3210102914",
               "3210104076",
               "3210102491",
               "3210104577",
               "3210102480",
               "3210103069",
               "3210100074",
               "3210102083",
               "3210101664",
               "3210103289",
               "3210103459",
               "3210101644",
               "3210100537",
               "3210100971",
               "3210101017",
               "3210100861",
               "3210100574",
               "3210100954",
               "3210100668",
               "3210104404",
               "3210102866",
               "3210104064",
              ]

    nid = "N0019000100030001"
    cardNo = "3210105148"
    openid = "oO-a2t2kqS3ycna4T47qSH94a3QI"

    session = requests.session()
    session.headers = {
        'User-Agent':
        'Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4'
    }
    for i in classes:
        cardNo = i
        try:
            checkFlag = False

            # 获取token
            time.sleep(5)
            access_token = getAccessToken(session, openid)

            # 获取最新的章节
            time.sleep(5)
            current_course = getCurrentCourse(session, access_token)

            # 签到
            time.sleep(5)
            res, checkFlag = getJoin(session, access_token, current_course, nid,
                                     cardNo)


            res = json.loads(res)
            mydingpush = dingpush(
                "青年大学习签到结果",
                "青年大学习签到成功：\n" + "状态码：" + str(res["status"]) + "\n课程ID: " +
                current_course + "\n签到学号: " + res["result"]["cardNo"] +
                "\n签到时间: " + res["result"]["lastUpdTime"], "", DD_BOT_TOKEN,
                DD_BOT_SECRET)
            mydingpush.SelectAndPush()
        except Exception as e:
            print("WARNING: " + str(e))
            try:
                mydingpush = dingpush(
                    "青年大学习签到结果",
                    "青年大学习签到出现问题：\n" + str(e) + "\n是否完成签到：" + str(checkFlag), "",
                    DD_BOT_TOKEN, DD_BOT_SECRET)
            except Exception as e:
                print("ERROR: " + str(e))
    print("you have finished all the task")
    mydingpush = dingpush(
    "成功：\n",
    "已完成所有大学习打卡@陶秋宇" ," ",DD_BOT_TOKEN, DD_BOT_SECRET)
    mydingpush.SelectAndPush()
