#coding: utf-8
from functools import wraps
from tornado.web import HTTPError
from hashlib import md5
import datetime
from settings import STATIC_DIR
import geohash, math, time, os
import re
import ast


def validate_email(email):
    return re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email)

def str_to_dict(_str):
    """str to dict"""
    return ast.literal_eval(_str)

def get_attach(pic_path):
    #商品图片路径
    return pic_path
    return os.path.join(STATIC_DIR, pic_path)

def generate_access_token(user_id):
    raw_string = str(user_id) + "quseit_application_for_qutao"
    return md5(raw_string).hexdigest()

def generate_geohash(lng_lat, level = 6):
	#生成 geohash
	#5位长度：2.4km
	#6位长度：0.61km
	#7位长度：0.076
	#8位长度：0.01911
	#9：0.00478
    lng, lat = lng_lat.split(',')
    return geohash.encode(float(lat), float(lng), level)

def geohash_neighbors(geohashstr):
    return {'$in': geohash.expand(geohashstr)}

def haversine(*args):
    """
    计算两点距离
    经度1，纬度1，经度2，纬度2
    :returns 两点距离，单位为m
    """
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(lambda x: math.radians(float(x)), args)

    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371 # 地球平均半径，单位为公里
    return c * r * 1000

def filter_distance(datas, lng_lat, distance):
    """
    过滤距离
    :param distance: 限定的距离，单位为m 
    """
    return filter(lambda x: haversine(*(x['lng_lat'].split(',') + lng_lat.split(','))) <= distance, datas)

def auth_decorator(method):
    """auth验证装饰器
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        token = self.request.headers.get("token", "").strip()
        user_id = self.request.headers.get("userid", "").strip()
        
        # 验证token
        if len(user_id) != 24 or len(token) != 32 or token != generate_access_token(user_id):
            self.db.token_error.insert({"user_id": user_id, "data": repr(self.request)})
            raise HTTPError(500, "Error. Token error!")

        self.user_id = user_id
        return method(self, *args, **kwargs)
    return wrapper

def timestampTodate(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

def datetime2timestamp(dt):
    timestamp = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
    return timestamp

def get_service_fee(money):
    """
    计算手续费
    :param time: 创建时间
    """
    return round(float(money) * 0.03, 2)
