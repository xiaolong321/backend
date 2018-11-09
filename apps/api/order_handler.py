#coding: utf-8
from bson import ObjectId
from apps.api.common import BaseHandler
from apps.api.utils import auth_decorator
from lib.routes import route
from lib import alipay
from lib.jpush import push_msg
from user_handler import ApiUserAccountHandler
from apps.models import Goods, User
import random, time
import settings


PARTNER = "2088712656208494"
SELLER = "quseitlab@gmail.com"
RSA_PRIVATE = """MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAN8rgdZnnrWpKd3UOD2nMejb/mrn5nbs/2wiJf4lgAfWh1qwHDbug35k0O/4ekeP8qiRl53H4CcyAVuMfG+bQ2GOzS5MO7hmjqyeFKhA+SfTXpbndDPeHI51EpI5O/zcSPf8ZlE3pKqg9pcSurPn3aLD2GVDsR+PaIdrmZx1LlZxAgMBAAECgYAwV0hEnSVvzDjZaELWeAUDn8O4fIsbb7LURYFdT9ov2HRxXHyAGaI6GrR3hqdWIQQ7J25kKwuO8fIBVqkNs+AgNgGskroUYC4Lw/QWaQX6szbfz5x5OXDfz5ntgTVCy0f0KNDyjsXA7WiAat/sVQNEIS8ffb3tJ+8m6o+St5ErUQJBAP5zJ4DpfwEUurnB6+xkExLn4mPqQ8iMYShEWV3Se9DlEMJT5j3AtuG8KtvszKNcT6bpscUY9trlL5mk+EX3mS8CQQDgh5FtNkC2lRFgwVhVg1dhlJX07T/5Gt26j4TBrtLn2exDJAeU+IP0uaHkbBr4Vwi8XB1ewhaQ8ij5lXmRv+JfAkANsZbTqj1KipoN+zC+NRiNsOsPI4FoXp2v9BW3JefB80H2o1tFwYRWG7FWyqSsugATZIpLqC9I0oLASw+NfGjDAkA/Q7OkVB8T0xjcbF4ZajKa2iUOqDLYW8uSH5JGiJ4AmhTKLkK8pPF5aTzGgfdvdgaOHF5iLsnw+Wq2OHnSqYB9AkAKcrOYOY+j31zjiIRk7500rds9f6LVBjTF67Ee2c8xTIht727Mxa57FZaW6I17XVcSWH0uU0nfn7K9fHQlj9HN"""
RSA_PUBLIC = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCnxj/9qwVfgoUh/y2W89L6BkRAFljhNhgPdyPuBV64bfQNN1PjbCzkIM6qRdKBoLPXmKKMiFYnkd6rAoprih3/PrQEB/VsW8OoM8fxn67UDYuyBTqA23MML9q1+ilIZwBC2AQ2UBVOrFXfFl75p6/B5KsiNG9zpgmLCUYuLkxpLQIDAQAB"

@route('/api/sd24/signstr')
class ApiSd24(BaseHandler):

    def post(self):
        name = self.get_argument('name')
        price = self.get_argument('price')
        sign_str = alipay.moving_signed_order_str(RSA_PRIVATE, PARTNER, SELLER,
            'sd' + str(int(time.time())), name, "shandong 24 hours goods", price, "http://quseit.cn:10010/alipay/sd/notify")
        return self.write_success({"sign_str": sign_str})


@route('/api/seller/order')
class ApiUserOrder(BaseHandler):
    """查看我的订单"""
    @auth_decorator
    def get(self):
        # type 买入: 1, 卖出: 2
        last_count = int(self.get_argument('last_count', 0)) #上次加载到第几条
        type = int(self.get_argument('type'))
        mykey, hiskey = 'custom_id', 'seller_id'
        if type == 2:
            mykey, hiskey = hiskey, mykey
        #self.db.Order.remove({})
        orders = self.db_find_all('Order', {mykey: self.user_id, "status": {"$ne": "0"}}, ("time", last_count))
        data = []
        for order in orders:
            order['user_info'] = self.db.User.find_one({"_id": ObjectId(order[hiskey])})
            order['user_info']['hx_name'] = self.db.User_extend.find_one({"user_id": order[hiskey]})['hx_username']
            order['goods_info'] = self.get_cache_goods_info(order['goods_id'])
            del order['user_info']['_id']
            order['_id'] = str(order['_id'])
            data.append(order)
        return self.write_success(data)

    # 订单状态:  0: 未支付, 1: 待收货, 2: 已完成, 3 已取消
    @auth_decorator
    def post(self):
        """新建订单"""
        # data 要存入Order的数据字典
        # custom_msg买家留言
        data = self.get_args(['goods_id', 'quantity', 'receiver_name', 'receiver_phone', 'receiver_address', 'custom_msg'],
            {'quantity': (int, 1)})

        goods_info = Goods.byid(self, data.goods_id)
        if goods_info:
            data.order_num = str(int(time.time()))[2:] + str(random.randint(1000,9999))
            data.custom_id = self.user_id
            data.seller_id = goods_info.seller_id
            goods_info.import_seller_info()
            # 记录当前的商品信息
            del goods_info._id
            data.goods_info = goods_info._data
            data.time   = int(time.time())
            data.status = "0" # 订单状态

            self.db.Order.insert(data)
            sign_str = alipay.moving_signed_order_str(RSA_PRIVATE, PARTNER, SELLER,
                data.order_num, goods_info.goods_name, "qutao_pay", "0.01" if settings.DEV else goods_info.price, settings.HOST + "/alipay/notify")
            return self.write_success({"sign_str": sign_str})

        return self.write_err('no such goods')

@route('/api/seller/moreorderme')
class ApiMoreOrderGenerate(BaseHandler):
    """生成多商品订单"""
    @auth_decorator
    def post(self):
        # TODO goodsid type list
        data = self.get_args(['goods_id', 'quantity', 'receiver_name', 'receiver_phone', 'receiver_address', 'custom_msg'],
            {'quantity': (int, 1)})
        goods_id_list = data.goods_id.split(',')  # "id, id, id,"
        print goods_id_list, "g" * 10
        data.order_num = str(int(time.time()))[2:] + str(random.randint(1000,9999))
        for item in goods_id_list:
            if item:
                data.goods_id = item
                data.custom_id = self.user_id
                data.seller_id = self.get_cache_goods_info(item).get('seller_id') #goods_info.seller_id
                data.goods_info = self.get_cache_goods_info(item)
                data.time   = int(time.time())
                data.status = "0" # 订单状态
                if data.get('_id', ''):
                    del data['_id']
                print data, ">>>>>>>"

                self.db.Order.insert(data)
        sign_str = alipay.moving_signed_order_str(RSA_PRIVATE, PARTNER, SELLER,
            data.order_num, data.order_num, "qutao_pay", "0.01" if settings.DEV else goods_info.price, settings.HOST + "/alipay/notify")
        return self.write_success({"sign_str": sign_str})


@route('/api/order/cancel')
class ApiUserOrderCancel(BaseHandler):
    """取消订单"""
    @auth_decorator
    def post(self):
        data = self.get_args(['order_num', 'reason', 'other_reason'], {'reason': (int, -1)})
        if data.reason > -1:
            # 订单状态置为3(申请退款)，并写入取消理由
            order_query = {"order_num": data.order_num}
            self.db.Order.update(order_query, {"$set": {"status": "3", "reason": data.reason, "other_reason": data.other_reason}})
            # 推送消息
            seller_id = self.db.Order.find_one(order_query)['seller_id']
            push_msg(self.user_id, u"您取消订单申请提交成功，正在审核中")
            push_msg(seller_id, u"您有一笔订单被买家申请取消，请到我的订单查看", extra={"extra": "extra_my_order_buy", "order_num": data.order_num})
            return self.write_success()
        else:
            return self.write_err('miss arg reason')

@route('/api/order/confirm')
class ApiUserOrderConfirm(BaseHandler):
    """确认收货"""
    @auth_decorator
    def post(self):
        order_num = self.get_argument('order_num')
        # 订单状态置为2
        query = {"order_num": order_num}
        order = self.db.Order.find_one(query)
        self.db.Order.update(query, {"$set": {"status": "2"}})
        # 同步卖家余额
        money = float(order['goods_info']['price'])
        self.db.User.update({"_id": ObjectId(order['seller_id'])}, {'$inc': {'balance': money}})
        # 清除缓存
        self.clear_cache("UserInfo:%s" % order['seller_id'])
        # 推送消息
        goods_name = order['goods_info']['goods_name']
        push_msg(order['seller_id'], u'商品%s已确认收货，货款已到账' % goods_name, extra="extra_my_account")
        return self.write_success()


@route('/alipay/notify')
class ApiApayOutTradeHandler(BaseHandler):
    """支付宝回调"""
    def post(self):
        data = self.get_args(['trade_status', 'notify_id', 'out_trade_no', 'total_fee'])
        params = self.request.arguments
        params = {key: params[key][0] for key in params}
        # 验证签名，验证是否为支付宝发送的消息
        if alipay.moving_verify_sign(params, RSA_PUBLIC) and alipay.verify_aplipay(PARTNER, data.notify_id):
            # set_order_status = lambda status: self.db.Order.update({"order_num": data.out_trade_no}, {"$set": {"status": status}})
            if data.trade_status == 'TRADE_FINISHED' or data.trade_status == 'TRADE_SUCCESS':
                # 交易设为待收货
                ApiUserAccountHandler.addItem(self, 1, order_num=data.out_trade_no)
                # set_order_status("1")
                self.db.Order.update({"order_num": data.out_trade_no}, {"$set": {"status": "1"}})
            # elif data.trade_status == 'TRADE_CLOSED':
            #     # 关闭交易
            #     set_order_status("-1")
        self.write("success")
