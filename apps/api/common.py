#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division

import time, datetime
import settings
import json
from bson import ObjectId
try:
    import ujson as json
except ImportError:
    import json
# import urlparse
import ast
import urllib
import math
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
import tornado.web
from settings import PAGE_LIMIT
from apps.api.utils import timestampTodate


# object转json
def str_json(obj):
    if type(obj) is dict:
        return {k: str_json(v) for k, v in obj.iteritems()}
    if type(obj) is list:
        return [str_json(i) for i in obj]
    return str(obj)

class BareboneHandler(tornado.web.RequestHandler):
    """底层的handler 用以解决各个资源组件连接"""
    def __init__(self, application, request, **kwargs):
        #处理
        super(BareboneHandler, self).__init__(application, request, **kwargs)
        if request.headers.get("cdn-src-ip", None):
            request.remote_ip = request.headers["cdn-src-ip"]
        elif request.headers.get("X-Forwarded-For", None):
            try:
                request.remote_ip = request.headers["X-Forwarded-For"].split(",")[0]
            except Exception as e:
                print(e)
        # 打印所有get参数
        # print {k:''.join(v) for k,v in self.request.arguments.iteritems()}

    @property
    def db(self):
        return self.application.con[settings.DATABASE_NAME]

    @property
    def huanxin(self):
        return self.application.huanxin

    @property
    def redis(self):
        return self.application.redis

    @property
    def log(self):
        return self.application.log

    def write_json(self, obj):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(obj)

    def write_success(self, data = None):
        result = {"errno": 0, "msg": "success", "data": data}
        if data is None:
            del result['data']
        self.write_json(result)

    def write_err(self, err = ""):
        self.write_json({"errno": 1, "msg": err})

    def get_user_info(self, user_id = None, keys = None):
        return self.db.User.find_one(
            {"_id": ObjectId(user_id or self.user_id)},
            {key: 1 for key in keys} if keys else None)

    def get_user_id(self, user_name):
        user = self.db.User.find_one({"nickname": user_name})
        return str(user['_id']) if user else u'!肯定不存在的东西!'

    def paginator(self, result_count):
        #计算总页数，向上取整，向下取整math.floor
        return int(math.ceil(result_count / PAGE_LIMIT))

    def datetime2timestamp(self, d):
        # datetime 2 timestamp
        return int(time.mktime(d.timetuple()))

    def timestamp2datetime(self, dt):
        return datetime.datetime.fromtimestamp(dt).strftime('%Y-%m-%d')

    def dataTable(self, cls, dint):
        #获取7天数据
        data = []
        dates = []
        ndata = []
        for i in range(7):
            day = 7 - i
            yday = day -1
            ydint = dint-yday*86400
            ndint = dint - day*86400
            dates.append(self.timestamp2datetime(ndint))
            data.append(self.db[cls].find({"last_up_at": {"$gt": ndint,
                                                          "$lt": ydint}}).count())
            ndata.append(self.db[cls].find({"create_at": {"$gt": ndint,
                                                          "$lt": ydint}}).count())
        return data, dates, ndata

    def fix_goods(self, list):
        data = []
        for i in list:
            i["_id"] = str(i["_id"])
            i["image"] =  ''#get_attach(i.get("images", '/static/images/'))
            i["create_at"] = timestampTodate(i["create_at"])
            i["seller"] = self.get_user_info(i["seller_id"])["nickname"] if self.get_user_info(i["seller_id"]) else ""
            data.append(i)
        return data

    def pagination(self, num, page):
    # TODO 搜索后的分页跳转会清掉s=xx
        page_num = num//PAGE_LIMIT + (not (not num%PAGE_LIMIT))
        page_list = range(page_num)[page-3 if page-3 >=0 else 0:page+3 if page+3 <= page_num else page_num]
        page_list = [str(x+1) for x in page_list]
        if '1' not in page_list:
            page_list = (['1'] if '2' in page_list else ['1', '...']) + page_list
        if str(page_num) not in page_list:
            page_list = page_list + ([str(page_num)] if str(page_num - 1) in page_list else ['...', str(page_num)])
        return self.render_string("pagination.html", **{
            'num': num,
            'page': page,
            'page_num': page_num,
            'page_list': page_list
        })

    def db_find_all(self, db, query = None, desc_and_by_count = None, keepid = False):
        """
        取出数据库中的数据
        tuple desc_and_by_count [0]为逆序排序的字段, [1]为last_count
        """

        def _id_to_str(item):
            item['_id'] = str(item['_id'])
        def _id_pop(item):
            item.pop('_id')
        data = []
        fn = _id_to_str if keepid else _id_pop
        cursor = self.db[db].find(query)
        if isinstance(desc_and_by_count, tuple):
            cursor = cursor.sort(desc_and_by_count[0], -1).skip(desc_and_by_count[1]).limit(PAGE_LIMIT)
        for item in cursor:
            fn(item)
            data.append(item)
        return data

    def db_join_data(self, data, db, key, tkey=None, select=None):
        """
        当前data联合查询的数据
        :param data: 当前数据
        :param db:   目标db名
        :param key:  当前查询db的键
        :param tkey: 目标db的键，默认和key相同
        :param select: 要过滤的字段集合
        :returns 目标表字典
        """
        if not tkey:
            tkey = key
        if tkey is '_id' and key is not tkey:
            getval = lambda v: ObjectId(v)
            getkey = lambda k: str(k)
        else:
            getval = lambda v: v
            getkey = getval
        values = [getval(item[key]) for item in data] # 要匹配的键的值集合
        # 目标游标
        if select:
            select = {key: 1 for key in select}
        targets = self.db[db].find({tkey: {'$in':values}}, select)
        # 目标列表
        return {getkey(target[tkey]): target for target in targets}

    def isAjax(self):
        return self.request.headers.get('X-Requested-With', '') == 'XMLHttpRequest'

    def get_args(self, keys, rules = None):
        from lib.type import Map
        data = Map()
        for key in keys:
            value = self.get_argument(key, None)
            if rules and key in rules:
                # sample: (int, 1)
                value = rules[key][0](value) if value is not None else rules[key][1]
            data[key] = value
        return data


class BaseHandler(BareboneHandler):
    """基础handler 类"""
    cache_expire = 86400
    @property
    def cache(self):
        """用redis 做缓存"""
        return self.redis
    
    def cache_set(self, key, value):
        # cache set and set expire
        self.cache.set(key, value)
        self.cache.expire(key, self.cache_expire)
    
    def cache_get(self, key):
        # cache get key
        return self.cache.get(key)
    
    def clear_cache(self, key):
        # 清除缓存
        self.cache_set(key, '')
    
    def get_cache_user_info(self, user_id):
        """获取cache 用户信息"""
        #self.cache.set('UserInfo:%s' % user_id, '')
        obj = self.cache_get('UserInfo:%s' % user_id)
        if not obj:
            obj = self.db.User.find_one({'_id': ObjectId(user_id)})
            if obj:
                obj['_id'] = str(obj['_id'])
                self.cache_set('UserInfo:%s' % user_id, obj)
            obj = {}
        else:
            # str to dict
            obj = ast.literal_eval(obj)
        return obj

    def get_cache_goods_info(self, goods_id):
        """获取cache 商品信息 """
        #self.cache.set('GoodsInfo:%s' % goods_id, '')
        goods_info = self.cache_get('GoodsInfo:%s' % goods_id)
        if not goods_info:
            goods_info = self.db.Goods.find_one({'_id': ObjectId(goods_id)})
            goods_info.pop('_id')
            self.cache_set("GoodsInfo:%s" % goods_id, goods_info)
        else:
            # str to dict
            goods_info = ast.literal_eval(goods_info)
        return goods_info

    def send_log(self, *args):
        """发送日志，后台记录"""
        try:
            self.log.publish(settings.NAMESPACE, ",".join(map(str, args)))
        except ConnectionError as e:
            print("send_log error", args, e)


class MaintainHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write({"error": 1, "msg": "We are busy updating the server for you and will be back shortly.\n"
                                       "我們正忙著為您更新服務器，馬上回來。\n"
                                       "私たちはあなたのために、サーバーを更新忙しく、すぐに戻ってくる。\n"
                                       "เราจะยุ่งปรับปรุงเซิร์ฟเวอร์สำหรับคุณและจะกลับมาในไม่ช้า"})

    def post(self, *args, **kwargs):
        self.get()

    def delete(self, *args, **kwargs):
        self.get()

class SimpleException(Exception):
    """基本异常类"""
    __data = ""
    def __init__(self, data):
        self.__data = data

    def __str__(self):  # 相当于 str(#)
        return self.__data
