#coding:utf-8
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


__author__ = 'Anlim'

@route('/api/goods')
class ApiGoodsHandler(BaseHandler):
    """商品列表"""
    #@auth_decorator
    def get(self):
        user_id = self.request.headers.get("userid", "").strip()
        if user_id:
            # 修改最后更新时间
            self.db.User.update({'_id': ObjectId(user_id)}, {'$set': {'last_update': int(time.time())}})
            # 清除缓存
            self.clear_cache('UserInfo:%s' % user_id)

        _lng_lat = self.get_argument("lng_lat", '')
        _community = self.get_argument("community", '')
        goods_type = self.get_argument("goods_type", '')
        _geohash = geohash_neighbors(generate_geohash(_lng_lat)) if _lng_lat else {'$ne': None}
        last_count = int(self.get_argument('last_count', 0)) #上次加载到第几条
        # 过滤下架、删除商品的功能
        find_data = {'status': '0', 'review': {'$in': ['0', '1']} }
        if _community:
            find_data['community'] = _community
        else:
            find_data['geohash'] = _geohash

        if goods_type:
            find_data['goods_type'] = goods_type
        else:
            # 首页精选
            find_data['is_select'] = '1'

        data = []
        goods = Goods(self)
        # select = {k: 1 for k in ("lng_lat", "can_pay_online", "introduce", "goods_name", "images", "price", "seller_id")}
        if last_count > 0:
            last_count = last_count +1

        goods_list = self.db.Goods.find(find_data).sort('last_update_at', -1)
        
        goods_list = goods_list.skip(last_count).limit(settings.PAGE_LIMIT)
        if _lng_lat:
            goods_list = filter_distance(goods_list, _lng_lat, settings.DISTANCE)
        
        if not len(list(goods_list)):
            # 当位置没有商品时，取全局推送的商品
            find_data = {'status': '0', 'review': {'$in': ['0', '1']}, 'is_global': '1', 'is_select': '1'}
            #find_data = {'is_global': '1'}
            goods_list = self.db.Goods.find(find_data).sort('last_update_at', -1)

            goods_list = goods_list.skip(last_count).limit(settings.PAGE_LIMIT)

        for item in goods_list:
            #item['images'] = [img+"?imageMogr2/thumbnail/140x140!" for img in item['images'] ]
            goods.setdata(item)
            goods.strid()
            goods.import_seller_info()
            goods.can_pay_online = goods.can_pay_online
            del goods.lng_lat
            data.append(goods._data)
        self.write_json({"errno": 0, "msg": "ok", "data": data})


@route('/api/goods/info')
class ApiGoodsDetail(BaseHandler):
    #商品详情
    #@auth_decorator
    def post(self):
        # 是否登录
        user_id = self.request.headers.get("userid", "").strip()
        goods_id = self.get_argument("id")
        if user_id:
            self.user_id = user_id
            #记录访问记录
            self.db.GoodsRecord.insert({"user_id": self.user_id,
                                        "goods_id": goods_id,
                                        "create_at": int(time.time())})

        goods = Goods.byid(self, goods_id)
        if goods:
            # u = self.db.User.find_one({"_id": ObjectId(data["seller_id"])})
            goods.strid()
            goods.import_seller_info_plus()
            goods.can_pay_online = goods.can_pay_online
            # 是否收藏
            goods.is_collect = 1 if goods.collected else 0
            # 评论信息
            comment_cusor = self.db.Goods_comment.find({"goods_id": goods_id}).sort("comment_time", -1).limit(4)
            comments = []
            comment  = Goods_comment(self)
            for item in comment_cusor:
                item['_id'] = str(item['_id'])
                user_info = self.get_cache_user_info(item['user_id'])
                if user_info:
                    user_info['nick'] = user_info['nickname']
                    item = dict(item, **user_info)
                    comments.append(item)
                #comment.setdata(item)
                #del comment._id
                #comments.append(comment._data)
            goods.comments = comments

        
        #商品统计：self.redis.setbit(today timestamp, goods_id, 1)
        return self.write_success(goods._data)

@route('/api/selling/collect')
class ApiSellingCollect(BaseHandler):
    #获取收藏商品列表
    @auth_decorator
    def get(self):
        data = []
        last_count = int(self.get_argument('last_count', 0)) #上次加载到第几条
        favorites = self.db.Favorite.find({"user_id": self.user_id}).sort("_id", -1).skip(last_count).limit(settings.PAGE_LIMIT)
        for f in favorites:
            goods = Goods.byid(self, f["goods_id"])
            if goods and goods.status in ('0','1'):
                goods.import_seller_info_plus()
                goods.strid()
                data.append(goods._data)
        return self.write_success(data)


@route('/api/goods_list')
class ApiSellingGoodsList(BaseHandler):
    '''查看卖家商品列表'''
    def get(self):
        userid = self.get_argument('userid', None)
        last_count = int(self.get_argument('last_count', 0)) #上次加载到第几条
        if not userid:
            return self.write_json({'errno': 404, 'msg': 'not found data'})

        data = []
        goods = self.db.Goods.find({"status":{"$in": ["1", "0"]},
                                    "seller_id": userid
                                   }).sort("_id", -1).skip(last_count).limit(settings.PAGE_LIMIT)
        for i in goods:
            i["_id"] = str(i["_id"])
            data.append(i)
        return self.write_json({"errno": 0,
                                "msg": "success",
                                "data": data})


@route('/api/selling/sell')
class ApiSellingProfile(BaseHandler):
    #个人商品
    @auth_decorator
    def get(self):
        data = []
        last_count = int(self.get_argument('last_count', 0)) #上次加载到第几条
        goods = self.db.Goods.find({
            "status":{"$in": ["1", "0"]},
            "seller_id": self.user_id
        }).sort("_id", -1).skip(last_count).limit(settings.PAGE_LIMIT)
        for i in goods:
            i["_id"] = str(i["_id"])
            data.append(i)
        return self.write_json({
            "errno": 0,
            "msg": "success",
            "data": {"sell": data}
        })

@route('/api/selling/del')
class ApiSellingDel(BaseHandler):
    """商品删除、归档"""
    @auth_decorator
    def post(self):
        goods_id = self.get_argument("id", '')
        self.db.Goods.update({"_id": ObjectId(goods_id)},
                                 {"$set": {"status":  '2'}})

        # 清除缓存
        self.clear_cache('GoodsInfo:%s' % goods_id)

        return self.write_json({
            "errno": 0,
            "msg": u"删除成功"
        })

@route('/api/selling/type')
class ApiSellingType(BaseHandler):
    """商品类别"""
    def get(self):
        goods_type = self.db.Goods_Type.find().sort('seq', -1)
        data = []
        for i in goods_type:
            i.pop('_id')
            data.append(i)
        return self.write_json({"errno": 0, "msg": "success", "data": data})

@route('/api/selling/community')
class ApiSellingCommunity(BaseHandler):
    """商品小区"""
    def get(self):
        _lng_lat = self.get_argument("lng_lat", False)
        _geohash = geohash_neighbors(generate_geohash(_lng_lat)) if _lng_lat else {'$ne': None}
        goods_community = self.db.Goods_Community.find({'geohash': _geohash})
        data = []
        for i in filter_distance(goods_community, _lng_lat, settings.DISTANCE):
            i.pop('_id')
            data.append(i)
        return self.write_success(data)


@route('/api/goods/recommend')
class ApiGoodsRecommend(BaseHandler):
    '''商品推荐'''
    @auth_decorator
    def get(self):
        _self = self.db.User.find_one({'_id': ObjectId(self.user_id)})
        similar_user = self.db.User.find({
            'geohash': _self['geohash'],
            'sex': _self['sex'],
            'age': _self['age']
        })
        if similar_user.count() < 10:
            similar_user = self.db.User.find({
                'geohash': _self['geohash'],
            })

        data = []
        for user in similar_user:
            sele = self.db.Goods.find({
                'seller_id': str(user['_id'])
            })
            for good in sele:
                good['_id'] = str(good['_id'])
                data.append(good)
        data = random.sample(data, 8 if len(data) >= 8 else len(data))
        return self.write_json({"errno": 0, "msg": "success", "data": data})

@route('/api/selling/comment')
class ApiGoods_comment(BaseHandler, JPush):
    '''商品评价'''
    def get(self):
        goods_id = self.get_argument("id", 0)
        last_count = int(self.get_argument('last_count', 0)) #上次加载到第几条
        datas = self.db.Goods_comment.find({"goods_id": goods_id}).sort("comment_time", -1).skip(last_count).limit(settings.PAGE_LIMIT)
        comments = []
        comment = Goods_comment(self)
        for item in datas:
            item['_id'] = str(item['_id'])
            user_info = self.get_cache_user_info(item['user_id'])
            if user_info:
                user_info['nick'] = user_info['nickname']
                item = dict(item, **user_info)
                comments.append(item)
            #comment.setdata(item)
            #del comment._id
            #comments.append(comment._data)
        return self.write_success(comments)

    @auth_decorator
    def post(self):
        '''提交评价'''
        goods_id = self.get_argument("id", 0)
        comment_body  = self.get_argument("comment_body", 0)
        _id = self.db.Goods_comment.insert({
            "user_id": self.user_id,
            "goods_id": goods_id,
            "comment_body": comment_body,
            "comment_time": int(time.time())
        })
        #  发布到趣淘圈
        user_info = self.get_cache_user_info(self.user_id)
        self.db.QtZone.insert({
            'type': 1, # 0 发布，1 评论，2 求购
            'goods_id': goods_id,
            'comment_id': _id,
            'user_id':  self.user_id, 
            'time': int(time.time()),
            'buy_msg': '',
            "lng_lat": user_info.get('lng_lat'),
            "geohash": user_info.get('geohash'),
        })
        # 推送消息
        # - 给发布者推送消息
        m = '您的商品%s 被%s评论，赶紧去看下吧~' % (self.get_cache_goods_info(goods_id).get('goods_name'), self.get_cache_user_info(self.user_id).get('nickname'))
        self.push_msg(self.get_cache_goods_info(goods_id).get('seller_id'), m, extra={'extra': 'extra_qtzone'})

        # 给评论用户推送
        user_list = []
        for item in self.db.Goods_comment.find({'goods_id': goods_id}):
            if not  item['user_id'] in user_list and item['user_id'] != self.user_id:
                msg = '商品%s, 被%s评论了，赶紧去抢沙发吧~' % (self.get_cache_goods_info(item['goods_id']).get('goods_name'), self.get_cache_user_info(self.user_id).get('nickname'))
                self.push_msg(item['user_id'], msg, extra={'extra': 'extra_qtzone'})
                user_list.append(item['user_id'])

        self.write_success()
