#coding:utf-8
"""商品举报 管理"""
from apps.api.common import BaseHandler, json
from lib.routes import route
from lib.jpush import push_msg
from login_handler import login
from settings import PAGE_LIMIT, DISTANCE
from bson import ObjectId
from apps.api.utils import generate_geohash, geohash_neighbors, filter_distance,\
                           timestampTodate
import time


#@route('/manager/goods/report')
#class GoodsReportManager(BaseHandler):
#    def get(self):
#        return self.write_json({'errno': 0, 'msg': 'success'})

@route('/manager/goods/report')
class GoodsReport(BaseHandler):
    """举报商品列表"""
    def get(self):
        data = []
        last_count = abs(int(self.get_argument('page', 0))) #上次加载到第几条
        filter_data = self.db.Goods_report.find().sort('_id', -1).skip(last_count).limit(PAGE_LIMIT)
        for item in filter_data:
            item['report_user'] = self.get_cache_user_info(item['user_id'])
            item['goods_info'] = self.get_cache_goods_info(item['goods_id'])
            item['goods_info']['user_info'] = self.get_cache_user_info(item['goods_info']['seller_id'])
            data.append(item)

        obj =  {"data": data, "pagination": self.pagination(len(data), last_count)}
        
        return self.render('goods-report.html', **obj)


    @login()
    def post(self):
        _id = self.get_argument('id')
        if _id:
            # 删除
            self.db.Goods_report.remove({'_id': ObjectId(_id)})
            return self.write({'errno': 0, 'msg': 'success'})
        return self.write({'errno': 400, 'msg': 'invalid params'})

