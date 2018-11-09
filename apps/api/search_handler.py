#coding: utf-8
import json
import time
import os
import tornado.web
from bson import ObjectId
from apps.api.common import BaseHandler
from apps.models import Goods
from lib.routes import route
from apps.api.utils import auth_decorator, generate_geohash, geohash_neighbors, filter_distance, get_attach
import settings

__author__ = 'Anlim'

@route('/api/searchtemp')
class ApiSearchTempHandler(BaseHandler):
    #热门搜索
    def get(self):
        data = ['a', 'b', 'c', 'd', 'e', 'f']
        return self.write_json({"errno": 0,
                                "msg": 'success',
                                "data": data})

@route('/api/search')
class ApiSearchHandler(BaseHandler):
    #搜索商品
    #@auth_decorator
    def get(self):
        _lng_lat = self.get_argument("lng_lat", False)
        _goods = self.get_argument("keyword", '')
        last_count = int(self.get_argument('last_count', 0)) #上次加载到第几条
        data = []
        #print _goods
        #print type(_goods)
        query = {
            "goods_name": {'$regex': _goods},
            'status': '0',
            'review': {'$in': ['0', '1']}
        }
        if _lng_lat:
           query['geohash'] = geohash_neighbors(generate_geohash(_lng_lat))
        datas = self.db.Goods.find(query).skip(last_count).limit(settings.PAGE_LIMIT)
        if _lng_lat:
            datas = filter_distance(datas, _lng_lat, settings.DISTANCE)
        goods = Goods(self)
        for i in datas:
            goods.setdata(i)
            goods.strid()
            goods.import_seller_info()
            data.append(goods._data)
        self.write_success(data)


@route('/api/typesearch')
class ApiTypesearchHandler(BaseHandler):
    #搜索商品
    @auth_decorator
    def post(self):
        goods_type = self.get_argument("goods_type")
        data = []
        goods = self.db.Goods.find({"goods_type": goods_type})
        for i in goods:
            i["_id"] = str(i["_id"])
            i["images"] = i["images"] if i["images"] else []
            data.append(i)
        self.write_json({"errno": 0, "msg": "ok", "data": data})
