#coding: utf-8
from bson import ObjectId
from apps.api.common import BaseHandler
from apps.api.utils import auth_decorator
from apps.models import User
from lib.routes import route
from lib.jpush import push_msg
import time


@route('/api/user/verify')
class ApiUserVerifyHandler(BaseHandler):
    '''用户实名验证'''
    @auth_decorator
    def get(self):
        data = self.db.User.find_one({"_id": ObjectId(self.user_id)}, {"verify_status": "1"})
        del data['_id']
        return self.write_success(data)

    @auth_decorator
    def post(self):
        # alipay 支付宝帐号
        data = self.get_args(['photo', 'fullname', 'phone', 'address', 'alipay'])
        query = {"_id": ObjectId(self.user_id)}
        data.status = "0"
        self.db.User.update(query, {'$set': {"verify_status": "1"}})
        # 清除用户缓存信息
        self.clear_cache("UserInfo:%s" % self.user_id)
        self.db.User_verify.update(query, {"$set": data}, True)
        push_msg(self.user_id, u"您的身份验证已提交，正在审核中")
        self.write_success()


@route('/api/user/account')
class ApiUserAccountHandler(BaseHandler):
    '''查看我的账户'''
    # db User_account
    # db.type  提现: 0, 买入: 1, 卖出: 2

    @auth_decorator
    def get(self):
        last_count = int(self.get_argument('last_count', 0)) #上次加载到第几条
        items_origin = self.db_find_all('User_account', {"user_id": self.user_id, "type": {'$ne': 1}}, ("time", last_count), keepid=True)
        # balance = 0 # 账户余额
        balance = round(User.byid(self, self.user_id, ('balance',)).balance, 2) # 账户余额
        items = []
        for item in items_origin:
            if item['type'] > 0:
                # 根据订单取出商品信息
                order = self.db.Order.find_one({'_id': ObjectId(item['order_id'])})
                if order['status'] != "2":
                    # 只有完成的订单才显示
                    continue

                goods = self.db.Goods.find_one({'_id': ObjectId(order['goods_id'])})
                goods['_id'] = str(goods['_id'])
                item['goods'] = goods

                # 取出用户信息
                hiskey = 'custom_id' if item['type'] == 2 else 'seller_id'
                user = self.db.User.find_one({"_id": ObjectId(order[hiskey])})
                item['user'] = {'nickname': user['nickname'], 'avatar': user['avatar']}

                # 计算余额
                # if item['type'] == 2:
                #     balance += float(goods['price'])
                del item['order_id']
            # else:
            #     balance -= float(item['money'])
            del item['_id']
            del item['user_id']
            items.append(item)
        self.write_success({'balance': balance, 'items': items})

    @staticmethod
    def addItem(self, type, **kwargs):
        '''交易成功、提现时会调用'''
        # param type  提现: 0, 交易: 1
        # kwargs 'order_num', 'money'

        # 要插入UserAccount的数据字典
        now = int(time.time())
        if type > 0:
            # 若为交易
            # 先取出订单对象看自己是买家还是卖家
            order_num = kwargs['order_num']
            order = self.db.Order.find_one({'order_num': order_num})
            if not order:
                return False
            # 生成我的账户记录
            if self.db.User_account.find({"order_id": str(order['_id'])}).count():
                return
            data = {"order_id": str(order['_id']), "time": now}
            data2 = {"order_id": str(order['_id']), "time": now}
            data['user_id'] = order['custom_id']
            data['type'] = 1
            self.db.User_account.insert(data)
            data2['user_id'] = order['seller_id']
            data2['type'] = 2
            self.db.User_account.insert(data2)
            # 商品下架
            self.db.Goods.update({"_id": ObjectId(order['goods_id'])}, {"$set": {'status': '1'}})
            # 清除缓存
            self.clear_cache("GoodsInfo:%s" % order['goods_id'])
            # 推送消息
            goods_name = order['goods_info']['goods_name']
            push_msg(order['seller_id'], u'请尽快联系买家完成交易并让TA确认收货', u'趣淘上的商品被购买')
            # push_msg(order['custom_id'], u'成功支付购买%s，请联系卖家完成交易 ' % goods_name)
        else:
            data = {"user_id": self.user_id, "money": float(kwargs['money']), "type": type, "time": now}
            return self.db.User_account.insert(data)


@route('/api/user/withdraw')
class ApiWithdrawHandler(BaseHandler):
    """提现"""
    @auth_decorator
    def post(self):
        # status 0: 待审核, 1: 已审核
        money = round(float(self.get_argument("money")), 2)
        # 同步我的账户
        account_id = ApiUserAccountHandler.addItem(self, 0, money=money)
        # 同步用户余额
        self.db.User.update({"_id": ObjectId(self.user_id)}, {'$inc': {'balance': -money}})
        # 清除缓存
        self.clear_cache("UserInfo:%s" % self.user_id)

        self.db.Withdraw.insert({
            "user_id": self.user_id,
            "account_id": str(account_id),
            "money": money,
            "time": int(time.time()),
            "status": '0'})
        return self.write_success()


@route('/api/user/ userinfo')
class GetUserInfo(BaseHandler):
    @auth_decorator
    def get(self):
        user_id = self.get_argument('user_id')
        return self.write_json({'errno': 0, 'msg': 'success', 'data': self.get_cache_user_info(user_id)})
