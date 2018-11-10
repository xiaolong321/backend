#coding:utf-8
from apps.api.common import BaseHandler
from lib.routes import route
from .login_handler import login
from settings import PAGE_LIMIT


@route('/manager/virtual/users/')
class VirtualUsersHandler(BaseHandler):
	#虚拟用户
    @login()
    def get(self):        
        self.write_json("virtual users")

@route('/manager/add/goods/')
class AddGoodsHandler(BaseHandler):
	#添加商品
	@login()
	def get(self):
		self.write_json("add goods")

@route('/manager/dialogue/')
@login()
class DialogueHandler(BaseHandler):
	#虚拟对话
	def get(self):
		self.write_json("dialogue manager")

	def post(self):
		self.write_json("send massage to some user")