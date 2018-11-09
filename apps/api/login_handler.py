#coding:utf-8
import time
from hashlib import md5
from bson import ObjectId
import tornado.web
from apps.api.common import BaseHandler
from lib.routes import route
from apps.api.utils import generate_access_token, generate_geohash


@route('/api/login')
class ApiLoginHandler(BaseHandler):
    #api 第三方登录（微信）
    def get(self):
        self.write_json({"errno": 0, "msg": "success"})

    def post(self):
        _username = self.get_argument('nickname')
        _openid = self.get_argument('openid') # uid
        _avatar = self.get_argument('avatar', '') # Third party login user avatar
        _location = self.get_argument('location')
        _lng_lat = self.get_argument('lng_lat') #经纬度
        _device_id = self.get_argument("device_id", None)
        _sex = self.get_argument('sex', '')
        _ftag = self.get_argument('ftag', '')
        _level = 0

        if not _openid:
            return self.write_json({"errno": 500, "msg": "invalid user openid, please post user openid"})

        u = self.db.Wechat_extend.find_one({"openid": _openid})
        if u:
            # 已经登录过
            user_id = str(u["user_id"])
            self.db.User.update({"_id": ObjectId(user_id)},
                                {"$set": {"last_update": int(time.time()),
                                          "lng_lat": _lng_lat,
                                          "sex": _sex,
                                          "geohash": generate_geohash(_lng_lat),
                                          "avatar": _avatar}})
            # 清除缓存
            self.clear_cache("UserInfo:%s" % user_id)

            hx = self.db.User_extend.find_one({"user_id": user_id})
            #self.db.User_extend.remove({"user_id": user_id})
            _token = generate_access_token(user_id)
            #user = self.db.User.remove({"_id": ObjectId(user_id)})
            user = self.db.User.find_one({"_id": ObjectId(user_id)})

            return self.write_json({"errno": 0, "msg": "ok", "data": {
                "user_id": user_id,
                "hx_name": hx['hx_username'],
                "hx_pwd": hx['hx_password'],
                "nickname": user["nickname"],
                "avatar": user["avatar"],
                "location": user["location"],
                "sex": user["sex"],
                "age": user["age"],
                "ftag": user["ftag"],
                "geohash": generate_geohash(user["lng_lat"]),
                "level": user["level"],
                "token": _token,
                "verify_status": user["verify_status"], # 是否通过实名认证
            }})
        
        # 第一次登录
        _age = self.get_argument('age', '')
        _phone = self.get_argument('phone', '')
        _email = self.get_argument('email', '')
        _t = int(time.time())
        au = self.db.User.insert({
            "device_id": _device_id,
            "phone": _phone,
            "nickname": _username,
            "avatar": _avatar,
            "location": _location,
            "sex": _sex,
            "age": _age,
            "email": _email,
            "lng_lat": _lng_lat,
            "geohash": generate_geohash(_lng_lat),
            "ftag": [],
            "level": 0,
            "create_at": _t,
            "last_update": _t,
            "verify_status": "0",
            "balance": 0,
        })
        user_id = str(au)

        self.user_id = user_id
        # 记录用户微信openid
        self.db.Wechat_extend.insert({"user_id": user_id, "openid": _openid})

        #注册环信
        uid = int(time.time())
        _hx_username = "wx%s%s" % (uid, 'qt1')
        _hx_password = md5(_hx_username).hexdigest()[:10]
        self.huanxin.register_new_user(_hx_username, _hx_password, _username)
        #self.huanxin.delete_user(_hx_username)

        #User_extend 用户拓展表，存放用户环信信息
        _token = generate_access_token(user_id)
        self.db.User_extend.insert({
            "user_id": user_id,
            "hx_username": _hx_username,
            "hx_password": _hx_password
        })

        return self.write_json({"errno": 0, "msg": "ok", "data": {
            "user_id": user_id,
            "hx_name": _hx_username,
            "hx_pwd": _hx_password,
            "nickname": _username,
            "avatar": _avatar,
            "location": _location,
            "sex": _sex, # 1 男，2女
            "age": _age, #
            "ftag": _ftag,
            "geohash": generate_geohash(_lng_lat), #
            "level": _level, #等级
            "token": _token,
            "verify_status": "0",
        }})


@route('/api/user_login')
class ApiUserLogin(BaseHandler):
    """账号登录（用户名＋密码）"""
    def post(self):
        username = self.get_argument('username', '')
        password = self.get_argument('password', '')
        _lng_lat = self.get_argument('lng_lat', '') #经纬度
        
        print "%s.,>>>>>" % username
        if username and password:
            find_data = {
                'username': username,
                'password': generate_access_token(password)
            }
            user = self.db.User.find_one(find_data)
            if user:
                user['_id'] = str(user['_id'])
                user['avatar'] = user['avatar'] or 'http://ohgdcjojy.bkt.clouddn.com/default.png'
                user['token'] = generate_access_token(str(user['_id']))
                user_ext = self.db.User_extend.find_one({'user_id': user.get('_id')})
                user['hx_name'] = user_ext.get('hx_username')
                user['hx_pwd'] = user_ext.get('hx_password')
                
                # 更新头像, 设置默认图像
                self.db.User.update({'_id': ObjectId(user['_id'])}, {'$set': {'avatar': 'http://ohgdcjojy.bkt.clouddn.com/default.png'}})
                # 清除缓存
                self.clear_cache("UserInfo:%s" % user['_id'])

                return self.write_json({'errno': 0, 'msg': 'success', 'data': user})
        
        return self.write_json({'errno': 400, 'msg': 'invalid username or password'})

