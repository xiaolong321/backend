#coding: utf-8
"""
七牛云存储类
七牛存储api
# 七牛请使用华东地区，华南地区会出错
"""
from qiniu import Auth, etag, put_file, put_data
import os
import uuid


ACCESS_KEY = 'Zt5y9AOFeTCFtX1HllY4bXkHRW08VHQP68SG8_HG'
SECRET_KEY = 'zoNb7G8gh9l3RYqVXeYedi8iqg9jQfZkVSSTvM6N'
BACKET_NAME = 'qutao'
DOMAIN = 'http://ohgdcjojy.bkt.clouddn.com/'


class Uploader(object):
    """七牛存、取图片类"""
    mime_type = "text/plain"
    q = Auth(ACCESS_KEY, SECRET_KEY)

    def save_file_to_qiniu(self, upload_file, path='attach', return_domain=True):
        """web上传文件"""
        ext = "." + upload_file.get('content_type').split('/')[1]
        key = str(uuid.uuid1()).replace('-', '')
        key = "%s/%s%s" % (path, key, ext)
        token = self.q.upload_token(BACKET_NAME, key, 3600)
        #ret, info = put_data(token, key, upload_file)
        ret, info = put_data(token, key, upload_file['body'])
        if not ret or ret.get('key',None) == None:
            raise Exception('upload error')
        else:
            if return_domain:
                return u"%s%s" % (DOMAIN, key)
            else:
                return key
       
    def get_attach_path(key):
        """根据key取图片"""
        url = "%s%s" % (DOMAIN, key)
        return u"%s%s" % (DOMAIN, key)

