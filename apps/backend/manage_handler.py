#coding:utf-8
from apps.api.common import BaseHandler
from lib.routes import route
from login_handler import login
from settings import PAGE_LIMIT
from apps.api.utils import timestampTodate, get_attach


@route('/manager/virtual/users/')
class VirtualUserHandler(BaseHandler):
    """虚拟用户管理"""
    @login()
    def get(self):
        self.write_json('virtual users manage')


@route('/manager/virtual/goods/')
class VirtualGoodsHandler(BaseHandler):
    """虚拟商品"""
    @login()
    def get(self):
        #导入
        self.write_json("virtual goods")

    @login()
    def delete(self):
        #删除
        goods = self.argument("goods_id") #集合[]
        return self.write_json({"errno": 0, "msg": "success"})

@route('/manager/message/')
class MessageHandler(BaseHandler):
    """消息管理（与用户对话）"""
    @login()
    def get(self):
        #获取消息列表
        data = []
        obj = dict(data=data)
        return self.render('message.html', **obj)
    
    @login()
    def put(self):
        #发送消息
        receive_id = self.get_argument("receive")
        msg = self.get_argument("msg")
        
        return self.write_json({"errno": 0, "msg": "success"})
