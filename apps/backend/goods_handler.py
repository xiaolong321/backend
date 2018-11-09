#coding:utf-8
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


@route('/manager/goods/type/')
class GoodsTypeHandler(BaseHandler):
    #商品类别
    @login()
    def get(self):
        search = self.get_argument('search', '')
        page = int(self.get_argument("page", 1))
        page = 1 if page <=1 else page
        goods_type = self.db.Goods_Type.find({'name': {'$regex': search}}).sort('seq', -1)
        num = goods_type.count()
        if page <= 1:
            goods_type = goods_type.limit(PAGE_LIMIT)
        else:
            goods_type = goods_type.skip((page-1) * PAGE_LIMIT).limit(PAGE_LIMIT)
        obj = {
            'data': [i for i in goods_type],
            'pagination': self.pagination(num,page)
        }
        return self.render("goods_type.html", **obj)

@route('/manager/del/goodstype')
class DelGoodsType(BaseHandler):
    '''删除商品类别'''
    @login()
    def get(self):
        gid = self.get_argument('id', False)
        if gid:
            self.db.Goods_Type.remove({"_id": ObjectId(gid)})
            return self.redirect(self.request.headers.get("Referer"))
        return  self.write_json({"errno": 100, "msg": "error gid or status"})

@route('/manager/goods/community/')
class GoodsCommunityHandler(BaseHandler):
    """商品小区"""
    @login()
    def get(self):

        '''
        community_list = self.db.Goods_Community.find()
        for community in community_list:
            self.db.Goods_Community.update({
                '_id': ObjectId(community['_id'])
            },{
                '$set': {
                    'geohash': generate_geohash(community['lng_lat'])
                }
            })
        '''
        search = self.get_argument('search', '')
        page = int(self.get_argument("page", 1))
        page = 1 if page <=1 else page
        goods_community = self.db.Goods_Community.find({'name': {'$regex': search}})
        num = goods_community.count()
        if page <= 1:
            goods_community = goods_community.limit(PAGE_LIMIT)
        else:
            goods_community = goods_community.skip((page-1) * PAGE_LIMIT).limit(PAGE_LIMIT)
        obj = {
            'data': [i for i in goods_community],
            'pagination': self.pagination(num, page)
        }
        return self.render("goods_community.html", **obj)

@route('/manager/del/community')
class DelGoodsCommunity(BaseHandler):
    '''删除商品小区'''
    @login()
    def get(self):
        gid = self.get_argument('id', False)
        if gid:
            self.db.Goods_Community.remove({"_id": ObjectId(gid)})
            return self.redirect(self.request.headers.get("Referer"))
        return  self.write_json({"errno": 100, "msg": "error gid or status"})

REVIEW_TABS = [u'待审核', u'已通过', u'已拒绝']
@route('/manager/goods/review/')
class GoodsReviewHandler(BaseHandler):
    #商品审核
    @login()
    def get(self):
        search = self.get_argument('search', '')
        page = int(self.get_argument("page", 1))
        review = self.get_argument("review", None)
        page = 1 if page <=1 else page
        if review == "1" or review == "2":
            review_query = review
        else:
            # 未审核或被举报
            review = "0"
            review_query = {'$in': ['0', '3']}
        sele = self.db.Goods.find({
            '$or': [
                {'goods_name': {'$regex': search}},
                {'seller_id': self.get_user_id(search)}
             ],
             'review': review_query,
             'status': {'$ne': '2'}
             }).sort("_id", -1)
        num = sele.count()
        if page <= 1:
            sele = sele.limit(PAGE_LIMIT)
        else:
            sele = sele.skip((page-1) * PAGE_LIMIT).limit(PAGE_LIMIT)
        data = self.fix_goods(sele)

        # 缓存community map
        community = []
        for goods in data:
            community.append(filter_distance(self.db_find_all('Goods_Community', {'geohash': geohash_neighbors(goods['geohash'])}), goods['lng_lat'], DISTANCE))

        return self.render("review.html", 
            data       = data,
            community  = json.dumps(community),
            review     = review,
            tabs       = REVIEW_TABS,
            num        = num,
            pagination = self.pagination(num, page))

@route('/manager/goods/info/(\w{24})')
class GoodsInfo(BaseHandler):
    """商品详情"""
    @login()
    def get(self, goods_id):
        data = self.get_cache_goods_info(goods_id)
        data['create_at'] = timestampTodate(data['create_at'])
        data['user_info'] = self.get_cache_user_info(data['seller_id']) 
        #data = dict(data, **)
        comment_data = self.db.Goods_comment.find({'goods_id': goods_id}).sort('comment_time', -1)
        comment_list = []
        for item in comment_data:
            user_info = self.get_cache_user_info(item['user_id'])
            item = dict(item, **user_info)
            item['comment_time'] = timestampTodate(item['comment_time'])
            comment_list.append(item)
        data['comment_data'] = comment_list
        #return self.write_json({'errno': 0, 'msg': 'ok', 'data': data})
        obj = {
            'user_list': [dict(item, **self.get_cache_user_info(item['user_id'])) for item in self.db.PushGoodsUser.find()],
            'goods_type_list': self.db.Goods_Type.find(),
            'goods_community_list': self.db.Goods_Community.find(),
            'data': data
        }
        return self.render('goods-add.html', **obj)
    
    @login()
    def post(self, goods_id):
        user_info = self.get_cache_user_info(self.get_argument('user_id'))
        data = dict(
            goods_name = self.get_argument('goods_name'),
            goods_type = self.get_argument('goods_type'),
            price = self.get_argument('price'),
            seller_id = self.get_argument('user_id'),
            lng_lat = user_info.get('lng_lat'),
            status = '0',
            collect_count = 0,
            create_at = int(time.time()),
            last_update_at = int(time.time()),
            introduce = self.get_argument('introduce'),
            can_pay_online = self.get_argument('can_pay_online'),
            community = self.get_argument('community', ''),
            tag = [],
            geohash = user_info.get('geohash'),
            location = '',
            images = str_to_dict(self.get_argument('images')),
            review = '0',
            is_new = self.get_argument('is_new'),
            is_global = self.get_argument('is_global')
        )
        self.db.Goods.update({'_id': ObjectId(goods_id)}, {'$set': data})
        # 清楚缓存
        self.clear_cache("GoodsInfo:%s" % goods_id)
        
        return self.write_json({'errno': 0, 'msg': 'success', 'next_url': ''})


@route('/manager/map')
class GoodsMap(BaseHandler):
    def get(self):
        return self.render("map.html")

@route('/manager/check_goods')
class CheckGoodsHandler(BaseHandler):
    """定期检查商品，发布超过一天自动下架"""
    @login()
    def post(self):
        dead_day = 3
        now = time.time()
        deadline = 3600 * 24 * dead_day # 3天
        for goods in self.db.Goods.find({}, {'goods_name': 1, 'seller_id': 1, 'last_update_at': 1}):
            if now - goods['last_update_at'] > deadline:
                self.db.Goods.update({'_id': goods['_id']}, {'$set': {'status': '1'}})
                # 推送消息
                push_msg(goods['seller_id'], '您的商品%s发布超过%d，已自动下架' % (goods['goods_name'], dead_day))

@route('/multifile/upload')
class MultifileUpload(BaseHandler, Uploader):
    """图片上传到七牛"""
    def post(self):
        image = self.request.files.get('image')
        if image:
            #image = image[0]
            key = self.save_file_to_qiniu(image[0])
            return self.write_json({"errno": 0, "msg": 'success', 'key': key})
        return self.write_json({"errno": 100, "msg": 'invalid files', 'key': ''})

@route('/manager/goods/add')
class GoodsAdd(BaseHandler):
    """发布商品"""
    @login()
    def get(self):
        obj = {
            'user_list': [dict(item, **self.get_cache_user_info(item['user_id'])) for item in self.db.PushGoodsUser.find()],
            'goods_type_list': self.db.Goods_Type.find(),
            'goods_community_list': self.db.Goods_Community.find(),
            'data': {}
        }
        return self.render('goods-add.html', **obj)
    

    @login()
    def post(self):
        user_info = self.get_cache_user_info(self.get_argument('user_id'))
        data = dict(
            goods_name = self.get_argument('goods_name'),
            goods_type = self.get_argument('goods_type'),
            price = self.get_argument('price'),
            seller_id = self.get_argument('user_id'),
            lng_lat = user_info.get('lng_lat'),
            status = '0',
            collect_count = 0,
            create_at = int(time.time()),
            last_update_at = int(time.time()),
            introduce = self.get_argument('introduce'),
            can_pay_online = self.get_argument('can_pay_online'),
            community = self.get_argument('community', ''),
            tag = [],
            geohash = user_info.get('geohash'),
            location = '',
            images = str_to_dict(self.get_argument('images')),
            review = '0',
            is_new = self.get_argument('is_new'),
            is_global = self.get_argument('is_global')
        )
        self.db.Goods.insert(data)
        return self.write_json({'errno': 0, 'msg': 'success', 'next_url': '/manager/index/'})
        

@route('/manager/goods/import/')
class GoodsImport(BaseHandler):
    """商品批量导入"""
    @login()
    def post(self):
        file_metas = self.request.files.get('upload-excel')
        if file_metas:
            filepath = ''
            for meta in file_metas:
                filename=meta['filename']
                if not os.path.exists(TMP_PATH):
                    os.mkdir(TMP_PATH)
                filename = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '.' +filename.split(".")[1]
                filepath=os.path.join(TMP_PATH, filename)
                with open(filepath,'wb') as up:      #有些文件需要已二进制的形式存储，实际中可以更改
                    up.write(meta['body'])
            msg = ''
            index = 0
            for item in excel_table_byindex(filepath):
                index += 1
                a = lambda x: item.get(x, '')
                user_info = self.db.User.find_one({'nickname': a(u'用户昵称')})
                if user_info:
                    data = dict(
                        goods_name = a(u'商品名称'),
                        goods_type = a(u'分类'),
                        price = a(u'价格'),
                        seller_id = str(user_info.get('_id')),
                        lng_lat = user_info.get('lng_lat'),
                        status = '1', # 默认为下架状态
                        collect_count = 0,
                        create_at = int(time.time()),
                        last_update_at = int(time.time()),
                        introduce = a(u'详细描述'),
                        can_pay_online = '1' if a(u'是否需要在线支付') else '0',
                        community = a(u'所在小区名称'),
                        tag = [],
                        geohash = user_info.get('geohash'),
                        location = a(u'所在小区名称'),
                        images = [],
                        review = '0',
                        is_new = '1' if a(u'是否新品') =='是' else '0',
                        is_global = '1' if a(u'是否全局推送') =='是' else '0',
                        taobao_link = a(u'淘宝链接'),
                    )
                    self.db.Goods.insert(data)
                else:
                    msg += '第%s行，用户%s不存在\r\n' % (index, a(u'用户昵称'))
            if not msg:
                return self.write_json({'errno': 0, 'msg': 'success'})
            else:
                return self.write_json({'errno': 400, 'msg': msg})
        return self.write_json({'errno': 400, 'msg': 'invalid file'})
