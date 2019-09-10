#coding=utf-8


import pymysql
from pyquery import PyQuery as pq
import re
import requests



def textHandel(text,flag):
    if len(text) != 0:
        if flag == 1:
            return text.replace('\n', '').replace('\r\n','').replace(' ', '').replace('\xa0', '')
        elif flag ==2:
            return text.replace('\r\n', '').replace(' ', '').replace('\xa0', '')
    else:
        return ''



def getDataFromUrl(link):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    resp = requests.get(link)
    resp.encoding = 'utf-8'
    doc = pq(resp.text)
    content_1 = doc('.content_1')

    content_1_text = textHandel(doc('.content_1').text(),1)
    content_2_text = textHandel(doc('.content_1').text(),2)

    title = textHandel(doc('.title').text(),1)

    table = content_1.find('table')

    print([table.length , link])

    # if '行政处罚' in title or '行政处罚' in content_1:
    #     print([link])



def getLinks():
    for i in range(0,3):
        if i == 0:
            url = 'http://www.gaxq.gov.cn/zwgk/xxgkml/zdlygk/hjbh_43848/wgcl/list.html'
        else:
            url = 'http://www.gaxq.gov.cn/zwgk/xxgkml/zdlygk/hjbh_43848/wgcl/list_'+str(i)+'.html'

        headers = {
            'Cookie':'Secure; UM_distinctid=165184dbcc46ef-02ef13adb564f-47e1039-144000-165184dbcc56dd; CNZZDATA1254539845=1528874566-1533710196-%7C1533710196; yfx_c_g_u_id_10000789=_ck18080814511215578618159885461; _trs_uv=jkks3ufp_1002_emyj; _trs_ua_s_1=jkks3ufp_1002_3kni; yfx_f_l_v_t_10000789=f_t_1533711072541__r_t_1533711072541__v_t_1533713865267__r_c_0',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }
        resp = requests.get(url, headers=headers)
        resp.encoding = 'utf-8'
        doc = pq(resp.text)
        trs = doc('#data').children('tr')
        for tr in trs.items():
            a = tr.children('td').children('h1').children('a')
            link =  a.attr('href')
            dataFlag = getDataFromUrl(link)



getLinks()














