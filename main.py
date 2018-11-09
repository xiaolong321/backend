#!/usr/bin/python
# -*- coding: utf-8 -*-

# pre path
import os
from tornado.log import access_log

import logging
import site
import os.path
import sys
import redis
#import motor
from tornado.options import parse_command_line
#import toredis
from apps.api.common import MaintainHandler
from lib.routes import route
from lib.db_class import MongoCon, HuanXin

ROOT = os.path.abspath(os.path.dirname(__file__))
path = lambda *a: os.path.join(ROOT, *a)
site.addsitedir(path('vendor'))

#tornado
import tornado.httpserver
import tornado.ioloop
import tornado.web

#app
import settings

class Application(tornado.web.Application):
    def __init__(self, database_name=None, ):
        #初始化路由
        if settings.IS_MAINTAIN:
            handlers = [(r"/.*", MaintainHandler)]
        else:
            handlers = route.get_routes()
        #全局redis连接池
        redis_pool = redis.ConnectionPool(host=settings.REDIS_HOST,
                                          port=settings.REDIS_PORT, db=settings.REDIS_POOL)
        self.redis = redis.Redis(connection_pool=redis_pool)
        # mongodb
        self.con = MongoCon.get_connection()
        #huanxin
        self.huanxin = HuanXin.get_huanxin()

        #应用程序设置
        app_settings = dict(
            debug = settings.DEBUG,
            autoescape = None,
            cookie_secret = "WERSDFASDFSF233423423#@$@#$@#$@#$#@$#@dsfsafd",
            gzip = True,
            template_path = os.path.join(ROOT, "templates"),
            static_path = os.path.join(ROOT, "static"))

        tornado.web.Application.__init__(self, handlers, **app_settings)

#导入所有的handler
#每个apps 的子项目都必须有一个handler.py
for app_name in settings.APPS:
    __import__('apps.%s' % app_name, globals(), locals(), ['handlers'], -1)


def main():
    parse_command_line()
    logging.getLogger().setLevel(settings.LOGGING_LEVEL)
    application = Application()
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    _port = settings.API_PORT if len(sys.argv) == 1 else int(sys.argv[1])
    logging.info("API server Starting on port %d" % _port)
    http_server.bind(_port)
    http_server.start()

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logging.info("exiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
