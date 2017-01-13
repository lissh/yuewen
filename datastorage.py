# -*- coding: utf-8 -*-
__author__ = 'lish'
from multiprocessing.dummy import Pool as ThreadPool
import io
import dealdb
import analyticAPI


ywdb=dealdb.handleDB('101.200.88.69',3307,'ebook','Ebook#swcnHk3','ebook_con')
ywapicont=analyticAPI.YWJsonAPI()

# ###处理con_book表
# select_sql='SELECT book_id FROM ebook_con.con_book'
# results=ywdb.selectdb(select_sql)
# if results!=[]:
# 	isExistCbids= [int(result[0]) for result in results]
# else:
# 	isExistCbids=[]

# booklistcont=ywapicont.BookList()
# isAPICbids=[int(bookcont) for bookcont in booklistcont]
# isNewCbids=list(set(isAPICbids)-set(isExistCbids))[1:3]

# if isNewCbids!=[]:
# 	pool = ThreadPool(2)
# 	results = pool.map(ywapicont.BookInfo,isNewCbids)
# 	pool.close()
# 	pool.join()
# 	if results!=[]:
# 		key=results[0].keys()
# 		isNewbookinfolist=[tuple(bookinfo.values()) for bookinfo in results]
# 		sqlpara1=str(tuple(key)).replace('(','').replace(')','').replace("'","")
# 		sqlpara2='%s'+',%s'*(len(key)-1)
# 		insert_sql='INSERT INTO ebook_con.con_book (%s) VALUES(%s)'%(sqlpara1,sqlpara2)
# 		print insert_sql
# 		# ywdb.insertdb(insert_sql,isNewbookinfolist)

# for isNewCbid in isNewCbids:
# 	###处理章节列表

# 	select_sql='SELECT chap_id FROM ebook_con.con_book_chapinfo'
# 	results=ywdb.selectdb(select_sql)
# 	if results!=[]:
# 		isExistCcids= [int(result[0]) for result in results]
# 	else:
# 		isExistCcids=[]

# 	chapterlist=ywapicont.ChapterList(isNewCbid)
# 	isAPICcids=[chapter['chap_id'] for chapter in chapterlist]
# 	isNewCcids=list(set(isAPICcids)-set(isExistCcids))[1:3]
# 	if isNewCcids!=[]:
# 		pool = ThreadPool(2)
# 		results = pool.map(ywapicont.BookInfo,isNewCbids)
# 		pool.close()
# 		pool.join()


# 	print isAPICcids[2:3]



# ###处理con_mcp_class
# bcategorylist=ywapicont.BCategoryList()
# isAPIBcategorylist=[tuple(bcategory.values()) for bcategory in bcategorylist]

# key=bcategorylist[0].keys()
# sqlpara1=str(tuple(key)).replace('(','').replace(')','').replace("'","")
# select_sql='SELECT %s FROM ebook_con.con_mcp_class WHERE mcp_id=3'%sqlpara1
# results=ywdb.selectdb(select_sql)
# if results!=[]:
# 	isExistBcategorylist= [int(result[0]) for result in results]
# else:
# 	isExistBcategorylist=[]
# isNewBcategorylist=list(set(isAPIBcategorylist)-set(isExistBcategorylist))

# if isNewBcategorylist!=[]:
# 	sqlpara2='%s'+',%s'*(len(key)-1)
# 	insert_sql='INSERT INTO ebook_con.con_mcp_class (%s) VALUES(%s)'%(sqlpara1,sqlpara2)
# 	print insert_sql
# 	# ywdb.insertdb(insert_sql,isNewBcategorylist)

# ###处理con_book_vols
# volumelist=ywapicont.VolumeList()
# isAPIVolumelist=[tuple(volume.values()) for volume in volumelist]

# key=volumelist[0].keys()
# sqlpara1=str(tuple(key)).replace('(','').replace(')','').replace("'","")
# select_sql='SELECT %s FROM ebook_con.con_book_vols'%sqlpara1
# results=ywdb.selectdb(select_sql)
# if results!=[]:
# 	isExistVolumelist= [int(result[0]) for result in results]
# else:
# 	isExistVolumelist=[]
# isNewVolumelist=list(set(isAPIVolumelist)-set(isExistVolumelist))


def dealdb(tablename,tabledatalist):

	isAPIBTabledatalist=[tuple(tabledata.values()) for tabledata in tabledatalist]
	key=tabledatalist[0].keys()
	sqlpara1=str(tuple(key)).replace('(','').replace(',)','').replace("'","").replace(')','')
	select_sql='SELECT %s FROM ebook_con.%s '%(sqlpara1,tablename)

	results=ywdb.selectdb(select_sql)
	if results!=[]:
		isExistTabledatalist=[]
		for result in results:
			if isinstance(result,tuple):
				isExistTabledatalist=results
			else:
				isExistTabledatalist.apppend(int(result[0]))
	else:
		isExistTabledatalist=[]

	#根据在某表中作为唯一键的值，对数据过滤，避免抓取重复数据
	isNewTabledatalist=[]
	primarykey=['chap_id','book_id','vol_id']
	flogkeys=list(set(key)&set(primarykey))
	if flogkeys!=[]:
		if len(flogkeys)==1:
			flogkey=flogkeys[0]
			locationI=key.index(flogkey)
			# print isExistTabledatalist[0]
			flogvalues=[int(isExistTabledata[locationI]) for isExistTabledata in isExistTabledatalist]

			for isAPIBTabledata in isAPIBTabledatalist:
				if int(isAPIBTabledata[locationI]) not in flogvalues:
					isNewTabledatalist+=[isAPIBTabledata]

		else:
			flogvalues=[]
			for isExistTabledata in isExistTabledatalist:
				flogvalues+=[tuple(int(isExistTabledata[key.index(flogkey)]) for flogkey in flogkeys)]

			for isAPIBTabledata in isAPIBTabledatalist:
				if tuple(int(isAPIBTabledata[key.index(flogkey)]) for flogkey in flogkeys) not in flogvalues:
					isNewTabledatalist+=[isAPIBTabledata]
	else:
		isNewTabledatalist=list(set(isAPIBTabledatalist)-set(isExistTabledatalist))

	if isNewTabledatalist!=[]:
		sqlpara2='%s'+',%s'*(len(key)-1)
		insert_sql='INSERT INTO ebook_con.%s (%s) VALUES(%s)'%(tablename,sqlpara1,sqlpara2)
		isNewTabledatalist=list(set(isNewTabledatalist))
		# print insert_sql
		ywdb.insertdb(insert_sql,isNewTabledatalist)



def main():
		mcpid='3'
		#处理分类
		bcategorylist=ywapicont.BCategoryList(mcpid)
		dealdb('con_mcp_class',bcategorylist)
		#处理图书列表		
		cbids=ywapicont.BookList()
		mcbids=[(mcpid,cbid) for cbid in cbids]
		pool = ThreadPool(5)
		bookinfolist = pool.map(ywapicont.BookInfo,mcbids)
		pool.close()
		pool.join()

		dealdb('con_book_copy',bookinfolist)

		dealcbids=[bookinfo['book_id'] for bookinfo in bookinfolist]

		for cbid in dealcbids:
			print 'dealing the cbid:%s!'%cbid
			#处理券列表
			volumelist=ywapicont.VolumeList(cbid)
			dealdb('con_book_vols_copy',volumelist)

			#处理章节列表
			chapterlist=ywapicont.ChapterList(cbid)
			dealdb('con_book_chapinfo_copy',chapterlist)

			#处理章节内容
			cbcids=[(cbid,int(chapter['chap_id'])) for chapter in chapterlist]
			pool = ThreadPool(10)
			isNewCContentContlist = pool.map(ywapicont.ChapterContent,cbcids)
			pool.close()
			pool.join()
			dealdb('con_book_chapcontent_copy',isNewCContentContlist)



if __name__ == '__main__':
	main()

