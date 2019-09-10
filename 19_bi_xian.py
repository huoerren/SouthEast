#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://www.cdepb.gov.cn'

global unfit_urls
unfit_urls = ['http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=859&aid=2AFE56425C904EC292CF87391D363994', # 不用录入数据库
              'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=859&aid=275A45DB4E514D1F81570732775760B7', # 不用录入数据库
              'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=859&aid=19518', # 已经录入数据库
              'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=859&aid=19517', # 已经录入数据库
              'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=859&aid=9F7882F767F64C3091AB6397AF6FB4FD', # 已经录入数据库
              'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=859&aid=08099AA83D53457EBEA45E552F713E3E'] # 已经录入数据库

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
        # link = 'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=859&aid=27676'
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
        Area = '成都-郫都区'

        DealUnit = '郫都区环境保护局'

        if '当事人名称或者姓名：\n' in content_02:
            Name = re.search('当事人名称或者姓名：\n(.*?)\n',content_02).group(1)
        elif '当事人：\n' in content_02:
            Name = re.search('当事人：\n(.*?)\n',content_02).group(1)

        if '处罚对象：\n' in content_02:
            match_Name = re.search('处罚对象：\n(.*?)\n',content_02)
            if match_Name:
                Name  = match_Name.group(1)
        elif '被处罚者：\n' in content_02:
            match_Name = re.search('被处罚者：\n(.*?)\n',content_02)
            if match_Name:
                Name  = match_Name.group(1)
        elif '处罚对象' in content_02:
            match_Name = re.search('处罚对象.(.*?)\n',content_02)
            if match_Name:
                Name  = match_Name.group(1)
        elif '被处罚者' in content_02:
            match_Name = re.search('被处罚者.(.*?)\n',content_02)
            if match_Name:
                Name  = match_Name.group(1)

        if '处罚对象，' in content:
            Name = re.search('处罚对象，(.*?)，',content).group(1)

        if Name == '':
            Name = title

        if '主要违法事实' in Name:
            Name = Name.split('主要违法事实')[0]

        Name = Name.replace('行政处罚的公告','').replace('行政处罚公告','').replace('行','')



        # if '文号' in content_02:
        #     match_AdministrativeNumber = re.search('文号.(.*?)\n' ,content_02)
        #     if match_AdministrativeNumber:
        #         AdministrativeNumber = match_AdministrativeNumber.group(1)
        #     else:
        #         match_AdministrativeNumber = re.search('文号.(.*)', content_02)
        #         if match_AdministrativeNumber:
        #             AdministrativeNumber = match_AdministrativeNumber.group(1)
        #
        # elif '文书号' in content_02:
        #     AdministrativeNumber = re.search('文书号.(.*?)\n' ,content_02).group(1)
        # elif '书号' in content_02:
        #     AdministrativeNumber = re.search('书号.(.*?)\n' ,content_02).group(1)
        #
        #

        if '信用代码：\n' in content_02:
            UnifiedSocialCode = re.search('信用代码：\n(.*?)\n' ,content_02).group(1)

        elif '信用代码' in content_02:
            UnifiedSocialCode = re.search('信用代码.(.*?)\n' ,content_02).group(1)

        UnifiedSocialCode  = UnifiedSocialCode.replace('公民身份证号）：', '')


        if '环境违法行为' in content and '以上事实' in content:
            Category = re.search('环境违法行为.(.*?)以上事实' , content).group(1)
        elif '违法事实，' in content:
            Category = re.search('违法事实，(.*?)，', content).group(1)
        elif '违法事实：\n' in content_02:
            Category = re.search('违法事实：\n(.*?)\n', content_02).group(1)
        elif '违法内容：\n' in content_02:
            Category = re.search('违法内容：\n(.*?)\n', content_02).group(1)
        elif '违法内容：' in content_02:
            Category = re.search('违法内容.(.*?)\n', content_02).group(1)
        elif '违法事实：' in content_02:
            Category = re.search('违法事实：(.*?)\n', content_02).group(1)
        elif '经查：' in content and '以上事实' in content:
            Category = re.search('经查：(.*?)以上事实', content).group(1)

        if '依据' in content and '，我局决定对' in content:
            According = re.search('依据(.*?)，我局决定对', content).group(1)
            According = '依据' + According
        elif '依据' in content and ',责令你' in content:
            According = re.search('依据(.*?),责令你', content).group(1)
            According = '依据' + According
        elif '依据：\n' in content_02:
            According = re.search('依据：\n(.*?)\n', content_02).group(1)
        elif '依据：' in content_02:
            According = re.search('依据：(.*?)\n', content_02).group(1)
        elif '处罚依据，' in content:
            According = re.search('处罚依据，(.*?)，', content_02).group(1)
        elif '处罚依据' in content:
            According = re.search('处罚依据(.*?)\n', content_02).group(1)
        elif '根据' in content and '，本局对' in content:
            According = re.search('根据(.*?)，本局对',content)

        if '下行政处罚：' in content and '限于接' in content:
            Measure = re.search('下行政处罚：(.*?)限于接',content).group(1)
        elif '处罚内容：\n' in content_02:
            Measure = re.search('处罚内容：\n(.*?)\n',content_02).group(1)
        elif '处罚内容：' in content_02:
            Measure = re.search('处罚内容.(.*?)\n',content_02).group(1)
        elif '责令你' in content and '上述款项' in content:
            Measure = re.search('责令你(.*?)上述款项',content).group(0)
            Measure = Measure.replace('上述款项','')
        elif '处罚内容，' in content and '，' in content:
            Measure = re.search('处罚内容，(.*?)，',content).group(1)
        elif '处罚的内容：' in content_02 :
            Measure = re.search('处罚的内容：(.*?)\n',content_02).group(1)

        if '处罚时间，' in content  :
            CreateDate = re.search('处罚时间，(.*)', content).group(1)
        elif '时间：\n' in content_02:
            CreateDate = re.search('时间：\n(.*)', content_02).group(1)
        elif '时间：' in content_02:
            CreateDate = re.search('时间：(.*)', content_02).group(1)
        elif '时间：' in content:
            CreateDate = re.search('时间：(.*)', content).group(1)

        CreateDate = CreateDate.replace('年','-').replace('月','-').replace('日','').replace('.','-').replace( '。', '')


        #   LinkUrl, Name, UnifiedSocialCode ，Category， According  Measure  CreateDate
        # print([LinkUrl, Name  ])

        dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
        data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

        if dataFromPage in data_For_Compare:
            return True
        else:
            dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
            if Name.strip() != '':
                sendDataToDb(dataToDb)



def getLinks():
    for i in range(1,26):
        url = 'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultList.aspx?cid=859&page='+ str(i)
        doc = pq(url, encoding="utf-8")
        div_items = doc('.ArticleList').items()
        for div_item in div_items:
            a = div_item.children('p span:nth-child(2) a:nth-child(2)')
            link = prefix + a.attr('href')
            title= a.attr('title')
            if '公示明细表' not in title and '撤销' not in title:
                dataFlag = getDataFromUrl(link,title)
            # if dataFlag:
            #     break


getLinks()


