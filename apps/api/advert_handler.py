#coding:utf-8
__author__ = 'Anlim'

from tornado.web import HTTPError
import time
import random
import tornado.web
from bson import ObjectId
from apps.api.common import BaseHandler
from apps.models import Goods, User, Goods_comment
from lib.routes import route
from apps.api.utils import auth_decorator, generate_geohash, geohash_neighbors, filter_distance, get_attach
import settings
from lib.jpush import push_msg, JPush


@route('/api/images')
class IndexImageHandler(BaseHandler):
    """app 首页轮播图"""
    def get(self):
        filter_data = self.db.AdImages.find({'is_delete': False}).sort('point', -1)
        data = []
        for item in filter_data:
            item['_id'] = str(item['_id'])
            item['link'] = settings.HOST + '/api/ad/redirect?aid=%s&redirect=%s' % (item['_id'], item['link'])
            data.append(item)
        return self.write_json({'errno': 0, 'msg': 'success', 'data': data})


@route('/api/ad/redirect')
class ApiAdRedirect(BaseHandler):
    """app 轮播图片点击跳转"""
    def get(self):
        redirect = self.get_argument('redirect', '')
        user_id = self.get_argument('user_id', '')
        aid = self.get_argument('aid', '')
        if redirect and aid:
            # 记录广告点击信息
            self.db.AdImagesClick.insert({'user_id': user_id, 'aid': aid, 'create_at': int(time.time())})
            # 跳转到advert link
            return self.redirect(redirect)
        
        raise HTTPError(500, "Error. invalid url!")


@route('/event/addfriends')
class AddFriends(BaseHandler):
    """添加微信朋友"""
    def get(self):
        return self.render('add-friends.html')


@route('/event/feedbackgetredpacket')
class FeedBackGetRedPacket(BaseHandler):
    """反馈送红包"""
    def get(self):
        return self.render("get-redpacket.html")
