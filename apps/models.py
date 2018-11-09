#encoding: utf8
from bson import ObjectId
import time

class Model(object):
    __slots__ = ('_data', '_handler')
    def __init__(self, handler, data = None):
        self._handler = handler
        self.setdata(data)

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        if name is not '_id' and name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            self._data[name] = value

    def __delattr__(self, name):
        del self._data[name]

    def delid(self):
        del self._id

    def strid(self):
        self._id = self.idstr

    def setdata(self, data):
        self._data = data
        if data:
            self.onsetdata()

    def onsetdata(self):
        pass

    def __and__(self, keys):
        return {key: self.__getattr__(key) for key in keys}

    def __nonzero__(self):
        return self._data is not None

    __bool__ = __nonzero__

    @property
    def db(self):
        return self._handler.db

    @property
    def idstr(self):
        return str(self._id)

    @classmethod
    def getdb(cls, handler):
        return handler.db[cls.__name__]

    @classmethod
    def byid(cls, handler, id, select = None):
        """
        根据id查询
        :param select: 要过滤的字段
        """
        if select:
            select = {key: 1 for key in select}
        return cls(handler, cls.getdb(handler).find_one({"_id": ObjectId(id)}, select))

class Goods(Model):
    __slots__ = ('_seller',)

    def onsetdata(self):
        self._seller = None

    def import_seller_info(self):
        """导入卖家用户名和头像"""
        user = User.byid(self, self.seller_id, ('avatar', 'nickname'))
        self.seller_nickname = user.nickname
        self.seller_avatar = user.avatar

    def import_seller_info_plus(self):
        self.seller_avatar = self.seller.avatar
        self.seller_nickname = self.seller.nickname
        self.seller_hx_name = self.seller.hx_name

    @property
    def seller(self):
        if not self._seller:
            self._seller = User.byid(self._handler, self.seller_id)
        return self._seller

    @property
    def collected(self):
        result = self.db.Favorite.find({"user_id": self._handler.user_id, "goods_id": self.idstr}).count()
        if result > 0:
            result = 1
        return result

class User(Model):
    __slots__ = ('_hx_name',)
    @property
    def hx_name(self):
        if not self._hx_name:
            self._hx_name = self.db.User_extend.find_one({'user_id': self.idstr})['hx_username']
        return self._hx_name

class Goods_comment(Model):
    def onsetdata(self):
        user = User.byid(self._handler, self.user_id, ('nickname', 'avatar'))
        self.nick = user.nickname
        self.avatar = user.avatar
        self.comment_time_diff = int(time.time()) - self.comment_time
        del self.goods_id

class QtZone(Model):
    pass
