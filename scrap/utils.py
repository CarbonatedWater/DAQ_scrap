import requests
import re
import json


REFER_B = 'http://mapp.btvplus.co.kr/recommend.do'


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
