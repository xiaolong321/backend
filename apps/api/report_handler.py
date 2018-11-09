#coding:utf-8
"""api 商品举报"""
import time
from bson import ObjectId
import tornado.web
from tornado import gen
from apps.api.common import BaseHandler
from lib.routes import route
from apps.api.utils import auth_decorator, generate_geohash
from apps.models import Goods
from lib.jpush import push_msg, JPush

@route('/api/selling/report')
class ApiSellingReport(BaseHandler, JPush):
    #举报商品
    @auth_decorator
    def get(self):
        #检查用户是否能举报商品
        pass

    @auth_decorator
    def post(self):
        goods_id = self.get_argument("id")
        query = {"goods_id": goods_id, "user_id": self.user_id}
        if goods_id: # and not self.db.Goods_report.find_one(query)
            self.db.Goods_report.update(query, query, True)
            goods = Goods.byid(self, goods_id)
            push_msg(goods.seller_id, u'您的商品%s被用户举报' % goods.goods_name, extra={'extra': 'extra_my_publish'})
            #self.push_all(u'商品%s被用户举报' % goods.goods_name, extra={'extra': 'extra_my_publish'})
        return self.write_success()
