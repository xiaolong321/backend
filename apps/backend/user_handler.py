#coding:utf-8
from apps.api.common import BaseHandler
from . import ManagerHandler
from lib.routes import route
from lib.jpush import push_msg
from lib.type import DictRef
from login_handler import login
from settings import PAGE_LIMIT
from apps.api.utils import timestampTodate, generate_geohash, generate_access_token, get_service_fee
from bson import ObjectId
import time
import random


@route('/manager/users/(''|last_update)')
class UsersHandler(BaseHandler):
    #用户列表
    @login()
    def get(self, sort=''):
        search = self.get_argument('search', '')
        page = int(self.get_argument("page", 1))
        page = 1 if page <=1 else page
        sele = self.db.User.find({'nickname': {'$regex': search}})
        num = sele.count()
        if sort !='last_update':

            sele.sort("_id", -1).skip((page-1) * PAGE_LIMIT).limit(PAGE_LIMIT)
        else:
            
            sele.sort("last_update", -1).skip((page-1) * PAGE_LIMIT).limit(PAGE_LIMIT)
            
        data = []
        for i in sele:
            i["create_at"] = timestampTodate(i["create_at"])
            i["last_update"] = timestampTodate(i["last_update"])
            i["_id"] = str(i["_id"])
            i["selling_count"] = self.db.Goods.find({"seller_id": i["_id"]}).count()
            i["invite_count"] = self.db.Invitation.find({"inviter": i["_id"]}).count()
            i["sex"] = [u"未知",u"男",u"女"][int(i["sex"])]
            i["verify_status"] = [u"未认证",u"审核中",u"已认证"][int(i["verify_status"])]
            data.append(i)
        obj = {
            'data': data,
            'pagination': self.pagination(num, page),
        }
        self.render("users.html", **obj)
    
    @login()
    def post(self, sort=''):
        # 添加商品所属用户记录
        user_id = self.get_argument('user_id')
        if user_id:
            if not self.db.PushGoodsUser.find({'user_id': user_id}).count():
                self.db.PushGoodsUser.insert({'user_id': user_id})
            return self.write_json({'errno': 0, 'msg': 'success'})
        return self.write_json({'errno': 400, 'msg': 'invalid data'})


@route('/manager/new/users/')
class NewUsersHandler(BaseHandler):
    #最新用户
    @login()
    def get(self):
        search = self.get_argument('search', '')
        page = int(self.get_argument("page", 1))
        page = 1 if page <=1 else page
        sele = self.db.User.find({"create_at": {"$gte": int(time.time()) - 7*86400}}).sort('_id', -1)
        num = sele.count()
        if page <=1:
            sele = sele.limit(PAGE_LIMIT)
        else:
            sele = sele.skip((page-1) * PAGE_LIMIT).limit(PAGE_LIMIT)
        data = []
        for i in sele:
            i["create_at"] = timestampTodate(i["create_at"])
            i["_id"] = str(i["_id"])
            i["selling_count"] = self.db.Goods.find({"seilling_id": i["_id"]}).count()
            data.append(i)
        obj = {
            'data': data,
            'pagination': self.pagination(num, page),
        }
        self.render("new_users.html", **obj)

@route('/manager/review/users/')
class ReviewUsersHandler(BaseHandler):
    #用户审核。被举报的用户
    @login()
    def get(self):
        self.write_json('review users')

@route('/manager/user/info')
class UserInfoHandler(BaseHandler):
    '''用户信息'''
    @login()
    def get(self):
        _id = self.get_argument('id')
        _type = self.get_argument('type', 'goods')
        page = int(self.get_argument("page", 1))
        page = 1 if page <=1 else page

        me = DictRef(self.get_user_info(_id))
        me.create_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(me.create_at))
        me.verify_status = ["未认证","审核中","已认证"][int(me.verify_status)]
        invited_user = self.db.Invitation.find_one({"_id": ObjectId(_id)})
        if invited_user:
            me.invited_user = self.get_cache_user_info(invited_user['inviter'])

        me._id = _id
        if _type == 'goods':
            data = self.db.Goods.find({"seller_id": _id}).skip((page-1) * PAGE_LIMIT).limit(PAGE_LIMIT)
            num = data.count()
        else:
            invited_ids = self.db.Invitation.find({"inviter": _id}).skip((page-1) * PAGE_LIMIT).limit(PAGE_LIMIT)
            data = []
            for item in invited_ids:
                user_id = str(item["_id"])
                user = self.get_user_info(user_id, ('avatar', 'nickname'))
                user["selling_count"] = self.db.Goods.find({"seller_id": user_id}).count()
                user["invite_count"] = self.db.Invitation.find({"inviter": user_id}).count()
                user["_id"] = user_id
                data.append(user)
            num = len(data)
        self.render("user_info.html", me=me, data = data, type=_type, pagination = self.pagination(num, page))

@route('/manager/add/virtual/user')
class AddVirtualUserHandler(BaseHandler):
    '''虚拟用户'''
    @login()
    def get(self):
        num = int(self.get_argument('num'))
        community_list = [i['name'] for i in self.db.Goods_Community.find()]
        obj = {
            'title': u'新增虚拟用户',
            'community_list': community_list,
            'num': range(num+1)[1:]
        }
        self.render('add_user.html', **obj)

    @login()
    def post(self):
        kv = {k:''.join(v) for k,v in self.request.arguments.iteritems()}
        num = kv.pop('num')
        target = kv.pop('target')
        community = self.db.Goods_Community.find_one({'name': target})
        users = {}
        for k in kv:
            s = k.split('_')
            if not users.has_key(s[1]):
                users[s[1]] = {}
            users[s[1]][s[0]] = kv[k]


        for user in users:

            _t = int(time.time())
            _lng_lat = community['lng_lat']# TODO

            au = self.db.User.insert({
                "device_id": None,
                "phone": '13000000000',#TODO
                "nickname": users[user]['name'],
                "avatar": users[user]['avatar'],
                "location": u'详细地址',#TODO
                "sex": users[user]['sex'],
                "age": random.randint(16, 36),#TODO
                "email": 'test@quseit.cn',#TODO
                "lng_lat": _lng_lat,
                "geohash": generate_geohash(_lng_lat),
                "ftag": [],
                "level": 0,
                "create_at": _t,
                "last_update": _t
            })
            user_id = str(au)

            self.user_id = user_id
            # 记录用户微信openid
            self.db.Wechat_extend.insert({"user_id": user_id,
                                          "openid": 'adsfadsfasdfadfasf'})#TODO

            #User_extend 用户拓展表，存放用户环信信息
            _token = generate_access_token(user_id)
            self.db.User_extend.insert({
               "user_id": user_id,
                "hx_username": 'test',#TODO
                "hx_password": 'test'
            })#TODO

        self.write_json(users)


@route('/manager/user/verify')
class UsersVerifyHandler(ManagerHandler):
    """用户实名认证"""
    @login()
    def get(self):
        status = self.get_argument('status', '0')
        query = {'status': status}
        self.render_db_data('user_verify.html', 
            'User_verify', query, join={'db':'User', 'key':'_id', 'select':('nickname', 'avatar', 'verify_status')}, **query)

    @login()
    def post(self):
        user_id = self.get_argument('user_id')
        action  = self.get_argument('action')
        query = {'_id': ObjectId(user_id)}
        if action == "0":
            self.db.User.update(query, {'$set': {'verify_status': "0"}})
            push_msg(user_id, u"您的身份验证未通过，信息不符合要求", extra="extra_mine")
        else:
            info = self.db.User_verify.find_one(query)
            self.db.User.update(query, {'$set': {'verify_status': "2", 'phone': info['phone'], 'alipay': info['alipay']}})
            self.db.User_verify.update(query, {'$set': {'status': "1"}})
            push_msg(user_id, u"您的身份验证已通过", extra="extra_mine")
        # self.db.User_verify.remove(query)
        return self.write_success()

@route('/manager/user/withdraw')
class WithdrawHandler(ManagerHandler):
    """提现审核"""
    @login()
    def get(self):
        self.render_db_data('user_withdraw.html', 
            'Withdraw', {'status':'0'}, {'db':'User', 'key':'user_id', 'tkey':'_id'}, 
            fee = get_service_fee, after_fee = lambda x: x - get_service_fee(x))

    @login()
    def post(self):
        withdraw_id = self.get_argument('id')
        query = {'_id': ObjectId(withdraw_id)}
        action = self.get_argument('action')
        if action == "1":
            info = self.db.Withdraw.find_one(query)
            self.db.Withdraw.update(query, {'$set': {'status': "2"}})
            money = info['money']

            push_msg(info['user_id'], u"您申请的%d元提现已成功，手续费为%s元" % (money, get_service_fee(money)))
        else:
            pass
        return self.write_success()
