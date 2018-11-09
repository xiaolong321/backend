#encoding: utf8
from apps.api.common import BaseHandler
from . import ManagerHandler
from lib.routes import route
from lib.jpush import push_msg
from login_handler import login
from bson import ObjectId
from apps.api.utils import get_service_fee, timestampTodate
from settings import PAGE_LIMIT

@route('/manager/order/cancel')
class OrderCancelHander(ManagerHandler):
    """取消订单审核"""
    @login()
    def get(self):
        self.render_db_data('order_cancel.html', 
            'Order', {'status': "3"}, join={'db':'User', 'key':'custom_id', 'tkey':'_id', 'select':('nickname', 'avatar')})

    @login()
    def post(self):
        order_num = self.get_argument('order_num')
        action = self.get_argument('action')
        status = "-1" if action == "1" else "1"
        order_query = {"order_num": order_num}
        order = self.db.Order.find_one(order_query)
        self.db.Order.update(order_query, {"$set": {"status": status}})
        # service_fee = get_service_fee(order['goods_info']['price'])
        # 推送消息
        
        push_msg(order['custom_id'], u'您的取消订单申请通过，货款已打到支付宝账户', extra={"extra": "extra_my_order_buy", "order_num": order_num})
        push_msg(order['seller_id'], u'您有一笔订单已被取消，请到我的订单查看', extra={"extra": "extra_my_order_sell", "order_num": order_num})
        self.write_success()

@route('/manager/order/list')
class OrderListManager(BaseHandler):
    """订单列表"""
    # status: 订单状态:  0: 未支付, 1: 待收货, 2: 已完成, 3: 申请退款（审核中）, -1: 交易关闭（已取消）
    @login()
    def get(self):
        page = int(self.get_argument("page", 1))
        filter_data = self.db.Order.find().sort('_id', -1)
        num = filter_data.count()
        filter_data = filter_data.skip((page-1) * PAGE_LIMIT).limit(PAGE_LIMIT)
        data = []
        for item in filter_data:
            #item['goods_info'] = self.get_cache_user_info(item['goods_id'])
            #if item['goods_info']:
            item['time'] = timestampTodate(item['time']) if item.get('time') else ''
            if item.get('custom_id'):
                item['custom_info'] = self.get_cache_user_info(item['custom_id'])

            if item.get('seller_id'):
                item['seller_info'] = self.get_cache_user_info(item['seller_id'])
            order_status = {
                '0': '未支付',
                '1': '待收货',
                '2': '已完成',
                '3': '申请退款（审核中）',
                '-1': '交易关闭（已取消）'
            }
            item['status'] = order_status[str(item['status'])]
            data.append(item)

        obj = {
            'data': data,
            'pagination': self.pagination(num,page)
        }
        return self.render('order-list.html', **obj)

    def post(self):
        _id = self.get_argument('id')
        action = self.get_argument('action')
        if _id and action:
            if action == 'finish':
                self.db.Order.update({'_id': ObjectId(_id)}, {"$set": {'status': 2}})
                return self.write_json({'errno': 0, 'msg': 'success'})
            
            if action == 'cacel':
                self.db.Order.update({'_id': ObjectId(_id)}, {"$set": {'status': -1}})
                return self.write_json({'errno': 0, 'msg': 'success'})
        return self.write_json({'errno': 400, 'msg': 'invalid data'})
