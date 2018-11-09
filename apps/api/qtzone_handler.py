#coding: utf-8
from bson import ObjectId
from apps.api.common import BaseHandler
from apps.api.utils import auth_decorator, generate_geohash, geohash_neighbors
from lib.routes import route
from apps.models import QtZone
import time
import settings


@route('/api/qutaozone/list')
class QutaoZone(BaseHandler):
    """趣淘圈列表"""
    @auth_decorator
    def get(self):
        data = []
        _lng_lat = self.get_argument("lan_lat", '')
        last_count = int(self.get_argument('last_count', 0)) #上次加载到第几条

        _geohash = geohash_neighbors(generate_geohash(_lng_lat)) if _lng_lat else {'$ne': None}
        filter_data = self.db.QtZone.find({'geohash': _geohash}).sort('time', -1).skip(last_count).limit(settings.PAGE_LIMIT)
        #filter_data = self.db.QtZone.find().sort('time', -1).skip(last_count).limit(settings.PAGE_LIMIT)
        for item in filter_data:
            item['_id'] = str(item['_id'])
            item['goods_id'] = str(item['goods_id'])
            # 用户信息
            user_info = self.get_cache_user_info(item['user_id'])
            user_extends = self.db.User_extend.find_one({'user_id': item['user_id']})
            if user_extends:
                user_info['hx_username'] = self.db.User_extend.find_one({'user_id': item['user_id']}).get('hx_username')
            
            item['user_info'] = user_info
            # 商品信息, type 0 发布，1评论，2 求购，求购时没有goods_id
            item['goods_info'] = {}
            if item['goods_id']:
                goods_info = self.get_cache_goods_info(item['goods_id'])
                goods_info['seller_name'] = self.get_cache_user_info(goods_info['seller_id']).get('nickname')
                item['goods_info'] = goods_info
            # 获取评论信息
            if item.get('comment_id'):
                item['comment_id'] = str(item['comment_id'])
                comment_info = self.db.Goods_comment.find_one({'_id': ObjectId(item['comment_id'])})
                comment_info = comment_info or {} 
                if comment_info:
                    comment_info.pop('_id')
                item['comment_info'] = comment_info
            item['buy_info'] = {'buy_msg': item['buy_msg']}
            item.pop('buy_msg')
            data.append(item)
        return self.write_json({'errno': 0, 'msg': 'success', 'data': data})

@route('/api/selling/buy')
class QutaoZoneBuy(BaseHandler):
    """发布求购信息"""
    @auth_decorator
    def post(self):
        buy_msg = self.get_argument('msg', '')
        u = self.get_cache_user_info(self.user_id) 
        lng_lat = self.get_argument('lng_lat') or u.get('lng_lat', '')

        _geohash = generate_geohash(lng_lat)
        self.db.QtZone.insert({
            'type': 2, # 0 发布，1 评论，2 求购
            'goods_id': '', # 空
            'user_id':  self.user_id, 
            'time': int(time.time()),
            'buy_msg': buy_msg,
            "lng_lat": lng_lat,
            "geohash": _geohash,
        })
        return self.write_json({'errno': 0, 'msg': 'success'})
