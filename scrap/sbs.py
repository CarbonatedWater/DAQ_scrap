"""
SBS 프로그램 수집
"""

import json
import re
from datetime import datetime, timedelta
from dateutil.parser import parse
from bs4 import BeautifulSoup 
from scrap import utils
from urllib.parse import unquote


REFER = 'https://programs.sbs.co.kr/'

API_URL = {
    'SBS 스페셜': 'sbsspecial', 
    '그것이 알고싶다': 'unansweredquestions', 
    '궁금한 이야기 Y': 'cube', 
    '순간포착 세상에 이런일이': 'whatonearth', 
    '꼬리에 꼬리를 무는 그날 이야기': '2020tail'
}

BTV_CON_ID = {
    'SBS 스페셜': '{A4FA8AF7-6AC3-11E8-BC2D-BD92772229B5}', 
    '그것이 알고싶다': '{C5AEC9FC-E1FB-493A-BF5E-69902B04F38A}', 
    '궁금한 이야기 Y': '{4BD19D72-285F-4629-A98F-3563064BD64A}'   
}


def scrap(prog_name, url, original_air_date, week):
    s = utils.sess(REFER)
    resp = s.get("https://static.apis.sbs.co.kr/program-api/2.0/main/" + API_URL[prog_name])
    #soup = BeautifulSoup(resp.text, 'lxml')
    content = json.loads(resp.text)
    if prog_name in ["궁금한 이야기 Y", "그것이 알고싶다", '순간포착 세상에 이런일이', \
        '꼬리에 꼬리를 무는 그날 이야기']:
        show_advance = content['layers'][3]['items'][0]['medias'] # 미리보기 리스트
    elif prog_name == "SBS 스페셜":
        show_advance = content['layers'][3]['items'][2]['medias']
    print(show_advance[0])
    try:
        regdate = parse(show_advance[0]['regdate']).date()
        day_diff = week.index(original_air_date[0]) - regdate.weekday()
        air_date = str(regdate + timedelta(days=day_diff))
    except:
        air_date = str(parse(show_advance[0]['broaddate']).date())

    if prog_name in ['순간포착 세상에 이런일이', '꼬리에 꼬리를 무는 그날 이야기']:
        if prog_name == '꼬리에 꼬리를 무는 그날 이야기':
            title = show_advance[0]['contenttitle']
        else:
            title = show_advance[0]['title']
        preview_img = show_advance[0]['thumb']['large']
        preview_mov = None
        description = show_advance[0]['description']
        # 다음 TV 정보 반영(회차)
        result_daum = utils.get_daum_info(prog_name)
        air_num = result_daum['air_num']
        air_date = result_daum['air_date']
    else:
        air_num_tmp = re.search(r"([0-9]+)회", show_advance[0]['title'])
        if not(air_num_tmp):
            return None
        air_num = air_num_tmp.group(1)
        title = show_advance[0]['title'].replace("[{}회] ".format(air_num), "")
        preview_img = "https:" + show_advance[0]['thumb']['large']
        preview_mov = None
        description = show_advance[0]['link_url']
    # DAUM 정보 보완
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
