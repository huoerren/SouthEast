#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://www.cdepb.gov.cn'

global unfit_urls
unfit_urls = ['http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=850&aid=7036857899A14EEE8D6859A1AC6236F8']

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
    sql = 'select Name,Category,According,Measure,CreateDate,Area,LinkUrl from xingzhengchufa_huanan where  Area = "'+ Area +'" '
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
                            LinkUrl,Name,Legal,CreateDate,Category,According,Measure,AdministrativeNumber,UnifiedSocialCode,Area 
                         ) 
                    values
                        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s );
                '''

            B = cur.execute(sqla,(dataToDb[0],dataToDb[1],dataToDb[2],dataToDb[3],dataToDb[4],dataToDb[5],dataToDb[6],dataToDb[7],dataToDb[8],dataToDb[9] ))
            conn.commit()
            print('成功')
        except Exception as e:
            print(str(e))

        cur.close()
        conn.close()
    else:
        return None

def getDataFromUrl(link):
    if link not in unfit_urls:
        doc = pq(link, encoding='utf-8')
        content = textHandel(doc('.ArticleContent').text(),1)
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
        Area = '成都-青白江区'


        if '行政处罚单位：\n' in content_02:
            Name = re.search('行政处罚单位.\n(.*?)\n', content_02).group(1)
        elif '被处罚单位：\n' in content_02:
            Name = re.search('被处罚单位.\n(.*?)\n', content_02).group(1)
        elif '行政处罚对象：\n' in content_02:
            Name = re.search('行政处罚对象.\n(.*?)\n', content_02).group(1)
        elif '行政处罚单位' in content_02:
            Name = re.search('行政处罚单位.(.*?)\n', content_02).group(1)
        elif '被处罚单位' in content_02:
            Name = re.search('被处罚单位.(.*?)\n', content_02).group(1)
        elif '行政处罚对象' in content_02:
            Name = re.search('行政处罚对象.(.*?)\n', content_02).group(1)


        if '法定代表人：\n' in content_02:
            Legal = re.search('法定代表人.\n(.*?)\n',content_02).group(1)
        elif '法定代表人' in content_02:
            Legal = re.search('法定代表人.(.*?)\n',content_02).group(1)

        if '社会代码：\n' in content_02:
            UnifiedSocialCode = re.search( '社会代码.\n(.*?)\n', content_02).group(1)
        elif '社会代码' in content_02:
            UnifiedSocialCode = re.search( '社会代码.(.*?)\n', content_02).group(1)
        UnifiedSocialCode = UnifiedSocialCode.replace('营业执照）：' , '')


        if '处罚文号：\n' in content_02:
            AdministrativeNumber = re.search( '处罚文号.\n(.*?)\n', content_02).group(1)
        elif '信用代码：\n' in content_02:
            AdministrativeNumber = re.search( '信用代码.\n(.*?)\n', content_02).group(1)
        elif '处罚文号' in content_02:
            AdministrativeNumber = re.search( '处罚文号.(.*?)\n', content_02).group(1)
        elif '信用代码' in content_02:
            AdministrativeNumber = re.search( '信用代码.(.*?)\n', content_02).group(1)


        if '时间' in content_02:
            match = re.search('时间.(.*?)\n',content_02)
            if match :
                CreateDate = match.group(1)
            else:
                CreateDate = re.search('时间.(\w+)',content).group(1)
            CreateDate = CreateDate.replace('年','-').replace('月','-').replace('日','')

        if '违法行为/案由：\n' in content_02:
            Category = re.search('违法行为/案由.\n(.*?)\n', content_02).group(1)
        elif '违法事实：\n' in content_02:
            Category = re.search('违法事实.\n(.*?)\n', content_02).group(1)
        elif '处罚内容：\n' in content_02:
            Category = re.search('处罚内容：\n(.*?)\n', content_02).group(1)
        elif '违法行为/案由' in content_02:
            Category = re.search('违法行为/案由.(.*?)\n', content_02).group(1)
        elif '违法事实' in content_02:
            Category = re.search('违法事实.(.*?)\n', content_02).group(1)
        elif '处罚内容' in content_02:
            Category = re.search('处罚内容.(.*?)\n', content_02).group(1)


        if '处罚依据：\n' in content_02:
            According = re.search('处罚依据.\n(.*?)\n' ,content_02).group(1)
        elif '处罚依据' in content_02:
            According = re.search('处罚依据.(.*?)\n' ,content_02).group(1)


        if '金额：\n' in content_02:
            match2 = re.search('金额.\n(.*?)\n',content_02)
            if match2:
                Measure = match2.group(1)
            else:
                Measure = re.search('金额.(\w+)',content).group(1)
        elif '处罚内容：\n' in content_02 :
            Measure = re.search('处罚内容.\n(.*?)\n',content_02).group(1)
        elif '金额' in content_02:
            match2 = re.search('金额.(.*?)\n',content_02)
            if match2:
                Measure = match2.group(1)
            else:
                Measure = re.search('金额.(\w+)',content).group(1)
        elif '处罚内容' in content_02 :
            Measure = re.search('处罚内容.(.*?)\n',content_02).group(1)


        # print([link, Name, UnifiedSocialCode, AdministrativeNumber, CreateDate, Legal ,Category , According, Measure] )
        # link , Name 1 ,Legal 1 , UnifiedSocialCode 1 ,AdministrativeNumber 1 , CreateDate , Category , According , Measure
        # print([link , Measure])

        dataFromPage = [Name, Category, According, Measure, CreateDate, Area ,LinkUrl]
        data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

        if dataFromPage in data_For_Compare:
            return False
        else:
            dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ]
            if Name.strip() != '':
                sendDataToDb(dataToDb)




def getLinks():
    for i in range(1,11):
        j = str(i)
        url = 'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultList.aspx?cid=850&page='+j
        doc = pq(url, encoding="utf-8")
        div_items = doc('.ArticleList').items()
        for div_item in div_items:
            for a in div_item.find('p span a').items():
                if a.attr('href') != '#':
                    link = prefix + a.attr('href')
                    dataFlag = getDataFromUrl(link)
                    if dataFlag:
                        break


getLinks()


