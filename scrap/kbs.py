"""
KBS 프로그램 수집
"""

import requests
import re
import json
from datetime import datetime, timedelta
from dateutil.parser import parse
import time
from scrap import utils


REFER = 'http://news.kbs.co.kr'

PARAM_A = {
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

PARAM_B = {
    'page_size': 1
}

BBS_URL = 'http://pbbsapi.kbs.co.kr/board/v1/list'
BBS_ID = {
    '추적 60분': 'T2000-0088-04-907289', 
    'KBS 스페셜': 'T2016-0065-04-622234', 
    '제보자들': 'T2016-0629-04-741959', 
    '특파원 보고 세계는 지금': 'T2016-0337-04-12370', 
    '세상의 모든 다큐': 'T2011-0923-04-569614', 
    '다큐 인사이트': 'T2019-0296-04-850025', 
    '시사기획 창': 'T2011-1097-04-968945'
}

BTV_CON_ID = {
    '제보자들': '{C18F4D30-81E7-4187-B03C-CF81083D46E1}', 
    '시사기획 창': '{10D376EB-3EE8-4576-AEB4-05094068615A}'
}

# 함수: 다음 요일 찾기
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)


def scrap(prog_name, url, original_air_date, week):
    s = utils.sess(REFER)
    if prog_name == '시사기획 창':
        url = 'http://news.kbs.co.kr/news/getNewsPage.do'
        resp = s.post(url, data=PARAM_A)
        content_info = json.loads(resp.text)['page_list'][0]
        title =  content_info['NEWS_TITLE'].split(' : ')[1]
        air_num = content_info['NEWS_CODE']
        preview_img = REFER + content_info['NEWS_IMG_URL']
        preview_mov = REFER + content_info['NEWS_VOD_URL'].replace('|N|Y|N|', '')
        description = ''
        regdate_tmp = re.search(r"[0-9]{4}\.[0-9]{2}\.[0-9]{2}", content_info['NEWS_REG_DATE']).group()
    else:
        PARAM_B['bbs_id'] = BBS_ID[prog_name]
        resp = s.get(BBS_URL, params=PARAM_B) # 공통 URL 사용
        #print(resp.text)
        content_info = json.loads(resp.text)['data'][0]
        title = content_info['title'].split('/')[0].strip()
        air_num = content_info['post_no']
        preview_img_tmp = content_info['post_cont_image']
        if preview_img_tmp is None:
            preview_img = ''
        else:    
            preview_img = json.loads(preview_img_tmp)[0]
        preview_mov = ''
        description = content_info['description']
        # 디스크립션 수정
        if prog_name == '제보자들':
            # air number, title 수정
            air_num = title.replace("회", "")
            title = ''
            if re.compile(r".+첫 번째 이야기").search(content_info['description']) is not None:
                front_padding = re.compile(r"(.+)첫 번째 이야기").search(content_info['description']).group(1)
                description = content_info['description'].replace(front_padding, "")
        elif prog_name == '특파원 보고 세계는 지금':
            if re.compile(r"^.+내용■ ").search(content_info['description']) is not None:
                front_padding = re.compile(r"^(.+내용■ )").search(content_info['description']).group(1)
                description = content_info['description'].replace(front_padding, "")
            if re.compile(r"^.+회■ ").search(content_info['description']) is not None:
                front_padding = re.compile(r"^(.+회■ )").search(content_info['description']).group(1)
                description = content_info['description'].replace(front_padding, "")
        # 등록일 처리
        if prog_name != '세상의 모든 다큐':
            regdate_tmp = content_info['rdatetime'].split()[0]
        else:
            regdate_tmp = title.replace('년', '-').replace('월', '-').replace('일', '').split()[:3]
            regdate_tmp = ''.join(regdate_tmp)
    
    regdate = parse(regdate_tmp).date()
    air_date = str(next_weekday(regdate, week.index(original_air_date[0])))
    if prog_name == '시사기획 창':
        # sk BTV 정보 보완
        btv_info = utils.get_btv_info(BTV_CON_ID[prog_name])
        if btv_info:
            try:
                air_date_check = re.search(r'\d{2}\.\d{2}\.\d{2}', btv_info['content']['s_title']).group()
            except:
                pass
            if air_date_check and (air_date == str(parse('20' + air_date_check).date())):
                description = btv_info['content']['c_desc']
    
    result = {
        'air_date': air_date, 
        'air_num': air_num, 
        'title': title.replace('"', "'"), 
        'preview_img': preview_img, 
        'preview_mov': preview_mov, 
        'description': description.replace('"', "'")
    }
    
    return [result]
