# -*- coding: utf-8 -*-
__author__ = 'lish'
import dealdb


ywdb=dealdb.handleDB('101.200.88.69',3307,'ebook','Ebook#swcnHk3','ebook_con')


###处理con_book表
select_sql='SELECT book_id FROM ebook_con.con_book'
results=

