#encoding: utf8
from __future__ import print_function

import json, requests



app_key = "2ef677a3ceba2906dfef5de9"
master_secret = "57a1a34e8a145ea4edc84388"


class JPush(object):
    def push_all(self, message, title=None, extra = 'extra_default'):
        headers = {
            'Content-Type': 'application/json'
        }
        extra = extra if isinstance(extra, dict) else {"extra": extra}
        payload = {
            "platform": "all",
            "audience": 'all',
            "notification": {
                "alert": message,
                "sound": "default",
                "badge": "+1",
                "ios": {
                    'extras': extra,
                    "sound": "default",
                    "badge": "1",
                },
                "android" : {
                    'extras': extra,
                },
            },
            "options": {
                "time_to_live": 86400,
                "apns_production": False, # True 表示推送生产环境，False 表示要推送开发环境
            }
        }
        if title:
            payload['notification']['title'] = title
        print(payload, ">>>>>>>")
        result = requests.post('https://api.jpush.cn/v3/push', auth=(app_key, master_secret), data=json.dumps(payload), headers=headers).content
        return result

    def push_msg(self, user_id, message, title = None, extra = 'extra_default'):
        headers = {
            'Content-Type': 'application/json'
        }
        extra = extra if isinstance(extra, dict) else {"extra": extra}
        payload = {
            "platform": "all",
            # "audience": {
            #     "registration_id": [jiguang_id]
            # },
            "audience" : {
                "alias" : [ user_id ],
            },
            "notification": {
                "alert": message,
                "sound": "default",
                "badge": "+1",
                "ios": {
                    'extras': extra,
                    "sound": "default",
                    "badge": "+1",
                },
                "android" : {
                    'extras': extra,
                },
            },
            "options": {
                "time_to_live": 86400,
                "apns_production": False, # True 表示推送生产环境，False 表示要推送开发环境
            }
        }
        if title:
            payload['notification']['title'] = title
        print(payload, ">>>>>>>")
        result = requests.post('https://api.jpush.cn/v3/push', auth=(app_key, master_secret), data=json.dumps(payload), headers=headers).content
        return result   

# u"您的商品被购买"
def push_msg(user_id, message, title = None, extra = 'extra_default'):
    headers = {
        'Content-Type': 'application/json'
    }
    extra = extra if isinstance(extra, dict) else {"extra": extra}
    payload = {
        "platform": "all",
        # "audience": {
        #     "registration_id": [jiguang_id]
        # },
        "audience" : {
            "alias" : [ user_id ],
        },
        "notification": {
            "alert": message,
            "sound": "default",
            "badge": "+1",
            "ios": {
                'extras': extra,
                "sound": "default",
                "badge": "+1",
            },
            "android" : {
                'extras': extra,
            },
        },
        "options": {
            "time_to_live": 86400,
            "apns_production": False, # True 表示推送生产环境，False 表示要推送开发环境
        }
    }
    if title:
        payload['notification']['title'] = title
    #if extra:
    #    payload['notification']['extra'] = extra if isinstance(extra, dict) else {"extra": extra}
    print(payload, ">>>>>>>")
    result = requests.post('https://api.jpush.cn/v3/push', auth=(app_key, master_secret), data=json.dumps(payload), headers=headers).content
    return result
