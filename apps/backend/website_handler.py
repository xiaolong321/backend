#coding:utf-8
"""网站页面handler"""
from apps.api.common import BaseHandler
from lib.routes import route
from bson import ObjectId
from .login_handler import login
from settings import PAGE_LIMIT, iOS_download, Android_download
import time



@route('/')
class WebsiteIndex(BaseHandler):
    '''网站首页'''
    def get(self):
        page = int(self.get_argument("page", 1))
        goods_type = self.get_argument('goods_type', '')

        goods_filter= self.db.Goods.find({'status': '0', }).sort('_id', -1)
        if goods_type:
            goods_filter = self.db.Goods.find({'status': '0', 'goods_type': goods_type})
        num = goods_filter.count()
        if page <= 1:
            goods_filter = goods_filter.limit(PAGE_LIMIT)
        else:
            goods_filter = goods_filter.skip((page-1) * PAGE_LIMIT).limit(PAGE_LIMIT)

        obj = dict(
            iOS_download=iOS_download,
            Android_download=Android_download,
            goods_type_list = self.db.Goods_Type.find(),
            goods_type_nav = self.db.Goods_Type.find(),
            goods_list = goods_filter,
            pagination = self.pagination(num, page),
        )
        return self.render('web.html', **obj)
