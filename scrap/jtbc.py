"""
JTBC 프로그램 수집
"""

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


REFER = 'https://http://tv.jtbc.joins.com/'

# 함수: 세션생성
def sess(refer):
    AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    s = requests.Session()
    s.headers.update({'User-Agent': AGENT, 'Referer': refer})
    return s


def scrap(prog_name, URL, original_air_date, week):
    s = sess(REFER)
    resp = s.get(URL)
    soup = BeautifulSoup(resp.text, 'lxml')
    if prog_name == '이규연의 스포트라이트':
        content = soup.select_one('div.bx_preview')
        tmp_date = content.select_one('span.date').text
        air_date = re.match(r"^\d{4}(\.\d{2}){2}", tmp_date).group().replace(".", "-")
        air_num = re.search(r"([0-9]+)회", content.select_one('span.tit').text).group(1)
        title = [x for x in content.select_one('span.info span.txt').children][0].replace("부제 : ", "").replace("'", "")
        preview_img = content.select_one('span.img > img')['src']
        preview_mov = None
        description = content.select_one('span.txt').text
    elif prog_name == '차이나는 클라스':
        #content = soup.select_one('[data-host]')
        tmp_date = soup.select_one('div.play_info em').text
        air_date = re.match(r"^\d{4}(\.\d{2}){2}", tmp_date).group().replace(".", "-")
        title = soup.find("meta", property="og:title")['content']
        air_num = re.search(r"([0-9]+)회", title).group(1)
        preview_img = soup.find("meta", property="og:image")['content']
        preview_mov = None
        description = soup.find("meta", {'name': "og:description"})['content']
    elif prog_name == '다큐 플러스':
        content = soup.select_one('div.bx_preview')
        tmp_date = content.select_one('span.date').text
        air_date = re.match(r"^\d{4}(\.\d{2}){2}", tmp_date).group().replace(".", "-")
        title = content.select_one('span.info span.txt').text
        preview_img = content.select_one('span.img > img')['src']
        # 회차가 없음
        air_num = re.search(r"img\/([0-9]{8})", preview_img).group(1)
        preview_mov = None
        description = content.select_one('span.txt').text

    result = {
        'air_date': air_date, 
        'air_num': air_num, 
        'title': title, 
        'preview_img': preview_img, 
        'preview_mov': preview_mov, 
        'description': description.replace('"', "'")
    }
    
    return [result]
