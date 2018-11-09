#encoding: utf8

from apps.api.common import BaseHandler
from settings import PAGE_LIMIT
from lib.type import DictsRef

class ManagerHandler(BaseHandler):
    def render_db_data(self, tpl, db, query = None, join = None, keepid = True, paged=True, **extdata):
        '''
        用db中的数据渲染tpl指定的模板文件
        join  处理join操作
        paged 是否分页
        '''

        def _id_to_str(item):
            item['_id'] = str(item['_id'])
        def _id_pop(item):
            item.pop('_id')

        fn = _id_to_str if keepid else _id_pop
        cursor = self.db[db].find(query)

        if paged:
            num = cursor.count()
            page = int(self.get_argument("page", 1))
            page = 1 if page <=1 else page
            if page <=1:
                cursor.sort("_id", -1).limit(PAGE_LIMIT)
            else:
                cursor.sort("_id", -1).skip((page-1) * PAGE_LIMIT).limit(PAGE_LIMIT)

        data = list(cursor)

        if join:
            targets = self.db_join_data(data, **join)
            for item in data:
                target = targets[item[join['key']]]
                target.pop('_id', None)
                item.update(target)

        for item in data:
            fn(item)

        self.render(tpl,
            data       = DictsRef(data),
            pagination = self.pagination(num, page),
            **extdata)