#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql
import datetime

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


# def textValue():
#     dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
#     data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据
#
#     if dataFromPage in data_For_Compare:
#         return False
#     else:
#         dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
#         if Name.strip() != '':
#             sendDataToDb(dataToDb)



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


def getName_Category_date(content):
    val = ['', '', '']
    content = textHandel(content ,1)
    if len(textHandel(content ,1)) >0:
        pattern = re.compile(r'\d{4}年\d{0,2}月\d{0,2}日{0,1}')
        match = pattern.search(content)
        if match:
            CreateDate = match.group()
            val = [content.split(CreateDate)[0].replace('当事人','').replace('于','') , content.split(CreateDate)[1] ,CreateDate.replace('年', '-').replace('月', '-').replace('日', '')]

    return val


def getDataFromUrl(link,title):
        doc = pq(link, encoding='utf-8')
        div_content = doc('.ArticleContent')

        content =    textHandel(doc('.ArticleContent').text().replace(':','：'),1)
        content_02 = textHandel(doc('.ArticleContent').text().replace(':','：'),2)

        tables = div_content.find('table.MsoTableGrid')
        if tables.length == 0:
            tables = div_content.find('table.MsoNormalTable')
        if tables.length >0:
            for table in tables.items():
                trs = table.children('tbody').children('tr')
                for tr in trs.items():
                    if tr.children('td').length > 5 and ('序号' not in tr.text()) :
                        table_val = []
                        for td in tr.children('td').items():
                            table_val.append(textHandel(td.text() ,1))

                        LinkUrl = link
                        Name = ''
                        Legal = ''

                        Category = ''
                        According = ''
                        Measure = ''

                        UnifiedSocialCode = ''
                        CreateDate = ''
                        AdministrativeNumber = ''
                        Area = '成都-青羊区'

                        DealUnit = '青羊区环境保护局'

                        if len(table_val) == 7 :
                            values = getName_Category_date(table_val[2])
                            LinkUrl = link
                            Name = values[0]
                            Category = values[1]
                            According = table_val[3]
                            Measure = table_val[5]
                            CreateDate = values[2]
                            AdministrativeNumber = table_val[1]

                            dataFromPage = [Name, Category, According, Measure, CreateDate, Area ]
                            data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

                            if dataFromPage in data_For_Compare:
                                return False
                            else:
                                dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area, DealUnit]
                                if Name.strip() != '':
                                    sendDataToDb(dataToDb)

                        if len(table_val) == 9 :
                            LinkUrl = link
                            Name =       table_val[1]
                            Category =   table_val[2]
                            According =  table_val[4]
                            Measure =    table_val[5]
                            CreateDate = table_val[6].replace('年', '-').replace('月', '-').replace('日', '')
                            AdministrativeNumber =  table_val[7]

                            dataFromPage = [Name, Category, According, Measure, CreateDate, Area ]
                            data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

                            if dataFromPage in data_For_Compare:
                                return False
                            else:
                                dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area, DealUnit]
                                if Name.strip() != '':
                                    sendDataToDb(dataToDb)

                        if len(table_val) == 10 :

                            LinkUrl = link
                            Name = table_val[1]
                            Category = table_val[4]
                            According = table_val[5]
                            Measure = table_val[7]
                            CreateDate = table_val[8].replace('.','-')
                            AdministrativeNumber = table_val[6]

                            dataFromPage = [Name, Category, According, Measure, CreateDate, Area ]
                            data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

                            if dataFromPage in data_For_Compare:
                                return False
                            else:
                                dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area, DealUnit]
                                if Name.strip() != '':
                                    sendDataToDb(dataToDb)

        else:
            LinkUrl = link
            Name = ''
            Legal = ''

            Category = ''
            According = ''
            Measure = ''

            UnifiedSocialCode = ''
            CreateDate = ''
            AdministrativeNumber = ''
            Area = '成都-青羊区'

            DealUnit = '青羊区环境保护局'

            if '对象：\n' in content_02:
                match_Name = re.search('对象：\n(.*?)\n', content_02)
                if match_Name:
                    Name = match_Name.group(1)
            elif '对象' in content_02:
                match_Name = re.search('对象.(.*?)\n',content_02)
                if match_Name:
                    Name  = match_Name.group(1)

            if '文号' in content_02:
                AdministrativeNumber = re.search('文号.(.*?)\n' ,content_02).group(1)


            # if '信用代码（营业执照）' in content_02:
            #     UnifiedSocialCode = re.search('信用代码（营业执照）.(.*?)\n' ,content_02).group(1)
            # elif '信用代码（或营业执照）' in content_02:
            #     UnifiedSocialCode = re.search('信用代码（或营业执照）.(.*?)\n' ,content_02).group(1)
            # elif '信用代码' in content_02:
            #     UnifiedSocialCode = re.search('信用代码.(.*?)\n' ,content_02).group(1)
            #
            #
            if '时间' in content:
                CreateDate = content.split('时间')[1].replace('：','').replace('.','-').replace('/','-').replace('年','-').replace('月','-').replace('日','')

            #
            if '事实：\n' in content_02:
                Category = re.search('事实：\n(.*?)\n', content_02).group(1)
            elif '案由：\n' in content_02:
                Category = re.search('案由：\n(.*?)\n', content_02).group(1)
            elif '行为：\n' in content_02:
                Category = re.search('行为：\n(.*?)\n', content_02).group(1)
            elif '情况：\n' in content_02:
                Category = re.search('情况：\n(.*?)\n', content_02).group(1)
            elif '事实' in content_02:
                Category = re.search('事实.(.*?)\n', content_02).group(1)
            elif '案由' in content_02:
                Category = re.search('案由.(.*?)\n', content_02).group(1)
            elif '行为' in content_02:
                Category = re.search('行为.(.*?)\n', content_02).group(1)
            elif '情况' in content_02:
                Category = re.search('情况.(.*?)\n', content_02).group(1)
            #
            #
            if '依据：\n' in content_02:
                According = re.search('依据：\n(.*?)\n', content_02).group(1)
            elif '依据' in content_02:
                According = re.search('依据.(.*?)\n', content_02).group(1)
            elif '条款：\n' in content_02:
                According = re.search('条款：\n(.*?)\n', content_02).group(1)
            elif '条款' in content_02:
                According = re.search('条款.(.*?)\n', content_02).group(1)

            #
            if '金额：\n' in content_02:
                Measure = re.search('金额：\n(.*?)\n', content_02).group(1)
            elif '内容：\n' in content_02:
                Measure = re.search('内容：\n(.*?)\n', content_02).group(1)
            elif '处罚决定：\n' in content_02:
                Measure = re.search('处罚决定：\n(.*?)\n', content_02).group(1)
            elif '金额' in content_02:
                Measure = re.search('金额.(.*?)\n', content_02).group(1)
            elif '内容' in content_02:
                Measure = re.search('内容.(.*?)\n', content_02).group(1)
            elif '处罚决定：' in content_02:
                Measure = re.search('处罚决定：(.*?)\n', content_02).group(1)


            # link , Name    ,Legal 2 , UnifiedSocialCode 2 ,AdministrativeNumber 2 , CreateDate 2, Category  , According  , Measure
            # print([link,Name,Category, According , Measure ,CreateDate])


            dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
            data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据
            if dataFromPage in data_For_Compare:
                return False
            else:
                dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
                if Name.strip() != '':
                    sendDataToDb(dataToDb)




def getLinks():
    for i in range(1,6):
        j = str(i)
        url = 'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultList.aspx?cid=845&page='+j
        doc = pq(url , encoding='utf-8')
        div_items = doc('.ArticleList').items()
        for div_item in div_items:
            a = div_item.children('p span:nth-child(2) a:nth-child(2)')
            link = prefix + a.attr('href')
            title= a.attr('title')
            # print([link , title])
            dataFlag = getDataFromUrl(link,title)
            if dataFlag:
                break


getLinks()


# def getTime():
#     t1 = datetime.datetime(2017, 3, 5, 8, 49, 0)
#     t2 = datetime.datetime(2017, 3, 5, 8, 50, 0)
#
#     print((t2-t1).total_seconds()/60)
#
# getTime()