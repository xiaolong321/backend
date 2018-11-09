#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import platform
import os
import socket


DEV = True
HOST = "funtao.aipy.org:10010" if DEV else "http://funtao.quseit.cn:10010"
try:
    if socket.gethostname() == 'test.aipy.org':
        DEV = False
        HOST = 'http://funtao.aipy.org'
except Exception:
	DEV = False

ROOT = os.path.abspath(os.path.dirname(__file__))
PIC_PATH = os.path.join(ROOT, 'static/pic/')
TMP_PATH = os.path.join(ROOT, 'static/tmp/')
API_PORT = 10010

#server is in mataining ?
IS_MAINTAIN = False
IS_DEV = False

REVIEW_ADMIN = ['review_admin', 'anlim@quseit.com', 'river@quseit.com', 'wx@quseit.com', "wangzheng@quseit.com"]
REVIEW_PASSWOED = ['Quseit520']

#download link
iOS_download = 'https://itunes.apple.com/cn/app/qu-tao-yu-you-lin-jiao-yi/id1165752466'
Android_download = 'http://a.app.qq.com/o/simple.jsp?pkgname=com.quseit.letgo'


# app 首页轮播图类型
Advert_Type = {'activity': '活动', 'ads': '广告'}

LOGGING_LEVEL = logging.DEBUG
DEBUG = True

#db
DATABASE_NAME = "qutao"
DB_REPLICA_SET_HOST = "localhost"
DB_REPLICA_SET_PORT= 27017
DB_REPLICA_SET_NAME = "qprs0"

#redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_POOL = 0

#启动的app
APPS = ("api",
        "backend")

PAGE_LIMIT = 20

#商品图片地址
STATIC_DIR = os.path.join(HOST, 'static/pic/')

# 搜索距离范围(m)
DISTANCE = 1200
