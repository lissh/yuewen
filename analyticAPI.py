# -*- coding: utf-8 -*-
__author__ = 'lish'
from multiprocessing.dummy import Pool as ThreadPool
from PIL import Image
import time, random, re, json, hashlib
import urllib2, urllib, datetime, time
import ConfigParser
import sys, os, json
import dealdb
reload(sys)
sys.setdefaultencoding('utf-8')


class YWJsonAPI(object):
    def __init__(self):
        self.host_url='http://cp.book.qq.com/ServiceBus.do?'
        self.host_coverpath='/data/static/con/image/book/'
        self.host_coverurl='con/image/book/'
        self.appKey = 'b7f7a2f01203'

    def cutPicture(self,bid,url,wsize=480,hsize=640):
        image_bytes = urllib2.urlopen(url).read()
        # internal data file
        data_stream = io.BytesIO(image_bytes)
        # open as a PIL image object
        pil_image = Image.open(data_stream)
        pil_image_resized = pil_image.resize((wsize, hsize), Image.ANTIALIAS)
        xsize,ysize=pil_image_resized.size
        box=(0,0,xsize,ysize)

        cover_path=host_coverpath+str(time.strftime("%Y%m%d", time.localtime()))+'/'+str(bid)+'.jpg'
        isExists=os.path.exists(cover_path)
        if not isExists:
            os.makedirs(host_coverpath+str(time.strftime("%Y%m%d", time.localtime())))
        pil_image_resized.crop(box).save(cover_path)

    def createActionURL(self,appKey,actionInfos):
        #生产appToken值
        appToken = appKey[-4::] + time.strftime("%Y%m%d", time.localtime())
        m = hashlib.md5()
        m.update(appToken)
        md5value = m.hexdigest()
        appToken = md5value[0:12]
        actionInfos['appKey']=appKey
        actionInfos['appToken']=appToken
        #生产API的URL地址
        url_para = ''
        for key, value in actionInfos.items():
            if url_para!='':
                url_para +='&'+key + '=' + str(value)
            else:
                url_para += key + '=' + str(value)
        url = self.host_url + url_para
        return url


    def analyticCont(self,appKey,actionInfos):
        url=self.createActionURL(appKey,actionInfos)
        req = urllib2.Request(url)
        content = urllib2.urlopen(req).read()
        bejson = json.loads(str(content))
        #业务数据字段result
        if bejson["returnCode"]==0 and bejson["returnMsg"]=="Success":
            result=bejson['result']
        else:
            print 'API接口内容获取失败，错误代码:%s'%bejson["returnCode"]

        resultkeys= result.keys()
        yuewenkeys=['types','cbids','book','resultData','content']
        keys=list(set(resultkeys)&set(yuewenkeys))

        if len(keys)==1:
            key=keys[0]
            resultvalue=result[key]
        else:
            resultvalue=[]
            print '借口关键字集合不合法，请核查！'

        return resultvalue




    def BCategoryList(self):
        actionInfos = {'service':'CpNovel','action': 'bookcategorylist'}
        categorylistcont=self.analyticCont(self.appKey,actionInfos)
        # [u'status', u'subcategoryid', u'freetype', u'categoryname', u'iDX', u'freetypename', u'subcategoryname', u'categoryid']
        categorylist=[(categorycont['freetype'],categorycont['freetypename'],categorycont['categoryid'],categorycont['categoryname'],categorycont['subcategoryid'],categorycont['subcategoryname']) for categorycont in categorylistcont]
        print categorylist
        return categorylist
        # sql=''

    ##获得图书列表
    def BookList(self):
        actionInfos = {'service':'CpNovel','action': 'booklist'}
        cbids=self.analyticCont(self.appKey,actionInfos)
        print cbids
        return cbids

    def GroundBookList(self,starttime='2015-09-11 19:00:00',endtime='2015-09-11 19:50:00'):
        actionInfos = {'service':'CpNovel','action':'groundbooklist','startTime':starttime,'endTime':endtime}
        groundbids=analyticCont(self.appKey,actionInfos)
        print groundbids
        return groundbids


    def BookInfo(self,cbid=3606775104033801):
        actionInfos = {'service':'CpNovel','action': 'bookinfo', 'CBID': cbid }
        bookinfocont=self.analyticCont(self.appKey,actionInfos)
        bookinfo={}
        #我们表中字段名跟第三方字段名对应关系字典
        keysdict={'book_id':'cBID','book_name':'title','book_cover':'coverurl','book_synopses':'intro','short_sub_title':'title','long_sub_title':'keyword','category_id':'subcategoryid','serial_status':'status','createtime':'createtime','modify_time':'updatetime','author_id':'authorid'}
        for key,value in keysdict.items():
            bookinfo[key]=bookinfocont[value]
        #处理封面
        self.cutPicture(cbid,bookinfo['coverurl'])
        bookinfo['book_cover']=self.host_coverurl+str(time.strftime("%Y%m%d", time.localtime()))+'/'+str(cbid)+'.jpg'
        #'书籍状态“0:编辑强制下架 1:发布状态 2:待上架 3:删除  作者新增章节后可以设置为：1和2 编辑可以操作为： 0，3'
        bookinfo['book_status']=1
        #自己的status:0 连载 1已完成 2出版中 3暂停 4封笔'---阅文进度状态 30:连载 中 40:暂停中 45: 完结申请 50:已完
        status=bookinfo['serial_status']
        if  status==30:
            bookinfo['serial_status']=0
        elif status==40:
            bookinfo['serial_status']=3
        elif status==45:
            bookinfo['serial_status']=4
        elif status==50:
            bookinfo['serial_status']=1

        #处理价格
        pricekey=list(set(['unitprice','totalprice'])&set(bookinfocont.keys()))
        if pricekey=![]:
            bookinfo['book_price']=bookinfocont[pricekey[0]]
        else:
            bookinfo['book_price']=0
        
        print bookinfo
        return bookinfo


    def VolumeList(self,cbid=3606775104033801):
        actionInfos = {'service':'CpNovel','action': 'volumelist', 'CBID': cbid}
        volumelistcont=analyticCont(self.appKey,actionInfos)
        volumelist=[]
        #我们表中字段名跟第三方字段名对应关系字典
        keysdict={'vol_title':'volumename','book_id':'cBID','vol_id':'cVID'}
        for volumecont in volumelistcont:
            volumeinfo={}
            for key,value in keysdict.items():
                volumeinfo[key]=volumecont[value]
            volumelist.append(volumeinfo)
        print volumelist
        return volumelist

    def VolumeInfo(self,cbid=3606775104033801,cvid=9681863266308581):
        actionInfos = {'service':'CpNovel','action': 'volume', 'CBID': cbid, 'CVID':cvid}
        volumecont=analyticCont(self.appKey,actionInfos)
        volumeinfo={}
        keysdict={'vol_title':'volumename','book_id':'cBID','vol_id':'cVID','vol_desc':'volumedesc'}
        for key,value in keysdict.items():
            volumeinfo[key]=volumecont[value]

        print volumeinfo

    def VolumeChapterList(self,cbid=3606775104033801,cvid=9681863266308581):
        actionInfos = {'service':'CpNovel','action': 'volumechapterlist', 'CBID': cbid, 'CVID':cvid}
        # actionInfos = {'service':'CpNovel','action': 'volumechapterlist', 'CBID': cbid, 'CVID':cvid,'pageNo':1, 'pageSize':10}
        volumechapterlistcont=analyticCont(self.appKey,actionInfos)
        keysdict={'chap_id':'cCID','book_id':'cBID','vol_id':'cVID','chap_name':'chaptertitle','chap_price':'amount','chap_rank':'chaptersort','create_time':'updatetime','status':'status','vip_status':'vipflag','word_size':'originalwords'}
        volumechapterlist=[]
        for volumechaptercont in volumechapterlistcont:
            chapterinfo={}
            for key,value in keysdict.items():
                chapterinfo[key]=volumechaptercont[value]
            if chapterinfo['vip_status']==-1:
                chapterinfo['vip_status']=0
            else:
                chapterinfo['vip_status']=1
            volumechapterlist.append(chapterinfo)
        print volumechapterlist
        return volumechapterlist

    def ChapterList(self,cbid=3606775104033801):
        actionInfos = {'service':'CpNovel','action': 'chapterlist', 'CBID': cbid}
        # actionInfos = {'service':'CpNovel','action': 'chapterlist', 'CBID': cbid, 'pageNo':1, 'pageSize':10}
        chapterlistcont=analyticCont(self.appKey,actionInfos)
        keysdict={'chap_id':'cCID','book_id':'cBID','vol_id':'cVID','chap_name':'chaptertitle','chap_price':'amount','chap_rank':'chaptersort','create_time':'updatetime','status':'status','vip_status':'vipflag','word_size':'originalwords'}
        chapterlist=[]
        for chaptercont in chapterlistcont:
            chapterinfo={}
            for key,value in keysdict.items():
                chapterinfo[key]=chaptercont[value]
            if chapterinfo['vip_status']==-1:
                chapterinfo['vip_status']=0
            else:
                chapterinfo['vip_status']=1
            chapterlist.append(chapterinfo)
        print chapterlist
        return chapterlist

    def ChapterInfo(self,cbid=3606775104033801,ccid=9681863240503756):
        actionInfos = {'service':'CpNovel','action': 'chapter', 'CBID': cbid,'CCID':ccid}
        chaptercont=analyticCont(self.appKey,actionInfos)
        chapterinfo={}
        keysdict={'chap_id':'cCID','book_id':'cBID','vol_id':'cVID','chap_name':'chaptertitle','chap_price':'amount','chap_rank':'chaptersort','create_time':'updatetime','status':'status','vip_status':'vipflag','word_size':'originalwords'}
        for key,value in keysdict.items():
            chapterinfo[key]=chaptercont[value]
        print chapterinfo
        return chapterinfo


    def ChapterContent(self,cbid=3606775104033801,ccid=9681863240503756):
        actionInfos = {'service':'CpNovel','action': 'content', 'CBID': 3606775104033801, 'CCID':9681863240503756}
        chaptercontentcont=analyticCont(self.appKey,actionInfos)

        chaptercontent={}
        keysdict={'chap_id':'cCID','content':'content'}
        for key,value in keysdict.items():
            chaptercontent[key]=chaptercontentcont[value]
        print chaptercontent
        return chaptercontent




if __name__ == '__main__':
    app=YWJsonAPI()
    app.BookInfo()



