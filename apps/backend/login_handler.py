#!/usr/bin/env python
# coding:utf-8

from apps.api.common import BaseHandler
from lib.routes import route
import settings
import sys

if sys.version_info.major == 3:
    import urllib.parse as parse
else:
    import urllib as parse

def login():
    def wrap(view_func):
        def is_login(self, *args, **kwargs):
            self.me = self.get_secure_cookie("user_name")
            if self.request.method == "GET" and not self.me:
                url = "/login"
                if self.request.uri.count("next") > 3:
                    return self.redirect(url)
                if "?" not in url:
                    url += "?" + parse.urlencode(dict(next=self.request.uri))
                return self.redirect(url)
            return view_func(self, *args, **kwargs)
        return is_login
    return wrap


@route('/login')
@route('/manager')
class BacksLoginHandler(BaseHandler):
    def get(self):
        if self.get_cookie('user_name'):
            return self.redirect('/manager/index/')

        return self.render("login.html")

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        _next = self.get_argument('next', '')   
        if username in settings.REVIEW_ADMIN and password in settings.REVIEW_PASSWOED:
            self.set_secure_cookie("user_name", username, expires_days=1)
            if _next:
                return self.redirect(_next)
            return self.redirect('/manager/index/')
        else:
            return self.redirect('/login')

@route('/login_out')
class LoginOutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('user_name')
        return self.redirect('/login')
