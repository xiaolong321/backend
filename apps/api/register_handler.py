#coding:utf-8
import time
from hashlib import md5
from apps.api.common import BaseHandler
from lib.routes import route
from apps.api.utils import generate_access_token, validate_email


__author__ = 'Anlim'
@route('/api/register')
class ApiRegisterHandler(BaseHandler):
    #api 用户名+密码注册
    def post(self):
        username = self.get_argument('username', '')
        password = self.get_argument('password', '')
        nickname = self.get_argument('nickname', '')

        if validate_email(username) and password and nickname:
            user = self.db.User.find_one({'username': username})
            if user:
                return self.write_json({'errno': 400, 'msg': 'username is existed'})

            # 创建用户
            _t = int(time.time())

            user_id = self.db.User.insert({
                'username': username,
                'password': generate_access_token(password),
                'nickname': nickname,
                "phone": '',
                "avatar": '',
                "location": '',
                "sex": '0',
                "age": '',
                "email": username,
                "lng_lat": '',
                "geohash": '', 
                "ftag": [],
                "level": 0,
                "create_at": _t,
                "last_update": _t,
                "verify_status": "0",
                "balance": 0,
            })
            #注册环信
            uid = int(time.time())
            _hx_username = "wx%s%s" % (uid, 'qt1')
            _hx_password = md5(_hx_username).hexdigest()[:10]
            self.huanxin.register_new_user(_hx_username, _hx_password, nickname)
            self.db.User_extend.insert({
                "user_id": str(user_id),
                "hx_username": _hx_username,
                "hx_password": _hx_password
            })
            return self.write_json({'errno': 0, 'msg': 'success'})
        return self.write_json({'errno': 400, 'msg': 'invalid post data'})

