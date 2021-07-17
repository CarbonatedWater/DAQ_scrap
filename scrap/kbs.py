"""
KBS 프로그램 수집
"""

import re
import json
from dateutil.parser import parse
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
    '시사기획 창': 'T2011-1097-04-428648', 
    '다큐세상': 'T2018-0304-04-989186', 
    '생로병사의 비밀': 'T2002-0429-04-185153', 
    '다큐멘터리 3일': 'T2007-0188-04-895363', 
    '시사 직격': 'T2019-0280-04-513653', 
    '이슈 픽 쌤과 함께': 'T2020-0372-04-880197', 
    '한국인의 밥상': 'T2010-1657-04-625263'
}


def scrap(prog_name, url, original_air_date, week):
    if prog_name in ['생로병사의 비밀', '다큐멘터리 3일']:
        result_daum = utils.get_daum_info(prog_name)
        air_num = result_daum['air_num']
        air_date = result_daum['air_date']
        title = result_daum['sub_title']
        description = result_daum['desc']
        preview_img = result_daum['preview_img']
        preview_mov = ''
    else:
        PARAM_B['bbs_id'] = BBS_ID[prog_name]
        s = utils.sess(REFER)
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
            air_num = re.compile(r'[-0-9]+').search(title).group()
            title = ''
            if re.compile(r".+첫 번째 이야기").search(content_info['description']) is not None:
                front_padding = re.compile(r"(.+)첫 번째 이야기").search(content_info['description']).group(1)
                description = content_info['description'].replace(front_padding, "")
        elif prog_name in ['이슈 픽 쌤과 함께', '시사 직격', '한국인의 밥상']:
            air_num_padding = re.compile(r"^\[([0-9]+)회\] ").search(title)
            air_num = air_num_padding.group(1)
            title = title.replace(air_num_padding.group(0), '')
        elif prog_name == '시사기획 창':
            try:
                air_num = re.compile(r'[-0-9]+').search(title).group()
                padding = re.compile(r'\[.*\: ?').match(title).group()
                title = title.replace(padding, '')
            except:
                pass
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
            try:
                regdate_tmp = title.replace('년', '-').replace('월', '-').replace('일', '').split()[:3]
                regdate = parse(regdate_tmp).date()
            except:
                tmp = content_info['title'].split('/')[1].strip()
            regdate_tmp = tmp.replace('년', '-').replace('월', '-').replace('일', '').split()[:3]
            try:
                regdate_tmp = re.compile(r'(.*)\(.+\)').search(''.join(regdate_tmp)).group(1)
            except:
                regdate_tmp = ''.join(regdate_tmp)
        else:
            regdate_tmp = content_info['rdatetime'].split()[0]
    
    # 방영일 파싱
    try:
        regdate = parse(regdate_tmp).date()
    except:
        pass
    if prog_name == '세상의 모든 다큐':
        air_date = str(regdate)
    elif prog_name in ['다큐멘터리 3일', '생로병사의 비밀']:
        air_date = utils.trans_date(air_date)
    elif prog_name in ['특파원 보고 세계는 지금', '다큐세상', '이슈 픽 쌤과 함께', '한국인의 밥상']:
        air_date = re.search(r'\d{4}년 ?\d{1,2}월 ?\d{1,2}일', content_info['title']).group()
        air_date = utils.trans_date(air_date)
    elif prog_name == '다큐 인사이트':
        try:
            air_date = re.search(r'(\d{4}년 ?\d{1,2}월 ?\d{1,2}일) \(.\)', content_info['description']).group(1)
            air_date = utils.trans_date(air_date)
        except:
            air_date = str(utils.next_weekday(regdate, week.index(original_air_date[0])))
    else:
        air_date = str(utils.next_weekday(regdate, week.index(original_air_date[0])))

    # 다음 정보 보완
    if prog_name == '제보자들':
        result_daum = utils.get_daum_info(prog_name)
        if result_daum and result_daum['air_date'] == air_date:
            air_num = result_daum['air_num']
            air_date = result_daum['air_date']
            title = result_daum['sub_title']
            description = result_daum['desc']
    else:
        result_daum = utils.get_daum_info(prog_name)
        if result_daum and result_daum['air_date'] == air_date:
            description = result_daum['desc']
    
    result = {
        'air_date': air_date, 
        'air_num': air_num, 
        'title': title.replace('"', "'"), 
        'preview_img': preview_img, 
        'preview_mov': preview_mov, 
        'description': description.replace('"', "'")
    }
    
    return [result]
