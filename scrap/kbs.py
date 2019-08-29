"""
KBS 프로그램 수집
"""

import requests
import re
import json
from datetime import datetime, timedelta
from dateutil.parser import parse
import time


REFER = 'http://news.kbs.co.kr'

param_a = {
    'SEARCH_SECTION': '0001', 
    'SEARCH_CATEGORY': '0001',
    'CURRENT_PAGE_NO': 1,
    'ROW_PER_PAGE': 12,
    'SEARCH_MODE': 'listBySisa',
    'SEARCH_DATE_TYPE': 'TERM',
    'SEARCH_DATE': '',
    'SEARCH_BROAD_CODE': '',
    'SEARCH_MENU_CODE': '0758',
    'SEARCH_SPECIAL_YN': '', 
    'SEARCH_AWARD_YN': '',
    'SEARCH_QUICKLY_YN': '',
    'SEARCH_PREVIEW_YN': 'Y'
}

param_b = {
    'page_size': 1
}

bbs_id = {
    '추적 60분': 'T2000-0088-04-907289', 
    'KBS 스페셜': 'T2016-0065-04-622234', 
    '제보자들': 'T2016-0629-04-741959', 
    '특파원 보고 세계는 지금': 'T2016-0337-04-12370', 
    '세상의 모든 다큐': 'T2011-0923-04-569614'
}


# 함수: 세션생성
def sess(refer):
    AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    s = requests.Session()
    s.headers.update({'User-Agent': AGENT, 'Referer': refer})
    return s

# 함수: 다음 요일 찾기
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)


def scrap(prog_name, URL, original_air_date, week):
    s = sess(REFER)
    if prog_name == '시사기획 창':
        resp = s.post(URL, data=param_a)
        content_info = json.loads(resp.text)['page_list'][0]
        title =  content_info['NEWS_TITLE'].split(' : ')[1]
        air_num = content_info['NEWS_CODE']
        preview_img = REFER + content_info['NEWS_IMG_URL']
        preview_mov = REFER + content_info['NEWS_VOD_URL'].replace('|N|Y|N|', '')
        description = ''
        regdate_tmp = re.search(r"[0-9]{4}\.[0-9]{2}\.[0-9]{2}", content_info['NEWS_REG_DATE']).group()
    elif prog_name in ['추적 60분', 'KBS 스페셜', '제보자들', '특파원 보고 세계는 지금', '세상의 모든 다큐']:
        param_b['bbs_id'] = bbs_id[prog_name]
        resp = s.get(URL, params=param_b)
        #print(resp.text)
        content_info = json.loads(resp.text)['data'][0]
        title = content_info['title'].split(' / ')[0]
        air_num = content_info['id']
        preview_img_tmp = content_info['post_cont_image']
        if preview_img_tmp is None:
            preview_img = ''
        else:    
            preview_img = json.loads(preview_img_tmp)[0]
        preview_mov = ''
        description = content_info['description']
        if prog_name != '세상의 모든 다큐':
            regdate_tmp = content_info['rdatetime'].split()[0]
        else:
            regdate_tmp = title.replace('년', '-').replace('월', '-').replace('일', '').split()[:3]
            regdate_tmp = ''.join(regdate_tmp)
    
    regdate = parse(regdate_tmp).date()
    air_date = str(next_weekday(regdate, week.index(original_air_date[0])))
    
    result = {
        'air_date': air_date, 
        'air_num': air_num, 
        'title': title, 
        'preview_img': preview_img, 
        'preview_mov': preview_mov, 
        'description': description
    }
    
    return [result]
