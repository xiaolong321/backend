#coding:utf-8
from __future__ import print_function

from apps.api.common import BaseHandler
from lib.routes import route
from lib.qiniu_class import Uploader
from .login_handler import login
from settings import PAGE_LIMIT
from bson import ObjectId
from apps.api.utils import generate_geohash

add_goods_type = {
    'data': {}, # 数据集
    'title': u'商品类别',
    'input_list': [
        {
            'name': u'分类图片',
            'type': 'file',
            'alias': 'logo',
            'value': '',
        },
        
        {
            'name': u'分类名称',
            'type': 'text',
            'alias': 'name',
            'value': '',
        },
        {
            'name': u'分类拓展',
            'type': 'text',
            'alias': 'cat',
            'value': '',
        },
        {
            'name': u'优先级',
            'type': 'text',
            'alias': 'seq',
            'value': '',
        },{
            'name': u'分类图片2',
            'type': 'file',
            'alias': 'logo2',
            'value': '',
        },
    ],
}


add_goods_community = {
    'data': {}, # 数据集
    'title': u'商品小区',
    'input_list': [
        {
            'name': u'小区图片',
            'type': 'text',
            'alias': 'logo',
            'value': '',
        },
        {
            'name': u'小区名称',
            'type': 'text',
            'alias': 'name',
            'value': '',
        },
        {
            'name': u'经纬度',
            'type': 'text',
            'alias': 'lng_lat',
            'value': '',
        },
        {
            'name': u'描述',
            'type': 'text',
            'alias': 'desc',
            'value': '',
        },
        
    ],
}


@route('/manager/add')
class AddHandler(BaseHandler, Uploader):
    @login()
    def get(self):
        type = self.get_argument('type')
        if type == 'goods_type':
            add_goods_type['data'] = {}
            return self.render("add.html", **add_goods_type)

        elif type == 'goods_community':
            add_goods_community['data'] = {}
            return self.render("add.html", **add_goods_community)

    @login()
    def post(self):
        type = self.get_argument('type')
        if type == 'goods_type':
            #logo = self.get_argument('logo')
            logo = self.request.files.get('logo')
            if logo:
                logo = self.save_file_to_qiniu(logo[0])
    
            logo2 = self.request.files.get('logo2')
            if logo2:
                logo2 = self.save_file_to_qiniu(logo2[0])

            name = self.get_argument('name')
            cat = self.get_argument('cat')
            seq = self.get_argument('seq')
            seq = int(seq)
            self.db.Goods_Type.insert({
                'logo': logo,
                'logo2': logo2,
                'name': name,
                'cat': cat,
                'seq': seq
            })
            return self.redirect('/manager/goods/type/')
            #return self.write_success();
        elif type == 'goods_community':
            logo = self.get_argument('logo')
            name = self.get_argument('name')
            lng_lat = self.get_argument('lng_lat')
            desc = self.get_argument('desc')
            geohash = generate_geohash(lng_lat)
            self.db.Goods_Community.insert({
                'logo': logo,
                'num': '0',
                'name': name,
                'lng_lat': lng_lat,
                'desc': desc,
                'geohash': geohash
            })
            return self.redirect('/manager/goods/community/')
            #return self.write_success();

@route('/manager/modify')
class ModifyHandler(BaseHandler, Uploader):
    @login()
    def get(self):
        type = self.get_argument('type')
        if type == 'goods_type':
            id = self.get_argument('id')
            goods_type = self.db.Goods_Type.find_one({'_id':ObjectId(id)})
            add_goods_type['input_list'][0]['value'] = goods_type['logo']
            add_goods_type['input_list'][1]['value'] = goods_type['name']
            add_goods_type['input_list'][2]['value'] = goods_type['cat']
            add_goods_type['input_list'][3]['value'] = goods_type['seq']
            add_goods_type['data'] = goods_type
            return self.render("add.html", **add_goods_type)
        elif type == 'goods_community':
            id = self.get_argument('id')
            goods_community = self.db.Goods_Community.find_one({'_id':ObjectId(id)})
            add_goods_community['input_list'][0]['value'] = goods_community['logo']
            add_goods_community['input_list'][1]['value'] = goods_community['name']
            add_goods_community['input_list'][2]['value'] = goods_community['lng_lat']
            add_goods_community['input_list'][3]['value'] = goods_community['desc']
            return self.render("add.html", **add_goods_community)
        return self.render("add.html", **add_goods_type)

    @login()
    def post(self):
        type = self.get_argument('type')
        if type == 'goods_type':
            id = self.get_argument('id')
            #logo = self.get_argument('logo')
            name = self.get_argument('name')
            cat = self.get_argument('cat')
            seq = self.get_argument('seq')
            seq = int(seq)
            data = {
                'name': name,
                'cat': cat,
                'seq': seq
            }
            logo = self.request.files.get('logo')
            print(logo, ">>>>>>>>")
            if logo:
                logo = self.save_file_to_qiniu(logo[0])
                data['logo'] = logo

            logo2 = self.request.files.get('logo2')
            if logo2:
                logo2 = self.save_file_to_qiniu(logo2[0])
                data['logo2'] = logo2

            self.db.Goods_Type.update({"_id": ObjectId(id)}, {'$set': data})
            return self.redirect('/manager/goods/type/')
        if type == 'goods_community':
            id = self.get_argument('id')
            logo = self.get_argument('logo')
            name = self.get_argument('name')
            lng_lat = self.get_argument('lng_lat')
            desc = self.get_argument('desc')
            geohash = generate_geohash(lng_lat)
            self.db.Goods_Community.update({"_id": ObjectId(id)},
            {'$set':{
                'logo': logo,
                'name': name,
                'lng_lat': lng_lat,
                'desc': desc,
                'geohash': geohash
            }})
            # return self.redirect('/manager/goods/community/')
            return self.write_json({"errno": 0, "msg": "修改成功"});
        return self.redirect('/manager/goods/type/')
