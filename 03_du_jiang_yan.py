#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://www.cdepb.gov.cn'


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

def getDataFromUrl(link,name):
    doc = pq(link, encoding='utf-8')
    content =    textHandel(doc('.ArticleContent').text(),1)
    content_02 = textHandel(doc('.ArticleContent').text(),2)

    LinkUrl = link
    Name = ''
    Legal = ''

    Category = ''
    According = ''
    Measure = ''

    UnifiedSocialCode = ''
    CreateDate = ''
    AdministrativeNumber = ''
    Area = '成都-都江堰市'

    DealUnit = '都江堰市环境保护局'


    if '违法事实' in content_02:
        Match_Category = re.search('违法事实.(.*?)\n',content_02)
        if Match_Category:
            Category = Match_Category.group(1)
    if Category.strip() == '':
        content_02 = content_02.replace('违法事实：\n', '违法事实：')
        if '违法事实' in content_02:
            Category = re.search('违法事实.(.*?)\n', content_02).group(1)


    if '文号' in content_02 :
        AdministrativeNumber = re.search('文号.(.*?)\n' ,content_02).group(1)
    elif '文书号' in content_02:
        AdministrativeNumber = re.search('文书号.(.*?)\n' ,content_02).group(1)


    if '处罚对象' in content_02 :
        Name = re.search( '处罚对象.(.*?)\n', content_02).group(1)
    if Name.strip() == '':
        content_02 = content_02.replace('处罚对象：\n','处罚对象：')
        if '处罚对象' in content_02:
            Name = re.search('处罚对象.(.*?)\n', content_02).group(1)


    if '信用代码（营业执照）' in content_02:
        UnifiedSocialCode = re.search('信用代码（营业执照）.(.*?)\n' ,content_02).group(1)
    elif '信用代码（或营业执照）' in content_02:
        UnifiedSocialCode = re.search('信用代码（或营业执照）.(.*?)\n' ,content_02).group(1)
    elif '信用代码' in content_02:
        UnifiedSocialCode = re.search('信用代码.(.*?)\n' ,content_02).group(1)


    pattern3 = re.compile(r'\d{4}年\d{0,2}月{0,1}\d{0,2}日{0,1}')
    match3 = pattern3.search(content)
    if match3:
        CreateDate = match3.group().replace('年', '-').replace('月', '-').replace('日', '')

    if '事实' in content_02:
        Category = re.search('事实.(.*?)\n', content_02).group(1)

    if '依据' in content_02:
        According = re.search('依据.(.*?)\n', content_02).group(1)

    if '金额' in content_02:
        Measure = re.search('金额.(.*?)\n', content_02).group(1)
    elif '处罚内容' in content_02:
        Measure = re.search('处罚内容.(.*?)\n', content_02).group(1)


    # link , Name 2   ,Legal 1 , UnifiedSocialCode 2 ,AdministrativeNumber 2 , CreateDate 2, Category 2, According 2 , Measure
    # print([link,Measure])



    dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
    data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

    if dataFromPage in data_For_Compare:
        return False
    else:
        dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
        if Name.strip() != '':
            sendDataToDb(dataToDb)




def getLinks():
    for i in range(1,5):
        url = 'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultList.aspx?cid=853&page='+ str(i)
        doc = pq(url, encoding="utf-8")
        div_items = doc('.ArticleList').items()
        for div_item in div_items:
            a = div_item.children('p span:nth-child(2) a:nth-child(2)')
            link = prefix + a.attr('href')
            name = a.attr('title')
            dataFlag = getDataFromUrl(link,name)
            if dataFlag:
                break






getLinks()


