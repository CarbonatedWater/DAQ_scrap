import requests
import re
import json
from bs4 import BeautifulSoup
from dateutil.parser import parse
from datetime import datetime, timedelta
from urllib.parse import quote_plus


REFER_B = 'http://mapp.btvplus.co.kr/recommend.do'
REFER_D = 'http://www.daum.net'


# 웹 세션 생성
def sess(refer):
    AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
    s = requests.Session()
    s.headers.update({'User-Agent': AGENT, 'Referer': refer})
    return s


# BTV 정보 가져오기
def get_btv_info(con_id):
    s = sess(REFER_B)
    base_url = 'http://mapp.btvplus.co.kr/synopsisInfo.do'
    resp = s.get(base_url, params={
        'con_id': con_id, 
        'yn_recent': 'Y'
    })
    try:
        info_json = re.compile(r'syData.+\};').search(resp.text).group()
        #print('===== info_json: %s' % info_json)
        return json.loads(info_json.replace('syData = ', '').replace(';', ''))
    except:
        print('===== json error')
        return None


# 제목에서 방영일 생성하기
def trans_date(date_string):
    air_date = date_string.replace(' ', '').replace('년', '-').replace('월', '-').replace('일', '')
    return str(parse(air_date).date())


# 함수: 다음 요일 찾기
def next_weekday(d: datetime.date, weekday: int) -> datetime.date:
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)


# html escape 수정
def html_escape(text: str) -> str:
    return text.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">")\
        .replace("&quot;", '"').replace("&amp;", "&")


# html encoding
def naver_search(session: requests.Session, word: str) -> requests.Response:
    url = 'https://search.naver.com/search.naver?query=%s' % quote_plus(word)
    return session.get(url)


# 다음 프로그램 정보 가져오기
def get_daum_info(query: str) -> dict:
    s = sess(REFER_D)
    resp = s.get("https://search.daum.net/search?w=tv&q={}".format(quote_plus(query)))
    soup = BeautifulSoup(resp.text, 'lxml')
    try:
        content_info = soup.select_one('ul.list_date > li.on')
        air_num = soup.select_one('div.episode_cont strong.txt_episode').text.\
            replace('회', '')
        air_date_tmp = content_info['data-clip']
        air_date = "{}-{}-{}".format(air_date_tmp[:4], air_date_tmp[4:6], air_date_tmp[6:])
        sub_title = soup.select_one('div.episode_cont p > strong').text
        try:
            preview_img = soup.select_one('div.wrap_player > div > a > img')['src']
        except:
            preview_img = ''
        ## 회차설명 추출
        description = soup.select_one('div.episode_cont p.episode_desc').text
        return {
            'air_num': air_num, 
            'air_date': air_date, 
            'sub_title': sub_title, 
            'desc': description, 
            'preview_img': preview_img
        }
    except:
        print("===== daum error")
        return None
