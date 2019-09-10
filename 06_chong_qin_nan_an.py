#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'https://hb.qianjiang.gov.cn'


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

def getDataFromUrl(data):

    LinkUrl = data[0]
    Name = data[1]
    Legal = ''

    Category = ''
    According = ''
    Measure = ''

    UnifiedSocialCode = ''
    CreateDate = data[3]
    AdministrativeNumber = data[2]
    Area = '重庆-南岸区'

    DealUnit = '重庆市南岸区环境保护局'



    # link , Name 1 ,Legal 1 , UnifiedSocialCode 1 ,AdministrativeNumber 1 , CreateDate , Category , According , Measure
    # print([link , Measure])

    dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
    data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

    if dataFromPage in data_For_Compare:
        return False
    else:
        dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
        if Name.strip() != '':
            sendDataToDb(dataToDb)




def getLinks():
    for i in range(1,8):
        url = 'http://hbj.cqna.gov.cn/Category_1084/Index_'+str(i)+'.aspx' # 每一页的地址
        doc = pq(url, encoding="utf-8")
        lis = doc('.newsList li').items()
        for j in lis:
            link = j.children('a').attr('href')
            title = j.children('a').text()
            time = j.children('span').text()
            if link != None and ('有限公司' in title or '集团' in title or '经营部' in title or '厂' in title or '公司' in title):
                link = 'http://hbj.cqna.gov.cn' + link
                if '处罚决定书' in title:
                    name = title.split('处罚决定书')[0]
                    AdministrativeNumber = title.split('处罚决定书')[1]

                else:
                    name = title.split('渝南')[0]
                    AdministrativeNumber = '渝南' + title.split('渝南')[1]

                data = [link, name, AdministrativeNumber, time]
                dataFlag = getDataFromUrl(data)
                if dataFlag:
                    break



getLinks()


