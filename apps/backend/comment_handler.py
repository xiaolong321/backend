#coding: utf-8 
"""评论管理"""
from apps.api.common import BaseHandler, json
from lib.routes import route
from lib.jpush import push_msg
from lib.qiniu_class import Uploader
from lib.excelRead import excel_table_byindex
from login_handler import login
from settings import PAGE_LIMIT, DISTANCE, TMP_PATH 
from bson import ObjectId
from apps.api.utils import generate_geohash, geohash_neighbors, filter_distance,\
                           timestampTodate, str_to_dict
import time, os, datetime


@route('/manager/comment')
class CommentManagerHandler(BaseHandler):
    """评论管理"""   
    def get(self):
        data = []
        last_count = int(self.get_argument('page', 0)) #上次加载到第几条

        filter_data = self.db.Goods_comment.find().sort('time', -1)
        for item in filter_data.skip(last_count).limit(PAGE_LIMIT):
            item['_id'] = str(item['_id'])
            item['goods_id'] = str(item['goods_id'])
            user_info = self.get_cache_user_info(item['user_id'])
            item['user_info'] = user_info
            if item['goods_id']:
                goods_info = self.get_cache_goods_info(item['goods_id'])
                item['goods_info'] = goods_info
                #item = dict(item, **goods_info)
            data.append(item)
        obj =  {"data": data, "pagination": self.pagination(len(data), last_count)}
        return self.render('comment-list.html', **obj)

    @login()
    def post(self):
        _id = self.get_argument('id')
        if _id:
            # 删除
            self.db.Goods_comment.remove({'_id': ObjectId(_id)})
            return self.write({'errno': 0, 'msg': 'success'})
        return self.write({'errno': 404, 'msg': 'invalid params'})

