#coding: utf-8
from time import time
from hashlib import md5
from bson import ObjectId
import tornado.web
from apps.api.common import BaseHandler
from lib.routes import route
from apps.api.utils import auth_decorator, generate_geohash
from apps.models import User

@route('/api/userinfo')
class ApiUserHandler(BaseHandler):
    """用户信息"""
    @auth_decorator
    def get(self):
        d = self.get_user_info(self.user_id)
        if d:
            d["_id"] = str(d["_id"])
            self.write_success(d)
        else:
            self.write_err('用户不存在')

    @auth_decorator
    def post(self):
        nickname = self.get_argument('nickname', '').strip()
        avatar = self.get_argument('avatar', '')
        sex = self.get_argument('sex', '')

        _nickname = _avatar = _sex = ''
        if nickname:
            _nickname = nickname
        if avatar:
            _avatar = avatar
        if sex:
            _sex = sex
        self.db.User.update({"_id": ObjectId(self.user_id)}, {"$set": {
            "nickname": _nickname, 
            "avatar": _avatar,
            "sex": _sex
        }})
        # 清除缓存
        self.clear_cache("UserInfo:%s" % self.user_id)

        return self.write_json({"errno": 0, "msg": "success", "data": {
            "nickname": _nickname,
            "avatar": _avatar,
            "sex": _sex
        }})

@route('/api/user/chatwith')
class ApiUserChatWith(BaseHandler):
    """最近聊天"""
    @auth_decorator
    def post(self):
        partner = self.get_argument('partner')
        _self = self.db.User.find_one({'user_id': ObjectId(self.user_id)})
        chatwith = _self['chatwith'][:19] + [partner] if hasattr(_self, 'chatwith') else [partner]
        self.db.User.update({"_id": ObjectId(self.user_id)}, {"$set": {"chatwith": chatwith}})
        _partner = self.db.User.find_one({'user_id': ObjectId(partner)})
        chatwith = _partner['chatwith'][:19] + [self.user_id] if hasattr(_partner, 'chatwith') else [self.user_id]
        self.db.User.update({"_id": ObjectId(partner)}, {"$set": {"chatwith": chatwith}})
        # 清除缓存
        self.clear_cache("UserInfo:%s" % self.user_id)

        return  self.write_json({"errno": 0, "msg": "success"})

    @auth_decorator
    def get(self):
        _self = self.db.User.find_one({'user_id': ObjectId(self.user_id)})
        chatwith = _self['chatwith'] if hasattr(_self, 'chatwith') else []
        #for user in chatwith:


@route('/api/seller/info')
class ApiUserInfoHandler(BaseHandler):
    '''查看卖家档案'''
    @auth_decorator
    def get(self):
        pass

@route('/api/hx_user')
class ApiHxUserHandler(BaseHandler):
    """使用环信名获取用户信息"""
    def get(self):
        hx_name = self.get_argument('hx_name')
        hx_info = self.db.User_extend.find_one({'hx_username': hx_name})
        if hx_info:
            user = User.byid(self, hx_info['user_id'], ('avatar', 'nickname'))
            user.strid()
            self.write_success(user._data)
        else:
            self.write_err('hx_name not found')

@route('/api/hx_name')
class ApiHxNmaeHandler(BaseHandler):
    """使用userid获取环信名"""
    def get(self):
        userid = self.get_argument('userid')
        hx_info = self.db.User_extend.find_one({'user_id': userid})
        self.write_success(hx_info['hx_username'])
