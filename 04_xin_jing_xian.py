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

def getDataFromUrl(link):
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
    Area = '成都-新津县'

    DealUnit = '新津县环境保护局'


    pattern2 =  re.compile(r'新环罚字{0,}.\d{4}.\d{0,4}号')
    pattern3 =  re.compile(r'新环.\d{4}.罚字第\d{0,4}号')
    pattern4 =  re.compile(r'新环法决罚字.\d{4}.\d{0,4}号')
    match_AdministrativeNumber02 = pattern2.search(content)
    if match_AdministrativeNumber02:
        AdministrativeNumber = match_AdministrativeNumber02.group()
    if AdministrativeNumber.strip() == '':
        match_AdministrativeNumber03 = pattern3.search(content)
        if match_AdministrativeNumber03:
            AdministrativeNumber = match_AdministrativeNumber03.group()
    if AdministrativeNumber.strip() == '':
        match_AdministrativeNumber04 = pattern4.search(content)
        if match_AdministrativeNumber04:
            AdministrativeNumber = match_AdministrativeNumber04.group()

    title = doc('.ArticleTitle').text()
    pattern1 = re.compile(r'关于(.*?)行政处罚')
    pattern0 = re.compile(r'关于(.*?)处罚公告')
    match_name1 = pattern1.search(title)
    match_name0 = pattern0.search(title)
    if match_name1:
        Name = match_name1.group(1)
    if Name.strip() == '':
        if match_name0:
            Name = match_name0.group(1)

    if Name.strip() == '':
        if '对象' in content_02:
            Name = re.search('对象.(.*?)\n',content_02).group(1)
    Name = Name.replace('环境', '').replace('的', '')



    if '信用代码' in content and '法定代表人' in content :
        UnifiedSocialCode = re.search('信用代码.(.*?)法定代表人', content).group(1)
    elif '信用代码（或营业执照、身份证号）：\n' in content_02:
        UnifiedSocialCode = re.search('信用代码（或营业执照、身份证号）：\n(.*?)\n', content_02).group(1)
    elif '信用代码（或营业执照、身份证号）' in content_02:
        UnifiedSocialCode = re.search('信用代码（或营业执照、身份证号）.(.*?)\n', content_02).group(1)

    elif '信用代码（或营业执照）：\n' in content_02:
        UnifiedSocialCode = re.search('信用代码（或营业执照）：\n(.*?)\n', content_02).group(1)
    elif'信用代码（或营业执照）' in content_02:
        UnifiedSocialCode = re.search('信用代码（或营业执照）.(.*?)\n', content_02).group(1)

    elif '信用代码：\n' in content_02:
        UnifiedSocialCode = re.search('信用代码：\n(.*?)\n', content_02).group(1)
    elif '信用代码' in content_02:
        UnifiedSocialCode = re.search('信用代码.(.*?)\n', content_02).group(1)


    if '事实' in content_02:
        Match_Category = re.search('事实.(.*?)\n',content_02)
        if Match_Category:
            Category = Match_Category.group(1)
    if Category.strip() == '':
        content_02 = content_02.replace('事实：\n', '事实：')
        if '事实' in content_02:
            Category = re.search(''
                                 '事实.(.*?)\n', content_02).group(1)
    if Category.strip() == '':
        if '环境违法行为' in content and '以上事实' in content:
            Category = re.search( '环境违法行为.(.*?)以上事实', content).group(1)

    if Category.strip() == '':
        if '事由' in content_02:
            Category = re.search( '事由.(.*?)\n', content_02).group(1)


    pattern3 = re.compile(r'\d{4}年\d{0,2}月{0,1}\d{0,2}日{0,1}')
    if '新津县环境保护局' in content:
        jieshu = content.split('新津县环境保护局')[-1]
        if '年' in jieshu and '月' in jieshu and '日' in jieshu:
            match = pattern3.search(jieshu)
            if match:
                CreateDate = match.group().replace('年', '-').replace('月', '-').replace('日', '')
    else:
        match3 = pattern3.search(content)
        if match3:
            CreateDate = match3.group().replace('年', '-').replace('月', '-').replace('日', '')


    if '依据' in content and '我局决定' in content:
        According = re.search('依据.(.*?).我局决定', content).group(1)
    elif '依据' in content_02:
        According = re.search('依据.(.*?)\n',content_02).group(1)


    if '金额' in content_02:
        Measure = re.search('金额.(.*?)\n', content_02).group(1)
    elif '处罚内容' in content_02:
        Measure = re.search('处罚内容.(.*?)\n', content_02).group(1)
    if Measure.strip() == '':
        match_Measure =  re.search('下行政处罚.(.*?)限于',content)
        if match_Measure:
            Measure = match_Measure.group(1)


    if '法定代表人' in content and '地址' in content:
        match_Legal = re.search('法定代表人.(.*?)地址',content)
        if match_Legal :
            Legal = match_Legal.group(1)
    Legal = Legal.replace( '负责人）：', '')
    if '身份证' in Legal:
        Legal = Legal.split('身份证')[0]


    # link , Name   ,Legal  , UnifiedSocialCode   ,AdministrativeNumber  , CreateDate  , Category  , According   , Measure
    # print([link, Legal  ])


    dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
    data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

    if dataFromPage in data_For_Compare:
        return False
    else:
        dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
        if Name.strip() != '':
            sendDataToDb(dataToDb)




def getLinks():
    for i in range(1,19):
        url = 'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultList.aspx?cid=862&page='+str(i)
        doc = pq(url, encoding="utf-8")
        div_items = doc('.ArticleList')
        for div_item in  div_items.items():
            a = div_item.children('p').children('span:nth-child(2)').children('a:nth-child(2)')
            a_href = a.attr('href')
            a_link = prefix + a_href
            dataFlag = getDataFromUrl(a_link)
            if dataFlag:
                break






getLinks()


