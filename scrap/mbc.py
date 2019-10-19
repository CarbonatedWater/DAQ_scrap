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

btv_con_id = {
    'MBC 스페셜': '{E0D9A6AC-5A6F-11E8-91B3-AF1AD3B8D2B6}', 
    'PD수첩': '{B03D32D2-3881-4409-AE53-3CC57DC7C271}', 
    '탐사기획 스트레이트': '{6CBA8FDB-9EEA-4008-8D0D-F6DC244969F3}', 
    '실화탐사대': '{7A96FC40-E748-40F2-B435-801E56DD3C64}'
}


# 함수: 다음 요일 찾기
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)


def scrap(prog_name, URL, original_air_date, week):
    s = utils.sess(REFER)
    resp = s.get(URL)
    soup = BeautifulSoup(resp.text, 'lxml')
    new_item = soup.select_one('section.preview-wrap')
    title = new_item.select_one('p').text
    air_num =  new_item.select_one('strong').text
    preview_mov = ''
    preview_img = new_item.select_one('img')['src']
    description = ''
    air_date = new_item.select_one('span.date').text.replace('.', '-')
    # sk BTV 정보 보완
    btv_info = utils.get_btv_info(btv_con_id[prog_name])
    print(btv_info)
    if btv_info:
        try:
            air_date_check = re.search(r'\d{2}\.\d{2}\.\d{2}', btv_info['content']['s_title']).group()
        except:
            print('===== air_date_check error')
            pass
        print('===== air_date_check: %s' % str(parse('20' + air_date_check).date()))
        if air_date_check and (air_date == str(parse('20' + air_date_check).date())):
            description = btv_info['content']['c_desc']
    
    result = {
        'air_date': air_date, 
        'air_num': air_num, 
        'title': title, 
        'preview_img': preview_img, 
        'preview_mov': preview_mov, 
        'description': description.replace('"', "'")
    }

    return [result]
