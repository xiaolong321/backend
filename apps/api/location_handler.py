#coding:utf-8
import json
import time
from bson import ObjectId
import tornado.web
from tornado import gen
from apps.api.common import BaseHandler
from lib.routes import route
from apps.api.utils import auth_decorator, generate_geohash

@route('/api/selling/location')
class ApiSellingLocation(BaseHandler):
    #我的位置
    @auth_decorator
    def post(self):
        location = self.get_argument('location')
        lng_lat = self.get_argument("lng_lat")
        geohash = generate_geohash(lng_lat)
        self.db.Users.update({"_id": ObjectId(self.user_id)}, {"$set": {"lng_lat": lng_lat,
                                                                        "geohash": geohash,
                                                                        "location": location}})
        # 清除缓存
        self.clear_cache("UserInfo:%s" % self.user_id)

        return self.write_json({"errno": 0, "msg": "success"})
