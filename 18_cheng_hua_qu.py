#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://www.cdepb.gov.cn'

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
    if link not in unfit_urls:
        # link = 'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=857&aid=18325'
        # print(link)
        doc = pq(link, encoding='utf-8')
        content =    textHandel(doc('.ArticleContent').text().replace(':','：'),1)
        content_02 = textHandel(doc('.ArticleContent').text().replace(':','：'),2)

        LinkUrl = link
        Name = ''
        Legal = ''

        Category = ''
        According = ''
        Measure = ''

        UnifiedSocialCode = ''
        CreateDate = ''
        AdministrativeNumber = ''
        Area = '成都-成华区'

        DealUnit = '成华区环境保护局'


        if '企业名称：\n' in content_02:
            match_Name = re.search('企业名称：\n(.*?)\n', content_02)
            if match_Name:
                Name = match_Name.group(1)
        elif '处罚对象：\n' in content_02:
            match_Name = re.search('处罚对象：\n(.*?)\n',content_02)
            if match_Name:
                Name  = match_Name.group(1)
        elif '企业名称' in content_02:
            match_Name = re.search('企业名称.(.*?)\n', content_02)
            if match_Name:
                Name = match_Name.group(1)
        elif '处罚对象' in content_02:
            match_Name = re.search('处罚对象.(.*?)\n',content_02)
            if match_Name:
                Name  = match_Name.group(1)

        elif Name.strip() == '':
            if '行政处罚' in doc('.ArticleTitle').text():
                Name = doc('.ArticleTitle').text().split('行政处罚')[0].replace('对', '')
            else:
                Name = doc('.ArticleTitle').text()


        if '文号' in content_02:
            match_AdministrativeNumber = re.search('文号.(.*?)\n' ,content_02)
            if match_AdministrativeNumber:
                AdministrativeNumber = match_AdministrativeNumber.group(1)
            else:
                match_AdministrativeNumber = re.search('文号.(.*)', content_02)
                if match_AdministrativeNumber:
                    AdministrativeNumber = match_AdministrativeNumber.group(1)

        elif '文书号' in content_02:
            AdministrativeNumber = re.search('文书号.(.*?)\n' ,content_02).group(1)
        elif '书号' in content_02:
            AdministrativeNumber = re.search('书号.(.*?)\n' ,content_02).group(1)


        if '信用代码或工商营业执照（身份证号）' in content_02:
            UnifiedSocialCode = re.search('信用代码或工商营业执照（身份证号）.(.*?)\n' ,content_02).group(1)
        elif '信用代码（或营业执照）' in content_02:
            UnifiedSocialCode = re.search('信用代码（或营业执照）.(.*?)\n' ,content_02).group(1)
        elif '信用代码' in content_02:
            UnifiedSocialCode = re.search('信用代码.(.*?)\n' ,content_02).group(1)


        if '时间：\n' in content_02:
            match_CreateDate = re.search('时间：\n(.*?)\n', content_02)
            match_CreateDate02 = re.search('时间：\n(.*)', content_02)
            if match_CreateDate:
                CreateDate = match_CreateDate.group(1)
            elif match_CreateDate02:
                CreateDate = match_CreateDate02.group(1)
        elif '时间' in content_02:
            match_CreateDate = re.search('时间.(.*?)\n', content_02)
            if match_CreateDate:
                CreateDate = match_CreateDate.group(1)
            else:
                createDate_text  = content.split('时间')[1]
                pattern = re.compile(r'\d{4}.\d{0,2}.\d{0,2}.')
                match_Create = pattern.search(createDate_text)
                if match_Create:
                    CreateDate = match_Create.group()
        CreateDate = CreateDate.replace('年','-').replace('月','-').replace('日','')


        if '违法行为：\n' in content_02:
            Category = re.search('违法行为：\n(.*?)\n', content_02).group(1)
        elif '事由：\n' in content_02:
            Category = re.search('事由：\n(.*?)\n', content_02).group(1)
        elif '事实：\n' in content_02:
            Category = re.search('事实：\n(.*?)\n', content_02).group(1)

        elif '违法行为：' in content_02:
            Category = re.search('违法行为：(.*?)\n', content_02).group(1)
        elif '事由：' in content_02:
            Category = re.search('事由：(.*?)\n', content_02).group(1)
        elif '事实：' in content_02:
            Category = re.search('事实：(.*?)\n', content_02).group(1)



        if '依据：\n' in content_02:
            According = re.search('依据：\n(.*?)\n', content_02).group(1)
        elif '依据\n' in content_02:
            According = re.search('依据\n(.*?)\n', content_02).group(1)
        elif '依据：《\n' in content_02:
            According = re.search('依据：《\n(.*?)\n', content_02).group(1)
            According = "《"+ According
        elif '依据' in content_02:
            According = re.search('依据.(.*?)\n', content_02).group(1)



        if '金额：\n' in content_02:
            Measure = re.search('金额：\n(.*?)\n', content_02).group(1)
        elif '行政处罚：\n' in content_02:
            match_Measure = re.search('行政处罚：\n(.*?)\n', content_02)
            if match_Measure:
                Measure = match_Measure.group(1)
        elif '处罚内容：\n' in content_02:
            match_Measure = re.search('处罚内容：\n(.*?)\n', content_02)
            if match_Measure:
                Measure = match_Measure.group(1)

        elif '金额：' in content_02:
            match_Measure = re.search('金额：(.*?)\n', content_02)
            if match_Measure:
                Measure = match_Measure.group(1)
        elif '行政处罚：' in content_02:
            match_Measure = re.search('行政处罚：(.*?)\n', content_02)
            if match_Measure:
                Measure = match_Measure.group(1)
        elif '处罚内容：' in content_02:
            match_Measure = re.search('处罚内容：(.*?)\n', content_02)
            if match_Measure:
                Measure = match_Measure.group(1)



        #  UnifiedSocialCode  AdministrativeNumber CreateDate   |
        # print([LinkUrl, Name, Category , According, Measure ,CreateDate, UnifiedSocialCode ,AdministrativeNumber ])

        dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
        data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

        if dataFromPage in data_For_Compare:
            return False
        else:
            dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
            if Name.strip() != '':
                sendDataToDb(dataToDb)



def getLinks():
    for i in range(1,12):
        url = 'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultList.aspx?cid=848&page='+ str(i)
        doc = pq(url , encoding='utf-8')
        div_items = doc('.ArticleList').items()
        for div_item in div_items:
            a = div_item.children('p span:nth-child(2) a:nth-child(2)')
            link = prefix + a.attr('href')
            title= a.attr('title')
            if '查封' not in title:
                dataFlag = getDataFromUrl(link,title)
                if dataFlag:
                    break


getLinks()


