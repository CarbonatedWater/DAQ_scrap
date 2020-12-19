"""
MBC 프로그램 수집
"""

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil.parser import parse
import time
from scrap import utils


REFER = 'http://m.imbc.com'

# 함수: 다음 요일 찾기
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)


def scrap(prog_name, url, original_air_date, week):
    s = utils.sess(REFER)
    resp = s.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    new_item = soup.select_one('section.preview-wrap')
    title = new_item.select_one('p').text
    air_num =  new_item.select_one('strong').text
    # 숫자가 아니면 넘기기
    try:
        int(air_num)
    except:
        return None
    preview_mov = ''
    preview_img = new_item.select_one('img')['src']
    description = ''
    air_date = new_item.select_one('span.date').text.replace('.', '-')
    # sk BTV 정보 보완
    #btv_info = utils.get_btv_info(BTV_CON_ID[prog_name])
    #print(btv_info)
               
    result = {
        'air_date': air_date, 
        'air_num': air_num, 
        'title': title.replace('"', "'"), 
        'preview_img': preview_img, 
        'preview_mov': preview_mov, 
        'description': description.replace('"', "'")
    }

    return [result]
