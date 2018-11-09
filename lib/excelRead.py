# -*- coding: utf-8 -*-
"""读取excel文件"""
import xlrd
import sys
import re
reload(sys)
sys.setdefaultencoding('utf-8')


def open_excel(filepath):
    data = xlrd.open_workbook(filepath)
    return data

def excel_table_byindex(filepath, colnameindex=0, by_index=0):
    data = open_excel(filepath)
    table = data.sheets()[by_index]
    #table = data.sheets()[]
    nrows = table.nrows #行数
    ncols = table.ncols #列数

    colnames = table.row_values(colnameindex) #某一行数据
    list = []
    #try:
    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        if row:
            app = {}
            for i in range(len(colnames)):
                app[colnames[i]] = row[i]
                #app[colnames[i]] = re.sub(r'[.\n]+', '', row[i])  #  去除换行
            list.append(app)
    #except IOError, e:
    #    print e
    return list[colnameindex:] #第一行的数据为列名称

def main(filepath):
    table = excel_table_byindex(filepath)
    return table

if __name__ =="__main__":
    print "ok"

