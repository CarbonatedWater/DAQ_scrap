"""
JTBC 프로그램 수집
"""

import re
from bs4 import BeautifulSoup
from scrap import utils


REFER = 'https://http://tv.jtbc.joins.com/'


btv_con_id = {
    '차이나는 클라스': '{6DEACDCD-2166-4599-9B9B-77B5938ED1F0}'
}


def scrap(prog_name, url, original_air_date, week):
    s = utils.sess(REFER)
    resp = s.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    try:
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
            try:
                air_num = re.search(r"([0-9]+)회", title).group(1)
            except:
                return None
            preview_img = soup.find("meta", property="og:image")['content']
            preview_mov = None
            description = soup.find("meta", {'name': "og:description"})['content']
        elif prog_name in ['다큐 플러스', 'JTBC FACTUAL']:
            content = soup.select_one('div.bx_preview')
            tmp_date = content.select_one('span.date').text
            air_date = re.match(r"^\d{4}(\.\d{2}){2}", tmp_date).group().replace(".", "-")
            if prog_name == '다큐 플러스':
                title = '다큐 플러스'
            else:
                title = content.select_one('span.info span.tit').text
            preview_img = content.select_one('span.img > img')['src']
            # 회차가 없음
            air_num = re.search(r"img\/([0-9]{8})", preview_img).group(1)
            preview_mov = None
            description = content.select_one('span.txt').text
    except Exception as e:
        print(f"===== error: {e}")
        pass
    # DAUM 정보 보완
    result_daum = utils.get_daum_info(prog_name)
    try:
        if result_daum and result_daum['air_date'] == air_date:
            description = result_daum['desc']
    except:
        air_date = result_daum['air_date']
        air_num = result_daum['air_num']
        title = result_daum['sub_title']
        preview_img = result_daum['preview_img']
        preview_mov = ''
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
