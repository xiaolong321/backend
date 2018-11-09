#encoding: utf8
from apps.api.common import BaseHandler
from bson import ObjectId
from lib.routes import route
from apps.models import Goods


@route('/api/share')
class ShareHandler(BaseHandler):
    def get(self):
        goods_id = self.get_argument("id")
        data = Goods.byid(self, goods_id)
        data.import_seller_info()
        import time
        ltime = time.localtime(data.create_at)
        data.create_at = time.strftime("%Y-%m-%d", ltime)
        self.render('share.html', data=data)
