#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://www.ynepb.gov.cn/hjjc/hjjcxzcf'

global prefix_01
prefix_01 = 'http://www.ynepb.gov.cn'

global prefix_02
prefix_02 = 'http://www.ynepb.gov.cn/hjjc'


global unfit_urls
unfit_urls = ['http://www.ynepb.gov.cn/hjjc/hjjcxzcf/201504/t20150416_77535.html',
              'http://www.ynepb.gov.cn/hjjc/hjjcxzcf/201504/t20150413_77483.html']

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
                            LinkUrl,Name,Legal,CreateDate,Category,According,Measure,AdministrativeNumber,UnifiedSocialCode,Area,DealUnit,PunishContentHtml
                         ) 
                    values
                        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                '''

            B = cur.execute(sqla,(dataToDb[0],dataToDb[1],dataToDb[2],dataToDb[3],dataToDb[4],dataToDb[5],dataToDb[6],dataToDb[7],dataToDb[8],dataToDb[9],dataToDb[10],dataToDb[11] ))
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
        # link = 'http://www.ynepb.gov.cn/hjjc/hjjcxzcf/201510/t20151022_95632.html'
        # print(link)
        doc = pq(link, encoding='utf-8')
        content = doc('#Zoom')
        content_head = doc('.content-title')

        content_head_1 = textHandel(content_head.text().replace(':','：') ,1)
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
        Area = '云南省'

        DealUnit = '云南省环境保护厅'

        PunishContentHtml = ''

        Name = getName(content_head_1)


        if '法定代表人（负责人）' in content_2:
            Legal = re.search('法定代表人（负责人）.(.*?)\n', content_2).group(1)
        elif '法定代表人' in content_2:
            Legal = re.search('法定代表人.(.*?)\n', content_2).group(1)
        elif '法人代表' in content_2:
            Legal = re.search('法人代表.(.*?)\n', content_2).group(1)
        if '营业执照' in Legal :
            Legal = Legal.split('营业执照')[0]
        if '详细地址' in Legal :
            Legal = Legal.split('详细地址')[0]
        if '职务' in Legal :
            Legal = Legal.split('职务')[0]
        if '身份证号码' in Legal:
            Legal = Legal.split('身份证号码')[0]


        if '违法事实和证据' in content_1 and '以上违法事实' in content_1:
            Category = re.search('违法事实和证据(.*?)以上违法事实', content_1).group(1)
        elif '违法事实和证据' in content_1 and '以上事实' in content_1:
            Category = re.search('违法事实和证据(.*?)以上事实', content_1).group(1)
        elif '环境违法事实和证据' in content_1 and '以上行为' in content_1:
            Category = re.search('环境违法事实和证据(.*?)以上行为', content_1).group(1)
        elif '环境违法行为' in content_1 and '以上事实' in content_1:
            Category = re.search('环境违法行为.(.*?)以上事实', content_1).group(1)
        elif '环境违法事实和证据' in content_1 and '行为' in content_1:
            Category = re.search('环境违法事实和证据.(.*?)行为', content_1).group(1)


        if '责令' in content_1 and '三、行政处罚的履行方式和期限' in content_1:
            Measure = re.search('责令(.*?)三、行政处罚的履行方式和期限',content_1).group(1)
            Measure = '（一）责令' + Measure
        elif '责令' in content_1 and '限于接到' in content_1:
            Measure = re.search('责令(.*?)限于接到', content_1).group(1)
            Measure = '（一）责令' + Measure
        elif '下行政处罚' in content_1 and '限于接到' in content_1:
            Measure = re.search('下行政处罚.(.*?)限于接到', content_1).group(1)
        elif '下行政处罚' in content_1 and '三、行政处罚的履行方式和期限' in content_1:
            Measure = re.search('下行政处罚.(.*?)三、行政处罚的履行方式和期限', content_1).group(1)
        elif '下行政处罚' in content_1 and '三、处罚决定' in content_1:
            Measure = re.search('下行政处罚.(.*?)三、处罚决定', content_1).group(1)
        elif '下处理决定' in content_1 and '三、行政处罚' in content_1:
            Measure = re.search('下处理决定.(.*?)三、行政处罚', content_1).group(1)
        elif '下处理决定' in content_1 and '三、责令改正' in content_1:
            Measure = re.search('下处理决定.(.*?)三、责令改正', content_1).group(1)

        PunishContentHtml = content_1  # 这个站点的 According 太复杂 全文都放到了  PunishContentHtml 这个字段中了


        pattern = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
        if '云南省环境保护厅' in content_1:
            jieshu = content_1.split('云南省环境保护厅')[-1]
            if '年' in jieshu and '月' in jieshu and '日' in jieshu:
                match = pattern.search(jieshu)
                if match:
                    CreateDate = match.group().replace('年', '-').replace('月', '-').replace('日', '')

        pattern2 = re.compile(r'云环罚字{0,1}.\d{4}.\d{0,3}号')
        pattern3 = re.compile(r'维环罚字{0,1}.\d{4}.\d{0,3}号')
        match2 = pattern2.search(content_1)

        if match2:
            AdministrativeNumber = match2.group()
        if  AdministrativeNumber.strip() == '':
            match2 = pattern2.search(content_head_1)
            if match2:
                AdministrativeNumber = match2.group()
        if  AdministrativeNumber.strip() == '':
            match3 = pattern3.search(content_1)
            if match3:
                AdministrativeNumber = match3.group()


        if '信用代码' in content_2:
            UnifiedSocialCode =  re.search('信用代码.(.*?)\n',content_2).group(1)


        #                 Name  Legal   Category   According  Measure  CreateDate                     AdministrativeNumber
        # print([LinkUrl, Name ,Legal , Category , According, Measure ,CreateDate, UnifiedSocialCode ,AdministrativeNumber ])

        # print([link ,Name , UnifiedSocialCode ])


        dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
        data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

        if dataFromPage in data_For_Compare:
            return False
        else:
            dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit , PunishContentHtml]
            if Name.strip() != '':
                sendDataToDb(dataToDb)



def getName(title):

        if '行政处罚决定书' in title and '云环罚' in title:
            Name = re.search('行政处罚决定书.(.*?).云环罚',title).group(1)
        else:
            Name = title.replace('行政处罚决定书','')
        return Name


def getLinks():
    for i in range(0,12):
        if i ==0 :
            url = 'http://www.ynepb.gov.cn/hjjc/hjjcxzcf/index.html'
        else:
            url = 'http://www.ynepb.gov.cn/hjjc/hjjcxzcf/index_'+str(i)+'.html'
        doc = pq(url , encoding='utf-8')
        links = doc('.ui-box span a').items()

        for i in links:
            title = i.text()
            link = ''
            if '../../' in i.attr('href'):
                href = i.attr('href').replace('../..', '')
                link = prefix_01 + href

            elif '../' in i.attr('href'):
                href = i.attr('href').replace('../', '/')
                link = prefix_02 + href

            else:
                href = i.attr('href').replace('./', '/')
                link = prefix + href

            if '行政处罚决定书' in title:
                dataFlag = getDataFromUrl(link, title)
                if dataFlag:
                    break



getLinks()





































