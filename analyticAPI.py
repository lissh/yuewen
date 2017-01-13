# -*- coding: utf-8 -*-
__author__ = 'lish'
from multiprocessing.dummy import Pool as ThreadPool
from PIL import Image
import time, random, re, json, hashlib
import urllib2, urllib, datetime, time
import ConfigParser
import multigetletter as toletter
import sys, os, json,io

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

        cover_path=self.host_coverpath+str(time.strftime("%Y%m%d", time.localtime()))+'/'+str(bid)+'.jpg'
        isExists=os.path.exists(self.host_coverpath+str(time.strftime("%Y%m%d", time.localtime()))+'/')
        if not isExists:
            os.makedirs(self.host_coverpath+str(time.strftime("%Y%m%d", time.localtime()))+'/')
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

            #接口类型关键词
            resultkeys= result.keys()
            yuewenkeys=['types','cbids','book','resultData','content']
            keys=list(set(resultkeys)&set(yuewenkeys))

            if len(keys)==1:
                key=keys[0]
                resultvalue=result[key]
            else:
                resultvalue=[]
                print '接口类型关键字集合不合法，请核查！'

            return resultvalue
        else:
            print 'API fail，erorr_code:%s'%bejson["returnCode"]




    def BCategoryList(self,mcpid):
        actionInfos = {'service':'CpNovel','action': 'bookcategorylist'}
        categorylistcont=self.analyticCont(self.appKey,actionInfos)
        categorylist=[]
        keysdict={'fst_class_id':'freetype','fst_class_name':'freetypename','snd_class_id':'categoryid','snd_class_name':'categoryname','trd_class_id':'subcategoryid','trd_class_name':'subcategoryname'}
   
        for categorycont in categorylistcont:
            categoryinfo={'mcp_id':mcpid}
            for key,value in keysdict.items():
                categoryinfo[key]=categorycont[value]
            categorylist.append(categoryinfo)

        return categorylist
        # sql=''

    ##获得图书列表
    def BookList(self):
        pagesize=100000
        cbids=[]
        for pageno in range(1,5):
            actionInfos = {'service':'CpNovel','action': 'booklist','pageNo':pageno, 'pageSize':pagesize}
            pagecbids=self.analyticCont(self.appKey,actionInfos)
            #判断是否为结束页面
            pagecbids=[int(pagecbid) for pagecbid in pagecbids]
            if pagecbids!=[] and cbids!=[]:
                endflog=list(set(cbids)&set(pagecbids))
                if endflog==[]:
                    cbids+=pagecbids
                else:
                    break
            elif cbids==[]:
                cbids+=pagecbids
            elif pagecbids:
                break
        cbids=list(set(cbids))
        print len(cbids)
        return cbids

    def GroundBookList(self,starttime='2015-09-11 19:00:00',endtime='2015-09-11 19:50:00'):
        actionInfos = {'service':'CpNovel','action':'groundbooklist','startTime':starttime,'endTime':endtime}
        groundbids=analyticCont(self.appKey,actionInfos)
        # print groundbids
        return groundbids


    def BookInfo(self,mcbid):
        mcpid=int(mcbid[0])
        cbid=int(mcbid[1])
        actionInfos = {'service':'CpNovel','action': 'bookinfo', 'CBID': cbid }
        bookinfocont=self.analyticCont(self.appKey,actionInfos)
        bookinfo={'mcp_id':mcpid}
        #我们表中字段名跟第三方字段名对应关系字典
        keysdict={'book_id':'cBID','book_name':'title','book_cover':'coverurl','book_synopses':'intro','short_sub_title':'title','long_sub_title':'keyword','category_id':'subcategoryid','serial_status':'status','create_time':'createtime','modify_time':'updatetime','author_id':'authorid'}
        for key,value in keysdict.items():
            bookinfo[key]=bookinfocont[value]
        #处理封面
        self.cutPicture(cbid,bookinfocont['coverurl'])
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
        #处理book_letter
        firstletter=toletter.multi_get_letter(bookinfo['book_name'])[0]
        bookinfo['book_letter']=firstletter.upper()
        #处理价格
        pricekey=list(set(['unitprice','totalprice'])&set(bookinfocont.keys()))
        if pricekey!=[]:
            bookinfo['book_price']=bookinfocont[pricekey[0]]
        else:
            bookinfo['book_price']=0

        #处理时间create_time,modify_time
        createtime=bookinfo['create_time']
        mytime=datetime.datetime.strptime(createtime, "%Y-%m-%d %H:%M:%S").time()
        mydate= datetime.datetime.strptime(createtime, "%Y-%m-%d %H:%M:%S").date()
        bookinfo['create_time']=datetime.datetime.combine(mydate,mytime)

        modifytime=bookinfo['modify_time']
        mytime=datetime.datetime.strptime(modifytime, "%Y-%m-%d %H:%M:%S").time()
        mydate=datetime.datetime.strptime(modifytime, "%Y-%m-%d %H:%M:%S").today()
        bookinfo['modify_time']=datetime.datetime.combine(mydate,mytime)
        
        return bookinfo


    def VolumeList(self,cbid=3606775104033801):
        actionInfos = {'service':'CpNovel','action': 'volumelist', 'CBID': cbid,'pageNo':1, 'pageSize':1000}
        volumelistcont=self.analyticCont(self.appKey,actionInfos)
        volumelist=[]
        #我们表中字段名跟第三方字段名对应关系字典
        keysdict={'vol_title':'volumename','book_id':'cBID','vol_id':'cVID'}
        for volumecont in volumelistcont:
            volumeinfo={}
            for key,value in keysdict.items():
                volumeinfo[key]=volumecont[value]
            volumelist.append(volumeinfo)
        # print volumelist
        return volumelist

    def VolumeInfo(self,cbid=3606775104033801,cvid=9681863266308581):
        actionInfos = {'service':'CpNovel','action': 'volume', 'CBID': cbid, 'CVID':cvid}
        volumecont=self.analyticCont(self.appKey,actionInfos)
        volumeinfo={}
        keysdict={'vol_title':'volumename','book_id':'cBID','vol_id':'cVID','vol_desc':'volumedesc'}
        for key,value in keysdict.items():
            volumeinfo[key]=volumecont[value]

        print volumeinfo

    def VolumeChapterList(self,cbid=3606775104033801,cvid=9681863266308581):
        actionInfos = {'service':'CpNovel','action': 'volumechapterlist', 'CBID': cbid, 'CVID':cvid,'pageNo':1, 'pageSize':10000}
        # actionInfos = {'service':'CpNovel','action': 'volumechapterlist', 'CBID': cbid, 'CVID':cvid,'pageNo':1, 'pageSize':10}
        volumechapterlistcont=self.analyticCont(self.appKey,actionInfos)
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
        # print volumechapterlist
        return volumechapterlist

    def ChapterList(self,cbid=3606775104033801):
        actionInfos = {'service':'CpNovel','action': 'chapterlist', 'CBID': cbid,'pageNo':1, 'pageSize':100000}
        # actionInfos = {'service':'CpNovel','action': 'chapterlist', 'CBID': cbid, 'pageNo':1, 'pageSize':10}
        chapterlistcont=self.analyticCont(self.appKey,actionInfos)
        # print chapterlistcont
        keysdict={'chap_id':'cCID','book_id':'cBID','vol_id':'cVID','chap_name':'chaptertitle','chap_price':'amount','chap_rank':'chaptersort','create_time':'updatetime','status':'status','vip_status':'vipflag','word_size':'originalwords'}
        chapterlist=[]
        for chaptercont in chapterlistcont:
            chapterinfo={}
            for key,value in keysdict.items():
                try:
                    chapterinfo[key]=chaptercont[value]
                except Exception, e:
                    chapterinfo[key]=''

            if chapterinfo['create_time']=='':
                createtime=str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                mytime=datetime.datetime.strptime(createtime, "%Y-%m-%d %H:%M:%S").time()
                mydate=datetime.datetime.strptime(createtime, "%Y-%m-%d %H:%M:%S").today()
                chapterinfo['create_time']=datetime.datetime.combine(mydate,mytime)

            if chapterinfo['vip_status']==-1:
                chapterinfo['vip_status']=0
            else:
                chapterinfo['vip_status']=1
            chapterlist.append(chapterinfo)
        # print chapterlist
        return chapterlist

    def ChapterInfo(self,cbid=3606775104033801,ccid=9681863240503756):
        actionInfos = {'service':'CpNovel','action': 'chapter', 'CBID': cbid,'CCID':ccid}
        chaptercont=self.analyticCont(self.appKey,actionInfos)
        chapterinfo={}
        keysdict={'chap_id':'cCID','book_id':'cBID','vol_id':'cVID','chap_name':'chaptertitle','chap_price':'amount','chap_rank':'chaptersort','create_time':'updatetime','status':'status','vip_status':'vipflag','word_size':'originalwords'}
        for key,value in keysdict.items():
            chapterinfo[key]=chaptercont[value]
        # print chapterinfo
        return chapterinfo


    def ChapterContent(self,cbcid):
        cbid=int(cbcid[0])
        ccid=int(cbcid[1])
        actionInfos = {'service':'CpNovel','action': 'content', 'CBID': cbid, 'CCID':ccid }
        chaptercontentcont=self.analyticCont(self.appKey,actionInfos)

        chaptercontent={}
        keysdict={'chap_id':'cCID','content':'content'}
        for key,value in keysdict.items():
            chaptercontent[key]=chaptercontentcont[value]
        # print chaptercontent
        return chaptercontent




if __name__ == '__main__':
    app=YWJsonAPI()
    # print app.ChapterList(2629224000085701)
    print app.ChapterList()



