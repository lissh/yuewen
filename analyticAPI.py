# -*- coding: utf-8 -*-
__author__ = 'lish'
import time, random, re, json, hashlib
import urllib2, urllib, datetime, time
import ConfigParser
import sys, os, json

reload(sys)
reload(sys)
sys.setdefaultencoding('utf-8')


# conf_path=os.path.split( os.path.realpath( sys.argv[0] ) )[0]+'/'
host_url='http://cp.book.qq.com/ServiceBus.do?'






def createActionURL(appKey, actionInfos):
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
    url = host_url + url_para
    req = urllib2.Request(url)
    content = urllib2.urlopen(req).read()
    print content







if __name__ == '__main__':
    # mcpid=128
    # app=IMJsonAPI(test_apiurls)
    # # bookinfos=app.BookInfos(1920,mcpid)
    # bookinfos=app.BookChapterIds(1920,46465)
    # # bookinfos=app.BookChapterCont({'bookid': 128, 'chapterid': 193971, 'chapterrank': 184, 'sourcebid': 1920, 'chaptername': '\xe7\xac\xac\xe4\xb8\x80\xe7\x99\xbe\xe5\x85\xab\xe5\x8d\x81\xe4\xb8\x89\xe7\xab\xa0\xef\xbc\x9a\xe7\xbc\x94\xe9\x80\xa0\xe6\x96\xb0\xe7\xa7\xa9\xe5\xba\x8f', 'pricetype': 2})
    # print str(tuple(bookinfos[0].keys())).replace("'",'')
    # print bookinfos[0].values()
    # print bookinfos[0].items()
    appKey = 'b7f7a2f01203'
    # actionInfos={'action':'bookinfo','CBID':22037867000124502,'pageNo':1,'pageSize':5}
    actionInfos = {'service':'CpNovel','action': 'booklist'}
    createActionURL(appKey, actionInfos)
