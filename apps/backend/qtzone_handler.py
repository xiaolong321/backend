#coding:utf-8
from apps.api.common import BaseHandler, json
from lib.routes import route
from lib.jpush import push_msg
from .login_handler import login
from settings import PAGE_LIMIT, DISTANCE
from bson import ObjectId
from apps.api.utils import generate_geohash, geohash_neighbors, filter_distance
import time


@route('/manager/qtzone/list')
class QtZoneList(BaseHandler):
    """趣淘圈列表"""
    @login()
    def get(self):
        data = []
        #_lng_lat = self.get_argument("lan_lat", False)
        last_count = int(self.get_argument('page', 0)) #上次加载到第几条

        #_geohash = geohash_neighbors(generate_geohash(_lng_lat)) if _lng_lat else {'$ne': None}
        filter_data = self.db.QtZone.find().sort('time', -1)
        for item in filter_data.skip(last_count).limit(PAGE_LIMIT):
            item['_id'] = str(item['_id'])
            item['goods_id'] = str(item['goods_id'])
            user_info = self.get_cache_user_info(item['user_id'])
            item['user_info'] = user_info
            #item = dict(item, **user_info)
            if item['goods_id']:
                goods_info = self.get_cache_goods_info(item['goods_id'])
                item = dict(item, **goods_info)
            data.append(item)
        obj =  {"data": data, "pagination": self.pagination(len(data), last_count)}
        #return self.write_json({'errno': 0, 'msg': 'success', 'data': data})
        return self.render('qtzone_list.html', **obj)

    @login()
    def post(self):
        _id = self.get_argument('id')
        if _id:
            # 删除
            self.db.QtZone.remove({'_id': ObjectId(_id)})
            return self.write({'errno': 0, 'msg': 'success'})
        return self.write({'errno': 404, 'msg': 'invalid params'})
        
