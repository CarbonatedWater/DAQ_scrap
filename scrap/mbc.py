"""
MBC 프로그램 수집
"""

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil.parser import parse
import time


REFER = 'http://m.imbc.com'


# 함수: 세션생성
def sess(refer):
    AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
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
    resp = s.get(URL)
    soup = BeautifulSoup(resp.text, 'lxml')
    new_item = soup.select_one('section.preview-wrap')
    title = new_item.select_one('p').text
    air_num =  new_item.select_one('strong').text
    preview_mov = ''
    preview_img = new_item.select_one('img')['src']
    description = ''
    air_date = new_item.select_one('span.date').text.replace('.', '-')
    
    result = {
        'air_date': air_date, 
        'air_num': air_num, 
        'title': title, 
        'preview_img': preview_img, 
        'preview_mov': preview_mov, 
        'description': description.replace('"', "'")
    }

    return [result]
