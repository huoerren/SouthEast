#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql


global unfit_urls
unfit_urls = []

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
    if link not in unfit_urls:
        # link = 'http://yl.km.gov.cn/c/2017-07-05/1742336.shtml'
        doc = pq(link, encoding='gbk')
        content = doc('.conTxt')

        content_1 = textHandel(content.text().replace(':','：') ,1)
        content_2 = textHandel(content.text().replace(':','：'), 2)

        LinkUrl = link
        Name = ''
        Legal = ''

        Category = ''
        According = ''
        Measure = ''

        UnifiedSocialCode = ''
        CreateDate = ''
        AdministrativeNumber = ''
        Area = '西藏自治区'

        DealUnit = '西藏自治区环境保护局'

        Name = content.children('p:nth-child(1)').text()

        if '法定代表人（负责人）' in content_2:
            Legal = re.search('法定代表人（负责人）.(.*?)\n', content_2).group(1)
        elif '法定代表人' in content_2:
            Legal = re.search('法定代表人.(.*?)\n', content_2).group(1)


        if '环境违法事实和证据' in content_1 and '你公司的以上行为' in content_1:
            Category = re.search('环境违法事实和证据(.*?)你公司的以上行为', content_1).group(1)


        Acc_Mea = re.search('行政处罚的依据、种类(.*?)三、行政处罚决定的履行方式和期限', content_1).group(1)

        if '决定' in Acc_Mea :
            According = Acc_Mea.split('，决定')[0]
            Measure   = Acc_Mea.split('，决定')[1]



        if '信用代码' in content_2:
            UnifiedSocialCode =  re.search('信用代码.(.*?)\n',content_2).group(1)


        #                 Name , Legal ,Category   According  Measure  CreateDate  UnifiedSocialCode  AdministrativeNumber
        # print([LinkUrl, Name, Legal , Category , According, Measure ,CreateDate, UnifiedSocialCode ,AdministrativeNumber ])

        dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
        data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

        if dataFromPage in data_For_Compare:
            return True
        else:
            dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
            if Name.strip() != '':
                sendDataToDb(dataToDb)



def getLinks():
        href = 'http://www.xzep.gov.cn/index.php/cms/item-list-category-1329.shtml'
        doc = pq(href,encoding='gbk')
        ul = doc('.main1').children('ul')
        lis = ul.children('li')
        for li in lis.items():
            a = li.children('a')
            title = a.text()
            link  = a.attr('href')
            if '行政处罚决定书' in title:
                dataFlag = getDataFromUrl(link, title)
                if dataFlag:
                    break



getLinks()





































