#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql
import datetime

global today
today = datetime.datetime.now().strftime('%Y-%m-%d')

global prefix
prefix = 'http://www.ddk.gov.cn'

global unfit_urls
unfit_urls = [] # http://www.cqdzhbj.gov.cn/viewcontent.jsp?faid=48&soid=68&id=1623



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


def getDataFromUrl(link, title):
    LinkUrl = link
    Name = ''
    Legal = ''

    Category = ''
    According = ''
    Measure = ''

    UnifiedSocialCode = ''
    CreateDate = ''
    AdministrativeNumber = ''
    Area = '重庆-大渡口区'

    DealUnit = ''

    doc = pq(link, encoding='gb2312')
    content =    textHandel(doc('#showcontent').text(),1)
    content_02 = textHandel(doc('#showcontent').text(),2)

    a_s = doc('#showcontent').children('a')
    # if a_s.length >0:
    #     for a in doc('#showcontent').children('a').items():
    #         a_s_text = a.text()
    #         pattern  =  re.compile(r'执\d{4}-\d{0,3}')
    #         match = pattern.search(a_s_text)
    #         if match:
    #             num = match.group()
    #             a_s_name = a_s_text.replace(num,'')
    #             a_s_name = a_s_name.split('公司')[0]
    #         a_s_href = a.attr('href')
    #         a_s_link = prefix + a_s_href
    #
    #
    #         print([a_s_link , a_s_name])

    if a_s.length < 1:  # 表示文本

        pattern = re.compile(r'渡环罚.\d{4}.\d{0,3}号')
        match = pattern.search(content)
        if match:
            AdministrativeNumber = match.group()


        if '被处罚单位' in content_02 :
            Name = re.search( '被处罚单位.(.*?)\n', content_02).group(1)

        if '法定代表人' in content_02:
            Legal = re.search( '法定代表人.(.*?)\n',content_02).group(1)

        if '信用代码' in content_02:
            UnifiedSocialCode = re.search('信用代码.(.*?)\n' ,content_02).group(1)


        pattern2 = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
        if '重庆市大渡口区环境保护局' in content:
            jieshu = content.split('重庆市大渡口区环境保护局')[-1]
            if '年' in jieshu and '月' in jieshu and '日' in jieshu:
                match2 = pattern2.search(jieshu)
                if match2:
                    CreateDate = match2.group().replace('年', '-').replace('月', '-').replace('日', '')

        if '环境违法行为' in content and '上述行为' in content:
            Category = re.search('环境违法行为.(.*?)上述行为', content).group(1)
            Category = Category.replace(Name , '')

        if '行政处罚决定依据及其履行方式和期限' in content and '重庆市大渡口区环境保护局决定' in content:
            According = re.search('行政处罚决定依据及其履行方式和期限(.*?)重庆市大渡口区环境保护局决定', content).group(1)
            DealUnit = '重庆市大渡口区环境保护局'
        elif '行政处罚决定依据及其履行方式和期限' in content and '重庆市大渡口区环境行政执法支队决定' in content:
            According = re.search('行政处罚决定依据及其履行方式和期限(.*?)，重庆市大渡口区环境行政执法支队决定', content).group(1)
            DealUnit = '重庆市大渡口区环境行政执法支队'
        elif '行政处罚决定依据及其履行方式和期限' in content and '，决定' in content:
            According = re.search('行政处罚决定依据及其履行方式和期限(.*?)，决定', content).group(1)
            DealUnit = '重庆市大渡口区环境保护局'
        elif '行政处罚的依据、种类及其履行方式、期限' in content and '重庆市大渡口区环境保护局决定' in content:
            According = re.search('行政处罚的依据、种类及其履行方式、期限(.*?)重庆市大渡口区环境保护局决定', content).group(1)
            DealUnit = '重庆市大渡口区环境保护局'



        if '下行政处罚：' in content and  '罚款限' in content:
            Measure = re.search('下行政处罚：(.*?)罚款限', content).group(1)
        elif '下行政处罚：' in content and '三、申请复议或者提起诉讼的途径和期限' in content:
            Measure = re.search('下行政处罚：(.*?)三、申请复议或者提起诉讼的途径和期限', content).group(1)

    # link , Name ,Legal , UnifiedSocialCode ,AdministrativeNumber  , CreateDate , Category , According , Measure

    dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
    data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

    if dataFromPage in data_For_Compare:
        return False
    else:
        dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
        if Name.strip() != '':
            sendDataToDb(dataToDb)




def getLinks():
    for i in range(1, 6):
        if i == 1:
            path = 'http://www.ddk.gov.cn/html/zfxxgk/zfjg/bmdw/zfbm/hbj/xzcf/'
        else:
            path = 'http://www.ddk.gov.cn/html/zfxxgk/zfjg/bmdw/zfbm/hbj/xzcf/List_' + str(i) + '.html'

        doc = pq(path, encoding="gb2312")
        items = doc('#showcontent dl dd ul li a').items()
        for i in items:
            href = i.attr('href')
            title = i.attr('title')
            link = prefix + href
            dataFlag = getDataFromUrl(link, title)
            if dataFlag:
                break


getLinks()


