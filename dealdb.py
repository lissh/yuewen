# -*- coding: utf-8 -*-
__author__ = 'lish'
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding('utf-8')



class handleDB(object):
    def __init__(self,host,port,user,passwd,db):
        self.conn=MySQLdb.connect(host=host,port=port,user=user,passwd=passwd,db=db,charset="utf8")
        self.cursor = self.conn.cursor()

    def insertdb(self,sql,datalist=[]):
        if datalist!=[]:
            n = self.cursor.executemany(sql,datalist)
        else:
            n = self.cursor.execute(sql)
        self.conn.commit()

    def updatedb(self,sql):
        self.cursor.execute(sql)
        self.conn.commit()

    def selectdb(self,sql):
        keydatalist=[]
        self.cursor.execute(sql)
        for row in self.cursor.fetchall():
            keydatalist+=[row]
        return keydatalist

    def truncatedb(self,sql):
        self.cursor.execute(sql)
        self.conn.commit()



if __name__ == '__main__':
    print '??'
    handleDB('101.200.88.69',3307,'ebook','Ebook#swcnHk3','ebook_con')
    print '???'


