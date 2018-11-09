#coding:utf-8
from apps.api.common import BaseHandler, json
from lib.routes import route
from lib.qiniu_class import Uploader
from login_handler import login
from settings import PAGE_LIMIT, DISTANCE, TMP_PATH, Advert_Type
from bson import ObjectId
from apps.api.utils import generate_geohash, geohash_neighbors, filter_distance,\
                           timestampTodate, str_to_dict

__author__ = 'Anlim'


@route('/manager/advert')
class AdManagerHandler(BaseHandler):
    """app 轮播图管理"""
    @login()
    def get(self):
        last_count = int(self.get_argument('page', 0)) #上次加载到第几条
        filter_data = self.db.AdImages.find({'is_delete': False}).sort('_id', -1)
        data = []
        for item in filter_data.skip(last_count).limit(PAGE_LIMIT):
            item['click_count'] = self.db.AdImagesClick.find({'aid': str(item['_id'])}).count()
            data.append(item)

        obj = dict(
            Advert_Type = Advert_Type,
            data = data,
            pagination = self.pagination(filter_data.count(), last_count)
        )        
        return self.render('ad-manager.html', **obj)
    
    @login()
    def post(self):
        _id = self.get_argument('id', '')
        action = self.get_argument('action', '')
        if _id and action:
            if action == u'delete':
                self.db.AdImages.update({'_id': ObjectId(_id)}, {'$set': {'is_delete': True}})
                return self.write_json({'errno': 0, 'msg': 'success'})

        return self.write_json({'errno': 400, 'msg': 'invalid data'})


@route('/manager/images/add')
class AdvertAddHandler(BaseHandler):
    """app 轮播图添加"""
    @login()
    def get(self):
        obj = dict(
            type_list = Advert_Type
        )        
        return self.render('advert-add.html', **obj)

    @login()
    def post(self):
        name = self.get_argument('name', '')
        _type = self.get_argument('type', '')
        link = self.get_argument('link', '')
        point = self.get_argument('point', '')
        images = self.get_argument('images', '')
        if name and _type and link and images:
            data = {
                'name': name,
                'type': _type,
                'link': link,
                'point': point,
                'images': images,
                'click_count': 0, # 点击数量
                'is_delete': False,
            }
            self.db.AdImages.insert(data)
            return self.write_json({'errno': 0, 'msg': 'success', 'next_url': '/manager/advert'})
        return self.write_json({'errno': 400, 'msg': 'invalid data'})
