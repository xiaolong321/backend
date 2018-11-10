#coding:utf-8
from apps.api.common import BaseHandler
from lib.routes import route
from bson import ObjectId
from .login_handler import login
from settings import PAGE_LIMIT
import time

INDEX_TABS = [u'上架中', u'已下架', u'已归档']

@route('/manager/index/')
class IndexHandler(BaseHandler):
    @login()
    def get(self):

        """
        #remove all
        self.db.Goods.remove({})
        self.db.Wechat_extend.remove({})
        self.db.User.remove({})
        self.db.User_extend.remove({})
        self.db.Goods_Type.remove({})
        self.db.Goods_Community.remove({})
        """
        search = self.get_argument('search', '')
        page = int(self.get_argument("page", 1))
        page = 1 if page <=1 else page
        sele = self.db.Goods.find({
            '$or': [
                {'goods_name': {'$regex': search}}, 
                {'seller_id': self.get_user_id(search)}
            ]
        }).sort("_id", -1)
        num = sele.count()
        if page <= 1:
            sele = sele.limit(PAGE_LIMIT)
        else:
            sele = sele.skip((page-1) * PAGE_LIMIT).limit(PAGE_LIMIT)
        data = self.fix_goods(sele)

        obj = {
            'data': data,
            'tabs':INDEX_TABS,
            'pagination': self.pagination(num, page),
        }
        return self.render("index.html", **obj)

@route('/manager/api/pull-off-shelves')
class PullOffShelvesHandler(BaseHandler):
    @login()
    def get(self):
        # 3天前的商品自动下架
        self.db.Goods.update({
            'last_update_at': {
                '$lte': int(time.time() - 3 * 24 * 60 * 60)
            },
            'status': '0'
        },
        {'$set': {'status': '1'}}, multi=True)
        return self.redirect(self.request.headers.get("Referer"))

@route('/manager/api/update/goods')
class SetGoodsStatus(BaseHandler):
    @login()
    def get(self):
        gid = self.get_argument('gid', False)
        attr = self.get_argument('attr', False)
        value = self.get_argument('v', False)
        if gid and attr and value:
            #self.db.Goods.remove({"_id": ObjectId(gid)})#从数据库内删除
            self.db.Goods.update({"_id": ObjectId(gid)},
                                 {"$set": {attr: value}})
            good = self.db.Goods.find_one({'_id': ObjectId(gid)})
            self.db.Goods_Community.update({"name": good['community']},
               {"$set": {'num': str(self.db.Goods.find({'community': good['community'], 'status': '0'}).count())}})
            if self.isAjax():
                return self.write_success()
            return self.redirect(self.request.headers.get("Referer"))
        return self.write_json({"errno": 100, "msg": "error gid or status"})

@route('/manager/search/')
class SearchHandler(BaseHandler):
	#搜索
	@login()
	def post(self):
		self.write_json("ok")
