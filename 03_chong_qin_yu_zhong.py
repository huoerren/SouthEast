# coding:utf-8

import pymysql
import requests
from pyquery import PyQuery as pq
import re




global prefix
prefix = 'http://www.xycq.gov.cn'

global dataList
dataList = []

global sec_urls
sec_urls = []

html_path = 'http://www.xycq.gov.cn/html/query/punish/list.html'



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

            B = cur.execute(sqla,(dataToDb[0],dataToDb[1],dataToDb[2],dataToDb[3],dataToDb[4],dataToDb[5],dataToDb[6],dataToDb[7],dataToDb[8],dataToDb[9],dataToDb[10]))
            conn.commit()
            print('成功')
        except Exception as e:
            print(str(e))

        cur.close()
        conn.close()
    else:
        return None



def postMethod():
    filePath = 'http://www.xycq.gov.cn/html/query/punish/list.html'

    for k in range(1, 11):  # 循环出　每一页　
        data = {
            "pageNo": k,
            "contentType": 1,
            "contentValue": None
        }

        content = requests.post(filePath, data=data)
        doc = pq(content.text)
        for i in doc('.conpany-name a').items():
            Name = i.text()
            linkurl = prefix + i.attr('href')
            doc_sub = pq(linkurl , encoding="utf-8")
            trs = doc_sub('.tab2-html-box tr')
            data = []
            data_db = []
            for j in trs.items():
                text = j.children('td:nth-child(2)').text()
                data.append(text)
            data.append('重庆-渝中区')
            data.append(linkurl)

            LinkUrl = data[13]
            Name = data[2]
            Legal = ''

            Category = ''
            According = data[6]
            Measure = data[4]

            UnifiedSocialCode = ''
            CreateDate = data[8].replace('/','-')
            AdministrativeNumber = data[0]
            Area = '重庆-渝中区'

            DealUnit = data[7]

            dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
            data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

            if dataFromPage in data_For_Compare:
                return False
            else:
                dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area, DealUnit]
                if Name.strip() != '':
                    sendDataToDb(dataToDb)
                print(dataToDb)



postMethod()












