#coding:utf-8
import json
from time import time
import tornado.web
from bson import ObjectId
from tornado import gen
from apps.api.common import BaseHandler
from lib.routes import route
from lib.jpush import push_msg, JPush
from apps.api.utils import auth_decorator, generate_geohash

__author__ = 'Anlim'

@route('/api/selling/like')
class ApiFavoriteHandler(BaseHandler, JPush):
    #收藏商品、取消收藏
    @auth_decorator
    def get(self):
        goods_id = self.get_argument("id")
        result = self.db.Favorite.find({"user_id": self.user_id, "goods_id": goods_id}).count()
        if result > 0:
            result = 1
        return self.write_success(result)

    @auth_decorator
    def post(self):
        #收藏/取消收藏
        goods_id = self.get_argument("id")
        action = int(self.get_argument("action"))
        fav_query = {"user_id": self.user_id, "goods_id": goods_id}
        exist = self.db.Favorite.find(fav_query).count() is not 0
        inc_collect_count = lambda inc: self.db.Goods.update({'_id': ObjectId(goods_id)}, {'$inc': {'collect_count': inc}})
        # 清除缓存
        self.clear_cache("GoodsInfo:%s" % goods_id)
        if action is 1:
            # 收藏
            print(exist)
            if not exist:
                fav_query["create_at"] = int(time())
                self.db.Favorite.insert(fav_query)
                inc_collect_count(1)
                seller_id = self.get_cache_goods_info(goods_id).get('seller_id')
                self.push_msg(seller_id, '%s赞了你的宝贝' % self.get_cache_user_info(self.user_id).get('nickname'))
                return self.write_success()
        else:
            # 收取消藏
            if exist:
                 self.db.Favorite.remove(fav_query)
                 inc_collect_count(-1)
                 return self.write_success()
        return self.write_err()

