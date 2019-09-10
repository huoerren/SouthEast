#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://www.kmepb.gov.cn'

global unfit_urls
unfit_urls = ['']

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
    div_L2 = doc('.L2')
    content_1 = textHandel(div_L2.text() ,1)
    content_2 = textHandel(div_L2.text(), 2)

    LinkUrl = link
    Name = ''
    Legal = ''

    Category = ''
    According = ''
    Measure = ''

    UnifiedSocialCode = ''
    CreateDate = ''
    AdministrativeNumber = ''
    Area = '昆明市'

    DealUnit = '昆明市环境保护局'


    if '姓名：' in content_2:
        Name = re.search('姓名.(.*?)\n', content_2).group(1)
    elif '单位/个人' in content_2:
        Name = re.search('单位/个人.(.*?)\n', content_2).group(1)
    elif '单位'  in content_2:
        Name = re.search( '单位.(.*?)\n',content_2).group(1)


    if '法定代表人' in content_2:
        Legal = re.search('法定代表人.(.*?)\n', content_2).group(1)


    if '违法事实和证据' in content_1 and '以上事实' in content_1:
        Category = re.search('违法事实和证据(.*?)以上事实', content_1).group(1)
    elif '环境违法事实和证据' in content_1 and '以上行为' in content_1:
        Category = re.search('环境违法事实和证据(.*?)以上行为', content_1).group(1)

    if '责令改正和行政处罚的依据、种类' in content_1 and '根据上述规定' in content_1:
        According = re.search('责令改正和行政处罚的依据、种类(.*?)根据上述规定', content_1).group(1)
    elif '行政处罚的依据、种类' in content_1 and '根据上述规定' in content_1:
        According = re.search('行政处罚的依据、种类(.*?)根据上述规定', content_1).group(1)
    elif '行政处罚的依据、种类及其履行方式和期限' in content_1 and '下行政处罚：' in content_1:
        According = re.search('行政处罚的依据、种类及其履行方式和期限(.*?)下行政处罚：', content_1).group(1)
    elif '行政处罚的依据、种类及其履行方式和期限' in content_1 and '行政处罚：' in content_1:
        According = re.search('行政处罚的依据、种类及其履行方式和期限(.*?)行政处罚：', content_1).group(1)

    According = According.replace('，对你公司处以下列','').replace('，对你公司作出如','')\
        .replace( '对你公司作出如', '').replace('，对你检测站作出如' ,'').replace('”对你作出如','').replace('，对你处以下列','')

    if '下决定：' in content_1 and '三、行政处罚决定' in content_1:
        Measure = re.search('下决定：(.*?)三、行政处罚决定', content_1).group(1)
    elif '下决定：' in content_1 and '三、责令改正' in content_1:
        Measure = re.search('下决定：(.*?)三、责令改正', content_1).group(1)
    elif '下决定：' in content_1 and '三、责令限制' in content_1:
        Measure = re.search('下决定：(.*?)三、责令限制', content_1).group(1)
    elif '行政处罚：' in content_1 and '以上罚款' in content_1:
        Measure = re.search('行政处罚：(.*?)以上罚款', content_1).group(1)
    elif '行政处罚：' in content_1 and '三、申请复议' in content_1:
        Measure = re.search('行政处罚：(.*?)三、申请复议', content_1).group(1)
    elif '行政处罚：' in content_1 and '三、责令改正' in content_1:
        Measure = re.search('行政处罚：(.*?)三、责令改正', content_1).group(1)

    elif '，我局决定' in content_1 and '三、责令改正' in content_1:
        Measure = re.search('，我局决定(.*?)三、责令改正', content_1).group(1)

    pattern = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
    if '昆明市环境保护局' in content_1:
        jieshu = content_1.split('昆明市环境保护局')[-1]
        if '年' in jieshu and '月' in jieshu and '日' in jieshu:
            match = pattern.search(jieshu)
            if match:
                CreateDate = match.group().replace('年', '-').replace('月', '-').replace('日', '')

    pattern2 = re.compile(r'昆环罚字{0,1}.\d{4}.\d{0,3}号')
    pattern3 = re.compile(r'滇中环罚{0,1}.\d{4}.\d{0,3}号')
    match2 = pattern2.search(content_1)
    if match2:
        AdministrativeNumber = match2.group()
    if AdministrativeNumber.strip() == '':
        match3 = pattern3.search(content_1)
        if match3:
            AdministrativeNumber = match3.group()


    if '信用代码' in content_2:
        UnifiedSocialCode =  re.search('信用代码.(.*?)\n',content_2).group(1)


    #                 Name , Legal , Category  According  Measure CreateDate    UnifiedSocialCode AdministrativeNumber
    # print([LinkUrl, Name, Legal , Category , According, Measure ,CreateDate, UnifiedSocialCode ,AdministrativeNumber ])

    # print([link ,According   ])


    dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
    data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

    if dataFromPage in data_For_Compare:
        return False
    else:
        dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
        if Name.strip() != '':
            sendDataToDb(dataToDb)



def getLinks():
    for i in range(1,18):
        if i == 1:
            url = 'http://www.kmepb.gov.cn/xxgkml/zdlygzxx/xzcfxx/'
        else:
            url = 'http://www.kmepb.gov.cn/xxgkml/zdlygzxx/xzcfxx/index_'+str(i)+'.shtml'

        doc = pq(url, encoding='utf-8')
        hrefs = doc('#listblock table tbody tr').items()
        for item in hrefs:
            link = prefix + item.children('.li2 a').attr('href')  # 处罚书 链接
            name = item.children('.li2 a').text()
            if '行政处罚决定书' in name:
                # print([link , name])
                dataFlag = getDataFromUrl(link, name)
                if dataFlag:
                    break
        # for div_item in div_items:
        #     a = div_item.children('p span:nth-child(2) a:nth-child(2)')
        #     link = prefix + a.attr('href')
        #     title= a.attr('title')
        #     dataFlag = getDataFromUrl(link,title)
            # if dataFlag:
            #     break


getLinks()





































