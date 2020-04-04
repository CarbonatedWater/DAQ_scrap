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
    '순간포착 세상에 이런일이': 'whatonearth'
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
    if prog_name in ["궁금한 이야기 Y", "그것이 알고싶다", '순간포착 세상에 이런일이']:
        show_advance = content['layers'][4]['items'][0]['medias'] # 미리보기 리스트
    elif prog_name == "SBS 스페셜":
        show_advance = content['layers'][4]['items'][2]['medias']
    print(show_advance[0])
    try:
        regdate = parse(show_advance[0]['regdate']).date()
        day_diff = week.index(original_air_date[0]) - regdate.weekday()
        air_date = str(regdate + timedelta(days=day_diff))
    except:
        air_date = str(parse(show_advance[0]['broaddate']).date())

    if prog_name == '순간포착 세상에 이런일이':
        title = show_advance[0]['title']
        preview_img = show_advance[0]['thumb']['large']
        preview_mov = None
        description = show_advance[0]['description']
        # 네이버 검색 노출 정보 반영(회차)
        resp = utils.naver_search(s, prog_name)
        soup = BeautifulSoup(resp.text, "lxml")
        content_info = soup.select_one('div.turn_info_wrap')
        try:
            air_date_check = re.search(r'\d{4}\.?\d{1,2}\.?\d{1,2}', content_info.select('dd')[1].text).group()
        except:
            pass
        print(air_date_check)
        if air_date_check and air_date == str(parse(air_date_check).date()):
            air_num = content_info.select_one('dl.turn_info_desc > dd').text.replace('회', '')
        elif air_date_check and parse(air_date).date() < parse(air_date_check).date():
            title = content_info.select_one('strong.tlt').text
            air_num = content_info.select_one('dl.turn_info_desc > dd').text.replace('회', '')
            air_date = str(parse(air_date_check).date())
            try:
                preview_img = content_info.select_one('div.thumb > img')['src'].replace('quality=90', 'quality=100')\
                    .replace('265x150', '530x300').replace(';=', '=')
                preview_img = unquote(preview_img)
            except:
                print('===== naver img None')
                preview_img = ''
            preview_mov = ''
            description = content_info.select_one('p.episode_txt').text
        else:
            air_num = ''
    else:
        air_num = re.search(r"([0-9]+)회", show_advance[0]['title']).group(1)
        title = show_advance[0]['title'].replace("[{}회] ".format(air_num), "")
        preview_img = "https:" + show_advance[0]['thumb']['large']
        preview_mov = None
        description = show_advance[0]['link_url']
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
