#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://www.cdepb.gov.cn'

global unfit_urls
unfit_urls = ['http://www.gzwd.gov.cn/zwgk/zdlygk/zfcg/xzcf/201705/t20170508_1796653.html',
              'http://www.gzwd.gov.cn/zwgk/zdlygk/zfcg/xzcf/201705/t20170508_1796652.html']

def textHandel(text,flag):
    if len(text) != 0:
        if flag == 1:
            return text.replace('\n', '').replace('\r\n','').replace(' ', '').replace('\xa0', '')
        elif flag ==2:
            return text.replace('\r\n', '').replace(' ', '').replace('\xa0', '')
    else:
        return ''


def getDataExisted(Area):
    data_For_Compare = []
    sql = 'select Name,Category,According,Measure,CreateDate,Area from xingzhengchufa_huanan where  Area = "'+ Area +'" '
    conn = pymysql.connect(host='118.178.88.242', user='greentest', password='test@2018', port=3306, db='greentest', charset='utf8')
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        for i in result:
            data_For_Compare.append(list(i))
    except Exception as e:
        print(str(e))
    return data_For_Compare



def sendDataToDb(dataToDb):
    conn = pymysql.connect(host='118.178.88.242', user='greentest', password='test@2018', port=3306,db='greentest',charset='utf8')
    cur = conn.cursor()
    if dataToDb != None:
        try:
            print(dataToDb[0])
            sqla = '''
                    insert into  xingzhengchufa_huanan (
                            LinkUrl,Name,Legal,CreateDate,Category,According,Measure,AdministrativeNumber,UnifiedSocialCode,Area,DealUnit
                         ) 
                    values
                        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                '''

            B = cur.execute(sqla,(dataToDb[0],dataToDb[1],dataToDb[2],dataToDb[3],dataToDb[4],dataToDb[5],dataToDb[6],dataToDb[7],dataToDb[8],dataToDb[9],dataToDb[10] ))
            conn.commit()
            print('成功')
        except Exception as e:
            print(str(e))

        cur.close()
        conn.close()
    else:
        return None

def getDataFromUrl(link,title):

    doc = pq(link, encoding='utf-8')
    table = doc('.content').find('table')

    if table.length >0 :
        trs = table.children('tr')
        for tr in trs.items():
            if '序号' not in textHandel(tr.text() ,1):
                tab_val = []
                for td in tr.children('td').items():
                    tab_val.append(textHandel(td.text() ,1))
                print(len(tab_val) ,link)
    else:
        print([link])


    # content =    textHandel(doc('.ArticleContent').text().replace(':','：'),1)
    # content_02 = textHandel(doc('.ArticleContent').text().replace(':','：'),2)



    #  UnifiedSocialCode  AdministrativeNumber CreateDate   |
    # print([LinkUrl, Name, Category , According, Measure ,CreateDate, UnifiedSocialCode ,AdministrativeNumber ])

    # dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
    # data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据
    #
    # if dataFromPage in data_For_Compare:
    #     return False
    # else:
    #     dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
    #     if Name.strip() != '':
    #         sendDataToDb(dataToDb)



def getLinks():
    for i in range(0,2):
        if i == 0:
            url = 'http://www.gzwd.gov.cn/zwgk/zdlygk/zfcg/xzcf/index.html'
        else:
            url = 'http://www.gzwd.gov.cn/zwgk/zdlygk/zfcg/xzcf/index_'+str(i)+'.html'
        doc = pq(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'},
                 encoding="utf-8")
        items = doc('.NewsList ul li').items()
        for item in items:
            link = item.find('a').attr('href')
            title = item.find('a').text()
            if '行政处罚决定书' in title or '行政处罚案件信息公开统计表' in title:
                if link not in unfit_urls:
                    print(link)
                    dataFlag = getDataFromUrl(link,title)
                    # if dataFlag:
                    #     break


getLinks()


