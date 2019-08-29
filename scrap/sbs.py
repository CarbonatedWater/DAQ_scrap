"""
SBS 프로그램 수집
"""

import requests
import json
import re
from datetime import datetime, timedelta
from dateutil.parser import parse


REFER = 'https://programs.sbs.co.kr/'

# 함수: 세션생성
def sess(refer):
    AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    s = requests.Session()
    s.headers.update({'User-Agent': AGENT, 'Referer': refer})
    return s


def scrap(prog_name, URL, original_air_date, week):
    s = sess(REFER)
    resp = s.get(URL)
    #soup = BeautifulSoup(resp.text, 'lxml')
    content = json.loads(resp.text)
    if prog_name in ["궁금한 이야기 Y", "그것이 알고싶다"]:
        show_advance = content['layers'][4]['items'][0]['medias'] # 미리보기 리스트
    elif prog_name == "SBS 스페셜":
        show_advance = content['layers'][4]['items'][2]['medias']

    regdate = parse(show_advance[0]['regdate']).date()
    day_diff = week.index(original_air_date[0]) - regdate.weekday()
    air_date = str(regdate + timedelta(days=day_diff))

    air_num = re.search(r"([0-9]+)회", show_advance[0]['title']).group(1)
    title = show_advance[0]['title']
    preview_img = "https:" + show_advance[0]['thumb']['large']
    preview_mov = None
    description = show_advance[0]['link_url']
    
    result = {
        'air_date': air_date, 
        'air_num': air_num, 
        'title': title, 
        'preview_img': preview_img, 
        'preview_mov': preview_mov, 
        'description': description
    }
    
    return [result]
