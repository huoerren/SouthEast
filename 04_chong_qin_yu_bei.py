#coding=utf-8

import requests
import re
from pyquery import PyQuery as pq
import pymysql

global prefix
prefix = 'http://www.cepb.gov.cn'

global unfit_urls
unfit_urls = [] # http://www.cqdzhbj.gov.cn/viewcontent.jsp?faid=48&soid=68&id=1623


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
    content_obj = doc('#Zoom')
    content =    textHandel(content_obj.text() ,1)
    content_02 = textHandel(content_obj.text() ,2)

    content_02_new = textHandel(content_obj.text() ,1)

    if '被处罚个人' not in content and '被处罚人' not in content:
        LinkUrl = link
        Name = ''
        Legal = ''

        Category = ''
        According = ''
        Measure = ''

        UnifiedSocialCode = ''
        CreateDate = ''
        AdministrativeNumber = ''
        Area = '重庆-渝北区'

        DealUnit = ''


        pattern = re.compile(r'渝环（两江）罚字.\d{4}.\d{0,3}号')
        match = pattern.search(content)
        if match:
            AdministrativeNumber = match.group()

        if '被处罚单位' in content_02 :
            Name = re.search( '被处罚单位.(.*?)\n', content_02).group(1)
        if Name.strip('') == '':
            content_02 = content_02.replace('被处罚单位：\n','被处罚单位：')
            if '被处罚单位' in content_02:
                Name = re.search('被处罚单位.(.*?)\n', content_02).group(1)
            elif '名称' in content_02:
                Name = re.search('名称.(.*?)\n', content_02).group(1)
            elif '被处罚经营户' in content_02:
                Name = re.search('被处罚经营户.(.*?)\n', content_02).group(1)


        if '法定代表人' in content_02_new:
            Legal_match = re.search( '法定代表人.(.*?)统一社会信用代码', content_02_new)
            if Legal_match:
                Legal = Legal_match.group(1)

        if '信用代码号' in content_02_new and '地址' in content_02_new :
            UnifiedSocialCode_match = re.search('信用代码号.(.*?)地址' ,content_02_new)
            if UnifiedSocialCode_match:
                UnifiedSocialCode = UnifiedSocialCode_match.group(1)
        elif '信用代码' in content_02_new  and '地址' in content_02_new  :
            UnifiedSocialCode_match = re.search('信用代码.(.*?)地址', content_02_new)
            if UnifiedSocialCode_match:
                UnifiedSocialCode = UnifiedSocialCode_match.group(1)


        pattern2 = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
        if '重庆市环境保护局两江新区分局' in content:
            jieshu = content.split('重庆市环境保护局两江新区分局')[-1]
            if '年' in jieshu and '月' in jieshu and '日' in jieshu:
                match2 = pattern2.search(jieshu)
                if match2:
                    CreateDate = match2.group().replace('年', '-').replace('月', '-').replace('日', '')

        if '环境违法事实、证据和陈述申辩（听证）意见、采纳情况及裁量理由' in content and '，属于' in content:
            Category = re.search('环境违法事实、证据和陈述申辩（听证）意见、采纳情况及裁量理由(.*?)，属于', content).group(1)
        elif '环境违法事实、证据和陈述申辩（听证）意见、采纳情况及裁量理由' in content and '上述行为' in  content:
            Category = re.search('环境违法事实、证据和陈述申辩（听证）意见、采纳情况及裁量理由(.*?)上述行为', content).group(1)
            Category = Category.replace(Name ,'')

        #
        if '行政处罚的依据、种类及其履行方式、期限' in content and '重庆市环境保护局两江新区分局决定' in content:
            According = re.search('行政处罚的依据、种类及其履行方式、期限(.*?)重庆市环境保护局两江新区分局决定', content).group(1)
        #
        if '下行政处罚：' in content and  '罚款限' in content:
            Measure = re.search('下行政处罚：(.*?)罚款限', content).group(1)
        elif '行政处罚如下：' in content and '罚款限' in content:
            Measure = re.search('行政处罚如下：(.*?)罚款限', content).group(1)
        elif '行政处罚：' in content and '罚款限' in content:
            Measure = re.search('行政处罚：(.*?)罚款限' ,content ).group(1)
        elif '从重处罚：' in content and '罚款限' in content:
            Measure = re.search('从重处罚：(.*?)罚款限' ,content ).group(1)



        # link , Name ,Legal , UnifiedSocialCode ,AdministrativeNumber  , CreateDate , Category , According , Measure
        # print([link , Name ,Measure   ])

        dataFromPage = [Name, Category, According, Measure, CreateDate, Area]
        data_For_Compare = getDataExisted(Area)  # 获得最新的本地域的 已经存在的 数据

        if dataFromPage in data_For_Compare:
            return False
        else:
            dataToDb = [LinkUrl, Name, Legal, CreateDate, Category, According, Measure, AdministrativeNumber, UnifiedSocialCode, Area ,DealUnit]
            print(dataToDb)
            # if Name.strip() != '':
            #     sendDataToDb(dataToDb)




def getLinks():
    for i in range(1,6):
        if i ==1 :
            url = 'http://www.cepb.gov.cn/xxgk/jggk/jgjs/zsfj/zqshjbhjljxqfj/fzxc/index.shtml'
        else:
            url = 'http://www.cepb.gov.cn/xxgk/jggk/jgjs/zsfj/zqshjbhjljxqfj/fzxc/index_'+str(i)+'.shtml'

        doc = pq(url, encoding="utf-8")
        items = doc('.List_list.font14 li a').items()
        for item in items:
            if '行政处罚决定书' in item.attr('title'):
                href = item.attr('href')
                link = prefix + href
                dataFlag = getDataFromUrl(link)
                # if dataFlag:
                #     break


getLinks()


