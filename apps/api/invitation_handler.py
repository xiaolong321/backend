#coding: utf-8
from bson import ObjectId
from apps.api.common import BaseHandler
from apps.api.utils import auth_decorator
from apps.models import User
from lib.routes import route
from lib.jpush import push_msg
import time, base64

def gen_invite_code(user_id):
    """生成邀请码"""
    return user_id[-5:]

@route('/api/invitation')
class ApiInvitationHandler(BaseHandler):
    @auth_decorator
    def get(self):
        '''我的邀请码'''
        query = {"_id": ObjectId(self.user_id)}
        user = self.db.User.find_one(query, {"invitation_code": 1})
        code = user and user.get("invitation_code", None)
        if not code:
            code = gen_invite_code(self.user_id)
            self.db.User.update(query, {"$set": {"invitation_code": code}})
            # 清除缓存
            self.clear_cache("UserInfo:%s" % self.user_id)
        is_invited = self.db.Invitation.find_one(query) is not None
        return self.write_success({"mycode": code, "is_invited": is_invited})
    
    @auth_decorator
    def post(self):
        '''填写邀请码'''
        code = self.get_argument('code')
        query = {"_id": ObjectId(self.user_id)}
        # 用户只能填一次邀请码，_id就是user_id
        if not self.db.Invitation.find_one(query):
            inviter = self.db.User.find_one({"invitation_code": code}, {"_id": 1})
            if inviter:
                inviter_id = str(inviter["_id"])
                if inviter_id != self.user_id:
                    query["inviter"] = inviter_id
                    self.db.Invitation.insert(query)
                    push_msg(inviter_id, u"你已邀请了" + self.get_user_info(keys=('nickname',))['nickname'])
                    return self.write_success()
        return self.write_err()
