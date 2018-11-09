#coding:utf-8
import json
import time
import os
import tornado.web
from bson import ObjectId
from apps.api.common import BaseHandler
from lib.routes import route
from apps.api.utils import auth_decorator, generate_geohash


@route('/api/selling/(putaway|soldout)')
class ApiGoodsStatusHandler(BaseHandler):
    #商品上架、下架
    @auth_decorator
    def post(self, action_name):
        goods_id = self.get_argument("id")
        good = self.db.Goods.find_one({'_id': ObjectId(goods_id)})
        apply(self.__getattribute__(''.join(('_', action_name))))
        self.db.Goods_Community.update({"name": good['community']},
                                       {"$set": {'num': str(self.db.Goods.find({'community': good['community'], 'status': '0'}).count())}})

    def _putaway(self):
        #上架 status: 0
        goods_id = self.get_argument("id")
        if len(goods_id) == 24:
            self.db.Goods.update({"_id": ObjectId(goods_id)},
                                 {"$set": {"status": '0'}})
            # 清除缓存
            self.clear_cache("GoodsInfo:%s" % goods_id)
            return self.write_json({"errno": 0, "msg": "success"})
        return self.write_json({"errno": 100, "msg": "invalid goods_id"})

    def _soldout(self):
        #下架 status: 1
        goods_id = self.get_argument("id")
        if len(goods_id) == 24:
            self.db.Goods.update({"_id": ObjectId(goods_id)},
                                 {"$set": {"status": '1'}})
            
            # 清除缓存
            self.clear_cache("GoodsInfo:%s" % goods_id)
            return self.write_json({"errno": 0, "msg": "success"})
        return self.write_json({"errno": 100, "msg": "invalid goods_id"})
