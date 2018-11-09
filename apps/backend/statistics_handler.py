#coding:utf-8
from apps.api.common import BaseHandler
from lib.routes import route
from login_handler import login
from settings import PAGE_LIMIT


@route('/manager/statistics/users/')
class StatisticsUsersHandler(BaseHandler):
	#活跃用户
    @login()
    def get(self):        
        self.write_json("statistics users")

@route('/manager/statistics/goods/')
class StatisticsGoodsHandler(BaseHandler):
	#活跃商品
	@login()
	def get(self):
		self.write_json("statistics goods")