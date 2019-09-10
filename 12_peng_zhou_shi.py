#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global unfit_urls
unfit_urls = ['http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=854&aid=27725',
              'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=854&aid=0C91F94D656C4A85A4BD353DB2C48B6C',
              'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=854&aid=C0E3267D881E4B28A6283CD8CD9106CB',
              'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=854&aid=0069A09285A044788F01388F7C4EBC0C',
              'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=854&aid=02C6279410C54559805127929CA9D532',
              'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=854&aid=5367889DADAC4B28B50DFFE8C1057139',
              'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=854&aid=27741',
              'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=854&aid=27734']

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

def getDataFromUrl(link,title):
    # link = 'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=854&aid=27725'
    if link not in unfit_urls:
        # link = 'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=854&aid=BAB6AF1D145647F9BB7A2D4037B153C4'
        # print(link)
        doc = pq(link, encoding='utf-8')
        title = textHandel(doc('.ArticleTitle').text() ,1)
        if '查封' not in title:
            trs = doc('.ArticleContent').children('span').children('table').children('tbody').children('tr')
            if trs.length >0 :
                for tr in trs.items():
                    if '行政处罚对象' not in  tr.text():
                        LinkUrl = link
                        Name = ''
                        Legal = ''

                        Category = ''
                        According = ''
                        Measure = ''

                        UnifiedSocialCode = ''
                        CreateDate = ''
                        AdministrativeNumber = ''
                        Area = '成都-彭州市'

                        DealUnit = '彭州市环境保护局'

                        table_val = []
                        for td in tr.children('td').items():
                            table_val.append(textHandel(td.text() ,1))

                        if len(table_val) == 5:
                            Name = table_val[0]
                            Category = table_val[1]
                            According = table_val[2]
                            Measure   = table_val[3]
                            CreateDate= table_val[4].replace('年','-').replace('月','-').replace('日','').replace('.', '-').replace('/','-')

                            dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
                            # print(dataFromPage)
                            data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

                            if dataFromPage in data_For_Compare:
                                return False
                            else:
                                dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
                                if Name.strip() != '':
                                    sendDataToDb(dataToDb)


                        elif len(table_val) == 6:
                            Name =  table_val[0]
                            Category = table_val[1]
                            According = table_val[2]
                            Measure = table_val[3]
                            AdministrativeNumber = table_val[4]
                            CreateDate = table_val[5].replace('年','-').replace('月','-').replace('日','').replace('.', '-').replace('/','-')

                            dataFromPage = [Name, Category, According, Measure, CreateDate, Area ]
                            # print(dataFromPage)
                            data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

                            if dataFromPage in data_For_Compare:
                                return False
                            else:
                                dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
                                if Name.strip() != '':
                                    sendDataToDb(dataToDb)


                        elif len(table_val) == 9:
                            Name = table_val[1]
                            Category = table_val[2]
                            According = table_val[4]
                            Measure = table_val[5]
                            AdministrativeNumber = table_val[6]
                            CreateDate = table_val[7].replace('年','-').replace('月','-').replace('日','').replace('.', '-').replace('/','-')

                            dataFromPage = [Name, Category, According, Measure, CreateDate, Area ]
                            # print(dataFromPage)
                            data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

                            if dataFromPage in data_For_Compare:
                                return False
                            else:
                                dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
                                if Name.strip() != '':
                                    sendDataToDb(dataToDb)

            else:
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
                Area = '成都-彭州市'

                DealUnit = '彭州市环境保护局'

                if '对象：\n' in content_02:
                    match_Name = re.search('对象：\n(.*?)\n', content_02)
                    if match_Name:
                        Name = match_Name.group(1)
                elif '对象' in content_02:
                    match_Name = re.search('对象.(.*?)\n',content_02)
                    if match_Name:
                        Name  = match_Name.group(1)
                if Name.strip() == '':
                    Name = doc('.ArticleTitle').text().split('行政处罚')[0].replace('关于对', '')


                if '文号' in content_02:
                    AdministrativeNumber = re.search('文号.(.*?)\n' ,content_02).group(1)


                # if '信用代码或工商营业执照（身份证号）' in content_02:
                #     UnifiedSocialCode = re.search('信用代码或工商营业执照（身份证号）.(.*?)\n' ,content_02).group(1)
                # elif '信用代码（或营业执照）' in content_02:
                #     UnifiedSocialCode = re.search('信用代码（或营业执照）.(.*?)\n' ,content_02).group(1)
                # elif '信用代码' in content_02:
                #     UnifiedSocialCode = re.search('信用代码.(.*?)\n' ,content_02).group(1)


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
                CreateDate = CreateDate.replace('年','-').replace('月','-').replace('日','').replace('.','-').replace('/','-')


                if '事实：\n' in content_02:
                    Category = re.search('事实：\n(.*?)\n', content_02).group(1)
                elif '案由：\n' in content_02:
                    Category = re.search('事实：\n(.*?)\n', content_02).group(1)
                elif '行为：\n' in content_02:
                    Category = re.search('事实：\n(.*?)\n', content_02).group(1)
                elif '事实' in content_02:
                    Category = re.search('事实.(.*?)\n', content_02).group(1)
                elif '案由' in content_02:
                    Category = re.search('案由.(.*?)\n', content_02).group(1)
                elif '行为' in content_02:
                    Category = re.search('行为.(.*?)\n', content_02).group(1)


                if '依据：\n' in content_02:
                    According = re.search('依据：\n(.*?)\n', content_02).group(1)
                elif '依据' in content_02:
                    According = re.search('依据.(.*?)\n', content_02).group(1)
                elif '情形：\n' in content_02:
                    According = re.search('情形：\n(.*?)\n', content_02).group(1)
                elif '情形' in content_02:
                    According = re.search('情形.(.*?)\n', content_02).group(1)


                if '金额：\n' in content_02:
                    Measure = re.search('金额：\n(.*?)\n', content_02).group(1)
                elif '内容：\n' in content_02:
                    Measure = re.search('内容：\n(.*?)\n', content_02).group(1)
                elif '处罚决定：\n' in content_02:
                    Measure = re.search('处罚决定：\n(.*?)\n', content_02).group(1)
                elif '措施：\n' in content_02:
                    Measure = re.search('措施：\n(.*?)\n', content_02).group(1)

                elif '金额' in content_02:
                    Measure = re.search('金额.(.*?)\n', content_02).group(1)
                elif '内容' in content_02:
                    Measure = re.search('内容.(.*?)\n', content_02).group(1)
                elif '处罚决定：' in content_02:
                    Measure = re.search('处罚决定.(.*?)\n', content_02).group(1)
                elif '措施' in content_02:
                    Measure = re.search('措施.(.*?)\n', content_02).group(1)


                dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
                data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

                if dataFromPage in data_For_Compare:
                    return False
                else:
                    dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
                    if Name.strip() != '':
                        sendDataToDb(dataToDb)



def getLinks():
    for i in range(1,27):
        url = 'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultList.aspx?cid=854&page='+ str(i)
        doc = pq(url, encoding="utf-8")
        div_items = doc('.ArticleList').items()
        for div_item in div_items:
            a = div_item.children('p span:nth-child(2) a:nth-child(2)')
            link = prefix + a.attr('href')
            title= a.attr('title')
            # print([link ,title])
            dataFlag = getDataFromUrl(link,title)
            if dataFlag:
                break


getLinks()


