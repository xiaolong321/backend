#coding:utf-8
import time
from bson import ObjectId
import tornado.web
from tornado import gen
from apps.api.common import BaseHandler
from lib.routes import route
from apps.api.utils import auth_decorator, generate_geohash
from settings import PIC_PATH
import uuid, os


@route('/api/selling/goods')
class SellingGoods(BaseHandler):
    #发布商品
    @auth_decorator
    def get(self):
        #检查用户是否可以发布商品。被举报的用户不能发布商品
        self.write_json({"errno": 0, "msg": "success"})

    @auth_decorator
    #@gen.coroutine
    def post(self):
        # 默认使用用户的位置，可以选择实时位置
        goods_name = self.get_argument("title")
        goods_type = self.get_argument("goods_type")
        introduce = self.get_argument("introduce")
        price = self.get_argument("price")
        is_new = self.get_argument("is_new", "0")
        u = self.get_cache_user_info(self.user_id) 
        # hx = self.db.User_extend.find_one({"user_id": self.user_id})
        location = self.get_argument('location') or u.get('location', '')
        lng_lat = self.get_argument('lng_lat') or u.get('lng_lat', '')
        _geohash = generate_geohash(lng_lat)
        tag = self.get_argument("tag", '')
        file_count = int(self.get_argument('file_count', 0))
        images = self.get_argument('images', '').split(',')
        can_pay_online = self.get_argument('can_pay_online', "0")
        self.attach = []
        #for f in range(file_count):
        #    _file = self.request.files.get("pic%s" % f)
        #    if bool(_file):
        #        fname = _file[0]["filename"]
        #        extn = os.path.splitext(fname)[1]
        #        cname = str(uuid.uuid4()).replace("-", '') + extn
        #        with open(PIC_PATH + cname, 'wb') as f:
        #            f.write(_file[0]['body'])
        #            self.attach.append(cname.strip())
        goods_id = self.db.Goods.insert({
            "goods_name": goods_name,
            "goods_type": goods_type,
            "introduce": introduce,
            "price": price,
            "location": location,
            "lng_lat": lng_lat,
            "community": '',
            "geohash": _geohash,
            "images": images,
            "can_pay_online": can_pay_online,
            "collect_count": 0,
            "seller_id": self.user_id,
            # "seller_nickname": u['nickname'],
            # "seller_hx_name": hx['hx_username'],
            # "seller_avatar": u['avatar'],
            "tag": [],
            "review": '0', # 0: 刚发布未审核, 1: 审核通过, 2: 不通过, 3: 被举报
            "status": '0', # 0: 上架(默认), 1: 下架, 2: 归档（所有用户不可见）
            "is_new": is_new,
            'is_global': '0',
            "last_update_at": int(time.time()),
            "create_at": int(time.time())
        })

        #  发布到趣淘圈
        self.db.QtZone.insert({
            'type': 0, # 0 发布，1 评论，2 求购
            'goods_id': goods_id,
            'user_id': self.user_id,
            'time': int(time.time()),
            'buy_msg': '',
            "lng_lat": lng_lat,
            "geohash": _geohash,
        })
        self.write_json({"errno": 0, "msg": "success"})


@route('/api/selling/edit')
class SellingEdit(BaseHandler):
    #编辑商品
    @auth_decorator
    def get(self):
        #检查用户是否可以发布商品。被举报的用户不能发布商品
        self.write_json({"errno": 0, "msg": "success"})

    @auth_decorator
    #@gen.coroutine
    def post(self):
        # 默认使用用户的位置，可以选择实时位置
        goods_id = self.get_argument("id", '')
        goods_name = self.get_argument("title")
        goods_type = self.get_argument("goods_type")
        introduce = self.get_argument("introduce")
        price = self.get_argument("price")
        is_new = self.get_argument("is_new", 0)

        u = self.db.User.find_one({"_id": ObjectId(self.user_id)})
        location = self.get_argument('location') or u['location']
        lng_lat = self.get_argument('lng_lat') or u['lng_lat']
        _geohash = generate_geohash(lng_lat)
        tag = self.get_argument("tag", '')
        file_count = int(self.get_argument('file_count', 0))
        images = self.get_argument('images', '').split(',')
        can_pay_online = self.get_argument('can_pay_online', "0")
        self.attach = []
        self.db.Goods.update({"_id": ObjectId(goods_id)},
                              {"$set":  {
                                "goods_name": goods_name,
                                "goods_type": goods_type,
                                "introduce": introduce,
                                "price": price,
                                "location": location,
                                "lat_lng": lng_lat,
                                "geohash": _geohash,
                                "images": images,
                                "can_pay_online": can_pay_online,
                                "seller_id": self.user_id,
                                "tag": [],
                                "review": '0', # 0 刚发布未审核， 1审核通过 2不通过 3被举报
                                "status": '0', # 0：上架(默认)，1:下架，2:归档（所有用户不可见）
                                "last_update_at": int(time.time()),
                                "is_new": is_new,
                                }
                              })
        # 清除缓存
        self.clear_cache("GoodsInfo:%s" % goods_id)

        self.write_json({"errno": 0, "msg": "success"})
