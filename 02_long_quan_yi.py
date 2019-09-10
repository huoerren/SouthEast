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

def getDataFromUrl(link,name):
    if '龙世江电镀加工坊' in name:
        print([link , name])
    else:

        doc = pq(link, encoding='utf-8')
        content =    textHandel(doc('.ArticleContent').text(),1)
        content_02 = textHandel(doc('.ArticleContent').text(),2)

        if '龙环查字'  not in content and '龙环拘移' not in content and '龙环责停' not in content:
            LinkUrl = link
            Name = name
            Legal = ''

            Category = ''
            According = ''
            Measure = ''

            UnifiedSocialCode = ''
            CreateDate = ''
            AdministrativeNumber = ''
            Area = '成都-龙泉驿区'

            DealUnit = '成都市龙泉驿区环境保护局'


            pattern = re.compile(r'龙环罚字.\d{4}.\w+号')
            match = pattern.search(content)
            if match:
                AdministrativeNumber = match.group()


            # if '法定代表人' in content_02:
            #     match_Legal = re.search('法定代表人.(.*?)；',content_02)
            #     if match_Legal:
            #         Legal = match_Legal.group(1)
            #     else:
            #         Legal = re.search('法定代表人.(.*?)\n',content_02).group(1)


            if '信用代码' in content_02:
                match_UnifiedSocialCode = re.search('信用代码.(.*?)；',content_02)
                if match_UnifiedSocialCode:
                    UnifiedSocialCode = match_UnifiedSocialCode.group(1)
                else:
                    UnifiedSocialCode = re.search('信用代码.(.*?)\n',content_02).group(1)

            UnifiedSocialCode =  UnifiedSocialCode.replace('；', '').replace(';', '')


            pattern3 = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
            if '成都市龙泉驿区环境保护局' in content:
                jieshu = content.split('成都市龙泉驿区环境保护局')[-1]
                if '年' in jieshu and '月' in jieshu and '日' in jieshu:
                    match3 = pattern3.search(jieshu)
                    if match3:
                        CreateDate = match3.group().replace('年', '-').replace('月', '-').replace('日', '')


            if '环境违法行为' in content and '以上事实' in content:
                Category = re.search('环境违法行为(.*?)以上事实', content).group(1)
            elif '调查情况及发现的环境违法事实、证据和陈述申辩及采纳情况' in content and '以上事实' in  content:
                Category = re.search('调查情况及发现的环境违法事实、证据和陈述申辩及采纳情况(.*?)以上事实', content).group(1)

            if Category.strip() == '':
                match4 = pattern3.search(content)
                if match4:
                    Category_time = match4.group()
                    Category = re.search(Category_time + '(.*?)\n',content_02).group(1)
                    Category = Category_time + Category
            Category = Category.replace('：','').replace('。','')


            if '依据' in content and '我局决定' in content:
                According = re.search('依据(.*?)我局决定', content).group(1)
            elif '依据' in content and '我局拟对' in content:
                According = re.search('依据(.*?)我局拟对', content).group(1)
            According = According.replace( '、种类及其履行方式、期限。', '')


            if '下行政处罚：' in content and  '限于' in content:
                Measure = re.search('下行政处罚：(.*?)限于', content).group(1)
            elif '下行政处罚：' in content and  '限期' in content:
                Measure = re.search('下行政处罚：(.*?)限期', content).group(1)



            # link ,      Name  1 ,  Legal  1   , UnifiedSocialCode  1 ,  AdministrativeNumber  1  , CreateDate 1 , Category 1 , According 1 , Measure
            # print([link ,Category ])

            dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
            data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

            if dataFromPage in data_For_Compare:
                return False
            else:
                dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
                if Name.strip() != '':
                    sendDataToDb(dataToDb)




def getLinks():
    for i in range(1,11):
        url = 'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultList.aspx?cid=849&page='+str(i)
        doc = pq(url , encoding='utf-8')
        div_items = doc('.ArticleList').items()
        for div_item in div_items:
            a = div_item.children('p span:nth-child(2) a:nth-child(2)')
            link = prefix + a.attr('href')
            name = a.attr('title')
            if  '关于对'  in a.attr('title'):
                name = name.replace('关于对' , '')
            if '关于' in a.attr('title'):
                name = name.replace('关于', '')
            if '行政处罚的公告' in a.attr('title'):
                name = name.replace('行政处罚的公告', '')
            if '行政处罚公告' in a.attr('title'):
                name = name.replace('行政处罚公告', '')
            if '行政处罚' in a.attr('title'):
                name = name.replace('行政处罚', '')
            dataFlag = getDataFromUrl(link,name)
            if dataFlag:
                break
            # urls.append([prefix + a.attr('href') , name])


getLinks()


