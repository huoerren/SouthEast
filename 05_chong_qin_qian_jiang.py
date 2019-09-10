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

def getDataFromUrl(link,name):
    doc = pq(link, encoding='utf-8')
    content = textHandel(doc('#content').text(),1)
    content_02 = textHandel(doc('#content').text(),2)


    LinkUrl = link
    Name = name
    Legal = ''

    Category = ''
    According = ''
    Measure = ''

    UnifiedSocialCode = ''
    CreateDate = ''
    AdministrativeNumber = ''
    Area = '重庆-黔江区'

    DealUnit = '重庆市黔江区环境行政执法支队'


    pattern = re.compile(r'渝（黔）环执罚.\d{4}.\d{0,3}号')
    pattern2= re.compile(r'黔江环罚.\d{4}.\d{0,3}号')
    match = pattern.search(content)
    if match:
        AdministrativeNumber = match.group()
    if AdministrativeNumber.strip() == '':
        match2 = pattern2.search(content)
        if match2:
            AdministrativeNumber = match2.group()

    # if '被处罚单位' in content_02 :
    #     Name = re.search( '被处罚单位.(.*?)\n', content_02).group(1)
    # if Name.strip('') == '':
    #     content_02 = content_02.replace('被处罚单位：\n','被处罚单位：')
    #     if '被处罚单位' in content_02:
    #         Name = re.search('被处罚单位.(.*?)\n', content_02).group(1)
    #     elif '名称' in content_02:
    #         Name = re.search('名称.(.*?)\n', content_02).group(1)
    #     elif '被处罚经营户' in content_02:
    #         Name = re.search('被处罚经营户.(.*?)\n', content_02).group(1)


    if '法定代表人' in content_02:
        Legal = re.search( '法定代表人.(.*?)\n',content_02).group(1)
    elif '负责人' in content_02:
        Legal = re.search('负责人.(.*?)\n', content_02).group(1)
    Legal = Legal.replace( '名：', '')


    if '信用代码号' in content_02:
        UnifiedSocialCode = re.search('信用代码号.(.*?)\n' ,content_02).group(1)
    elif '信用代码' in content_02:
        UnifiedSocialCode = re.search('信用代码.(.*?)\n' ,content_02).group(1)


    pattern3 = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
    if '重庆市黔江区环境保护局' in content:
        jieshu = content.split('重庆市黔江区环境保护局')[-1]
        if '年' in jieshu and '月' in jieshu and '日' in jieshu:
            match3 = pattern3.search(jieshu)
            if match3:
                CreateDate = match3.group().replace('年', '-').replace('月', '-').replace('日', '')

    if '环境违法行为：' in content and '以上事实' in content:
        Category = re.search('环境违法行为：(.*?)以上事实', content).group(1)
    elif '违法事实、证据、陈述申辩（听证）情况和处罚理由' in content and '上述行为违反' in  content:
        Category = re.search('违法事实、证据、陈述申辩（听证）情况和处罚理由(.*?)上述行为违反', content).group(1)
    elif '违法事实、证据、陈述申辩（听证）情况和处罚理由' in content and '有下列证据为证' in  content:
        Category = re.search('违法事实、证据、陈述申辩（听证）情况和处罚理由(.*?)有下列证据为证', content).group(1)

    if '行政处罚的依据、种类及其履行方式、期限' in content and '，我队决定' in content:
        According = re.search('行政处罚的依据、种类及其履行方式、期限(.*?)，我队决定', content).group(1)
    if '行政处罚的依据、种类及其履行方式、期限' in content and '，决定对' in content:
        According = re.search('行政处罚的依据、种类及其履行方式、期限(.*?)，决定对', content).group(1)

    # #
    if '下行政处罚：' in content and  '罚款限' in content:
        Measure = re.search('下行政处罚：(.*?)罚款限', content).group(1)
    elif '下行政处罚罚：' in content and '罚款限' in content:
        Measure = re.search('下行政处罚罚：(.*?)罚款限', content).group(1)


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
    for i in range(1,7):
        if i ==1 :
            url = 'https://hb.qianjiang.gov.cn/hbj_html/167/index.html'
        else:
            url = 'https://hb.qianjiang.gov.cn/hbj_html/167/index-'+str(i)+'.html'

        doc = pq(url, encoding="utf-8")
        items = doc('.listlb li a').items()

        for item in items:
            if '行政处罚决定书' in item.attr('title'):
                name = item.attr('title').split('行政处罚决定书')[1]
                name = name.replace('（','').replace('）','')
                if '-' in name:
                    name = name.split('-')[0]

                link = prefix + item.attr('href')
                dataFlag = getDataFromUrl(link,name)
                if dataFlag:
                    break
                # getData(name, prefix + item.attr('href'))






getLinks()


