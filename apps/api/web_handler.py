#encoding: utf8
from apps.api.common import BaseHandler
from bson import ObjectId
from lib.routes import route
from apps.models import Goods


@route('/download')
class DownloadHandler(BaseHandler):
    def get(self):
        self.render('web.html')
