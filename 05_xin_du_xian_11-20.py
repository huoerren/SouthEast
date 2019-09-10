#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://www.cdepb.gov.cn'

global unfit_urls
unfit_urls = ['http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=851&aid=A4A07BB0346E4B1EB3E0D97D22AF04A7',
              'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=851&aid=18419',
              'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultInfo.aspx?cid=851&aid=9D65572F876441009FA0EB4279EAF189']


def textHandel(text,flag):
    if len(text) != 0:
        if flag == 1:
            return text.replace('\n', '').replace('\r\n','').replace(' ', '').replace('\xa0', '')
        elif flag ==2:
            return text.replace('\r\n', '').replace(' ', '').replace('\xa0', '')
        elif flag == 3:
            return text.replace('\u3000', '')
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
        return data_For_Compare
    except Exception as e:
        print(str(e))
    finally:
        cursor.close()
        conn.close()




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

        # print(link)
        title = textHandel(title.replace(':','：'),1)
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
        Area = '成都-新都区'

        DealUnit = ' 新都区环境保护局'


        pattern1 = re.compile(r'新环连{0,1}罚字{0,1}.\d{4}.\d{0,4}号')

        match1 = pattern1.search(title)
        if match1:
            AdministrativeNumber = match1.group()
        if AdministrativeNumber == '':
            match1 = pattern1.search(content)
            if match1:
                AdministrativeNumber = match1.group()

        # 第一类
        if '被处罚者' in content_02:
            Name = re.search('被处罚者.(.*?)\n',content_02).group(1)

            if '信用代码' in content_02:
                UnifiedSocialCode = re.search('信用代码.(.*?)\n', content_02).group(1)

            if '法定代表人' in content_02:
                Legal = re.search('法定代表人.(.*?)\n', content_02).group(1)
                Legal = textHandel(Legal,3)

            if '违法事实和证据' in content  and '以上事实' in content:
                Category = re.search('违法事实和证据(.*?)以上事实',content).group(1)

            if '行政处罚的依据' in content and '四、陈述申辩' in content:
                According = re.search('行政处罚的依据(.*?)四、陈述申辩', content).group(1)

            if '五、处罚决定' in content and '六、履行方式' in content:
                Measure = re.search('五、处罚决定(.*?)六、履行方式', content).group(1)

            # AdministrativeNumber , UnifiedSocialCode,  Legal  Category   According   Measure
            # print([link, Name, Measure ])

        else:
            # 第二类
            if AdministrativeNumber.strip() != '':
                Name_match = re.search('(.*?)：', content)
                if Name_match:
                    Name = Name_match.group(1)

                if '信用代码：\n' in content_02:
                    UnifiedSocialCode = re.search('信用代码：\n(.*?)\n', content_02).group(1)
                elif '信用代码：' in content_02:
                    UnifiedSocialCode = re.search('信用代码.(.*?)\n', content_02).group(1)

                if '法定代表人（负责人）：\n' in content_02:
                    Legal = re.search('法定代表人（负责人）：\n(.*?)\n', content_02).group(1)
                elif '法定代表人（负责人）：' in content_02:
                    Legal = re.search('法定代表人（负责人）：(.*?)\n', content_02).group(1)

                if '法定代表人：\n' in content_02:
                    Legal = re.search('法定代表人：\n(.*?)\n', content_02).group(1)
                elif '法定代表人：' in content_02:
                    Legal = re.search('法定代表人：(.*?)\n', content_02).group(1)

                if '环境违法行为' in content and '以上事实' in content:
                    Category = re.search('环境违法行为.(.*?)以上事实', content).group(1)

                if '我局决定对你' in content_02:
                    According =  re.search('\n(.*?).我局决定对你', content_02).group(1)
                    if len(According) < 5:
                        According = re.search('依据(.*?).我局决定对你', content).group(1)
                        According = '依据' + According
                elif '故一致' in content and '依据' in content:
                    According = re.search('依据(.*?).故一致', content).group(1)
                    According = '依据' + According

                elif '依据' in content and '决定对你' in content :
                    According = re.search('依据(.*?).决定对你', content).group(1)
                    According = '依据' + According

                if '下行政处罚：' in content and '限于接' in content:
                    Measure = re.search('下行政处罚：(.*?)限于接', content).group(1)
                elif '按日连续处罚：' in content and '限于接' in content:
                    Measure = re.search('按日连续处罚：(.*?)限于接', content).group(1)
                elif '下行政处罚：' in content and '你(单位)如不服' in content:
                    Measure = re.search('下行政处罚：(.*?)你\(单位\)如不服', content).group(1)

                # link , Name , UnifiedSocialCode , Legal  Category   According   Measure

            #第三类
            else:
                # print('----------------  第三类   -----------------')
                if '名称：' in title:
                    Name_x = title.split('名称：')[1]
                    Name = Name_x[0:len(Name_x)-1]
                elif '在生产过程中' in title:
                    Name = title.split('在生产过')[0]
                else:
                    Name = title.replace('关于','').replace('对','').replace('环境','').replace('行政处罚决定书','').replace('行政处罚公告','').replace('行政处罚','')

                Name = Name.replace('）行政处罚公', '')

                if '违法事实' in content_02:
                    Category = re.search('违法事实(.*?)\n' , content_02).group(1)

                if '处罚依据' in content_02:
                    According = re.search('处罚依据(.*?)\n' , content_02).group(1)

                if '处罚内容' in content_02:
                    Measure = re.search('处罚内容(.*?)\n' , content_02).group(1)

                if '决定时间' in content:
                    CreateDate = re.search('决定时间(.*)', content).group(1)
                    CreateDate = CreateDate.replace('年','-').replace('月','-').replace('日','')

                Measure = Measure.replace('：','')
                CreateDate = CreateDate.replace('：','')

                # link , name , Category , According ,Measure ,CreateDate

        dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
        data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

        if dataFromPage in data_For_Compare:
            return True
        else:
            dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area, DealUnit]
            if Name.strip() != '':
                sendDataToDb(dataToDb)


def getLinks():
    for i in range(11,21):
        url = 'http://www.cdepb.gov.cn/cdepbws/Web/Template/GovDefaultList.aspx?cid=851&page='+str(i)
        doc = pq(url, encoding="utf-8")
        # print(doc.text())
        div_items = doc('.ArticleList').items()
        # print(doc('.ArticleList').length)
        for div_item in div_items:
            a = div_item.children('p span:nth-child(2) a:nth-child(2)')
            link = prefix + a.attr('href')
            title= a.attr('title')
            # print([link,title])
            dataFlag = getDataFromUrl(link,title)
            if dataFlag:
                break


getLinks()


