from pymongo import MongoClient
from lib.huanxin import EMChatAsync
import settings


class MongoCon(object):
    __db = None
    __database = None

    @classmethod
    def get_connection(cls):
        if cls.__db is None:
            try:
                cls.__db = MongoClient(settings.DB_REPLICA_SET_HOST, settings.DB_REPLICA_SET_PORT) #MongoClient(','.join(settings.DB_REPLICA_SET))
            except Exception as e:
                print(e)
        return cls.__db

    @classmethod
    def get_database(cls):
        if cls.__database is None:
            cls.__database = MongoCon.get_connection()[settings.DATABASE_NAME]
        return cls.__database

class HuanXin(object):
    __huanxin = None

    @classmethod
    def get_huanxin(cls):
        if cls.__huanxin is None:
            cls.__huanxin = EMChatAsync()
        return cls.__huanxin
