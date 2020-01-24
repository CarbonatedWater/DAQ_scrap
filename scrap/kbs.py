"""
KBS 프로그램 수집
"""

import requests
import re
import json
from datetime import datetime, timedelta
from dateutil.parser import parse
import time
from bs4 import BeautifulSoup
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
    '시사기획 창': 'T2011-1097-04-968945', 
    '다큐세상': 'T2018-0304-04-989186', 
    '생로병사의 비밀': 'T2002-0429-04-185153', 
    '다큐멘터리 3일': 'T2007-0188-04-895363'
}

BTV_CON_ID = {
    '제보자들': '{C18F4D30-81E7-4187-B03C-CF81083D46E1}', 
    '시사기획 창': '{10D376EB-3EE8-4576-AEB4-05094068615A}'
}


# BTV 정보로 방영정보 업데이트
def update_from_btv(prog_name: str, air_date: str):
    btv_info = utils.get_btv_info(BTV_CON_ID[prog_name])
    if btv_info:
        try:
            air_date_check = re.search(r'\d{2}\.\d{2}\.\d{2}', btv_info['content']['s_title']).group()
        except:
            pass
        if air_date_check and (air_date == str(parse('20' + air_date_check).date())):
            return btv_info['content']['c_desc']


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
    elif prog_name in ['다큐멘터리 3일', '생로병사의 비밀']:
        resp = utils.naver_search(s, prog_name)
        soup = BeautifulSoup(resp.text, "lxml")
        content_info = soup.select_one('div.turn_info_wrap')
        title = content_info.select_one('strong.tlt').text
        air_num = content_info.select_one('dl.turn_info_desc > dd').text.replace('회', '')
        air_date = re.search(r'\d{4}\.?\d{1,2}\.?\d{1,2}', content_info.select('dd')[1].text).group()
        try:
            preview_img = content_info.select_one('div.thumb > img')['src'].replace('quality=90', 'quality=100')\
                .replace('265x150', '530x300')
        except:
            print('===== naver img None')
            preview_img = ''
        preview_mov = ''
        description = content_info.select_one('p.episode_txt').text
        if prog_name == '생로병사의 비밀':
            PARAM_B['bbs_id'] = BBS_ID[prog_name]
            resp = s.get(BBS_URL, params=PARAM_B) # 공통 URL 사용
            #print(resp.text)
            content_info = json.loads(resp.text)['data'][0]    
            preview_img_tmp = content_info['post_cont_image']
            if preview_img_tmp is None:
                preview_img = ''
            else:    
                preview_img = json.loads(preview_img_tmp)[0]
    else:
        PARAM_B['bbs_id'] = BBS_ID[prog_name]
        resp = s.get(BBS_URL, params=PARAM_B) # 공통 URL 사용
        #print(resp.text)
        content_info = json.loads(resp.text)['data'][0]
        
        # preview image, description 링크 저장
        preview_img_tmp = content_info['post_cont_image']
        if preview_img_tmp is None:
            preview_img = ''
        else:    
            preview_img = json.loads(preview_img_tmp)[0]
        preview_mov = ''
        description = content_info['description']

        # 타이틀, 방영회차 수정
        title = content_info['title'].split('/')[0].strip()
        air_num = content_info['post_no']
     
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
        # description의 html 코드 수정
        description = utils.html_escape(description)
        
        # 등록일 처리
        if prog_name == '세상의 모든 다큐':
            regdate_tmp = title.replace('년', '-').replace('월', '-').replace('일', '').split()[:3]
            regdate_tmp = ''.join(regdate_tmp)
        else:
            regdate_tmp = content_info['rdatetime'].split()[0]
    
    # 방영일 파싱
    try:
        regdate = parse(regdate_tmp).date()
    except:
        pass
    if prog_name == '다큐세상':
        air_date = re.search(r'\d{4}년 ?\d{1,2}월 ?\d{1,2}일', content_info['title'].split('/')[1]).group()
        air_date = utils.trans_date(air_date)
    elif prog_name in ['다큐멘터리 3일', '생로병사의 비밀']:
        air_date = utils.trans_date(air_date)
    elif prog_name in ['특파원 보고 세계는 지금']:
        air_date = re.search(r'\d{4}년 ?\d{1,2}월 ?\d{1,2}일', content_info['title']).group()
        air_date = utils.trans_date(air_date)
    else:
        air_date = str(utils.next_weekday(regdate, week.index(original_air_date[0])))

    # sk BTV 정보 보완
    if prog_name in ['시사기획 창']:
        description_tmp = update_from_btv(prog_name, air_date)
        if description_tmp is not None:
            description = description_tmp
    
    result = {
        'air_date': air_date, 
        'air_num': air_num, 
        'title': title.replace('"', "'"), 
        'preview_img': preview_img, 
        'preview_mov': preview_mov, 
        'description': description.replace('"', "'")
    }
    
    return [result]
