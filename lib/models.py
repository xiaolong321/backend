#coding:utf-8
import time
import settings
from mongoengine import *
import settings
import sys

try:
    pass
    #connect(settings.DATABASE_NAME)
    #connect('blog', host='192.168.3.1', username='root', password='1234')

except ConnectionError as e:
    print(e)
    sys.exit()

class Users(Document):
    username = StringField(max_length=128, required=True)
    password = StringField(max_length=128, required=True)
    email = StringField(max_length=64, required=True)
    headImgUrl = StringField(max_length=256)
    sex = IntField(default=0)
    locale = StringField(max_length=64)
    age =  StringField(max_length=16)
    create_at = IntField(default=int(time.time()))

class MyApp(Document):
    title = StringField(max_length=64, required=True)
    code = StringField(max_length=64, required=True)
    logo = StringField()
    describe = StringField(max_length=256)
    ext = StringField(max_length=32)
    user = ReferenceField(Users)

class MyMarket(Document):
    title = StringField(max_length=64)
    description = StringField(max_length=255)
    prefix = StringField(max_length=255)

class MyVersion(Document):
    app = ReferenceField(MyApp)
    market = StringField(max_length=64)
    pub_date = IntField(default=int(time.time()))
    ver_name = StringField(max_length=16)
    ver_code = StringField(max_length=16)
    ver_desc = StringField()

class MyDefaultConf(Document):
    app = ReferenceField(MyApp)
    key = StringField(max_length=64)
    val = StringField(max_length=256)
    is_ext = BooleanField()

class MyConf(Document):
    ver = ReferenceField(MyVersion)
    key = StringField(max_length=64)
    val = StringField(max_length=256)
    is_ext = BooleanField()

class AppConfigure(Document):
    key = StringField(max_length=64)
    val = StringField(max_length=256)

class Lang(Document):
    lang = StringField(max_length=64)

class Mobile(Document):
    brand = StringField(max_length=64)
    model = StringField(max_length=128)
    unique_id = StringField(max_length=128)

class Daily_data(Document):
    app = ReferenceField(MyApp)
    dau = IntField()
    den = IntField()
    dnu = IntField()
    ver_code = IntField()
    is_overview = BooleanField(default=False)
    create_at = IntField(default=int(time.time()))

class AdType(Document):
    title = StringField(max_length=128)

class AdMan(Document):
    app = ReferenceField(MyApp)
    title = StringField(max_length=128)

class AdMaster(Document):
    title = StringField(max_length=128)
    app_code = StringField(max_length=64)
    logo = StringField(max_length=128)
    ad_log = StringField(max_length=128)
    ad_log2 = StringField(max_length=128)
    ad_log3 = StringField(max_length=128)

class MyAdPlan(Document):
    ad_master = ReferenceField(AdMaster)
    ad_link = StringField(max_length=512)

class AdDefault(Document):
    ad_type = ReferenceField(AdType)
    ad_master = ReferenceField(AdMaster)
    ad_point = StringField()

class MyLog(Document):
    mobile = ReferenceField(Mobile)
    lang = ReferenceField(Lang)
    ver_app = ReferenceField(MyVersion)
    count = IntField()
    info = StringField(required=True)
    is_solved = BooleanField()

class AppItem(Document):
    idt = StringField(required=True)
    param = StringField(required=True)
    is_ext = BooleanField(default=False)

class AppLog(Document):
    ver_app = ReferenceField(MyVersion)
    lang = ReferenceField(Lang)
    item = ReferenceField(AppItem)
    count = IntField()
    last_up_at = IntField(int(time.time()))

class QPyApp(Document):
    title = StringField(required=True, max_length=64)
    code = StringField(max_length=64)
    ext = StringField(max_length=32)