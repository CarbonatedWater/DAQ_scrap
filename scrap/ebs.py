"""
EBS 프로그램 수집
"""

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil.parser import parse
import time
from scrap import utils


REFER = 'http://home.ebs.co.kr/'

btv_con_id = {
    '다큐 시선': '{617E3A57-A40A-11E7-A50E-376259EF559C}', 
    '건축탐구 집': '{53FEA124-AA1A-460E-A445-2A88A7F2993D}', 
    '명의': '{57B29139-4752-11E7-B550-E7E06F367DD3}'
}


def scrap(prog_name, url, original_air_date, week):
    s = utils.sess(REFER)
    resp = s.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    new_item = soup.select('tbody#itemList > tr')[0]
    try:
        title = new_item.select_one('td.subject span').text
    except:
        return None
    sub_link = requests.compat.urljoin(REFER, new_item.select_one('td.subject a')['href'])
    if prog_name != '다큐프라임':
        if prog_name == '다큐 시선':
            air_num_tmp = re.search(r"\[([0-9]+)화\]", title)
            air_num = air_num_tmp.group(1)
            date_tmp = re.search(r"\([0-9]{1,2}\/[0-9]{1,2}\)", title)
            if date_tmp:
                title = title.replace(air_num_tmp.group(0), "").replace(date_tmp.group(), "").strip()
            else:
                title = title.replace(air_num_tmp.group(0), "").strip()
        elif prog_name == '건축탐구 집':
            air_num = re.search(r"view/([0-9]{11})", sub_link).group(1)
            title = title.replace("건축탐구 집 시즌2", "").replace("<", "").replace(">", "").strip()
        elif prog_name == "명의":
            air_num_tmp = re.search(r"제 ([0-9]{3})회", title).group()
            air_num = re.search(r"제 ([0-9]{3})회", title).group(1)
            title = title.replace(air_num_tmp, "").strip()
        time.sleep(3)
        # 뉴 방송 페이지 접속
        resp = s.get(sub_link)
        soup = BeautifulSoup(resp.text, 'lxml')
        content = soup.select_one('div.con_txt')
        preview_mov = content.select_one('video')['src']
        preview_img = ''
        cont_text_tmp = [x.text for x in content.select('div') if (x.attrs == {}) and (x.text != '')]
        if len(cont_text_tmp) < 1:
            # 추출 실패 시 조건 완화해서 재실행
            cont_text_tmp = [x.text for x in content.select('div') if x.text != '']
        cont_text_tmp.extend([x.text for x in content.select('p') if x.text != ''])
        cont_text_tmp = [x.strip() for x in cont_text_tmp if x not in ['끝.', '\n\n\n\n']]
        description = '\n'.join(cont_text_tmp)
        air_date_tmp = ''
        for text in cont_text_tmp:
            if re.search("EBS", text):
                try:
                    air_date_tmp = re.search(r"[0-9]{4}년 ?[0-9]{1,2}월 ?[0-9]{1,2}일", text).group()
                except:
                    print("===== sentence: %s" % text)
                    pass
        if air_date_tmp == '':
            regdate = re.search(r"[0-9]{4}\.[0-9]{2}\.[0-9]{2}", new_item.text).group()
            regdate = parse(regdate).date()
            air_date = str(utils.next_weekday(regdate, week.index(original_air_date[0])))
        else:
            air_date = str(parse(air_date_tmp.replace('일', '').replace('월', '-').replace('년', '')).date())
        # sk BTV 정보 보완
        btv_info = utils.get_btv_info(btv_con_id[prog_name])
        if btv_info:
            try:
                air_date_check = re.search(r'\d{2}\.\d{2}\.\d{2}', btv_info['content']['s_title']).group()
            except:
                pass
            if air_date_check and (air_date == str(parse('20' + air_date_check).date())):
                description = btv_info['content']['c_desc']
                preview_img = btv_info['content']['hd_series'][-1]['thumb_image'].\
                replace('195x110', '390x220')

        result = {
            'air_date': air_date, 
            'air_num': air_num, 
            'title': title, 
            'preview_img': preview_img, 
            'preview_mov': preview_mov, 
            'description': description.replace('"', "'")
        }

        return [result]
        
    else:
        # 이미지 수집을 위한 EBS 방송 페이지 접속
        resp = s.get(sub_link)
        soup = BeautifulSoup(resp.text, 'lxml')
        preview_img = soup.select_one('div.view_con > div.gallery > div.gallery_img > p > img')['src']
        try:
            preview_mov = soup.select_one('div.view_con > div.gallery > div.owl-carousel a')['data-src']
        except KeyError:
            preview_mov = ''
        ## 다큐프라임 정보 추출(다음 정보)
        result_daum = utils.get_daum_info(prog_name)
        if result_daum:
            # DB 삽입 결과 생성
            result = {
                'air_date': result_daum['air_date'], 
                'air_num': result_daum['air_num'], 
                'title': result_daum['sub_title'], 
                'preview_img': preview_img, 
                'preview_mov': preview_mov, 
                'description': result_daum['desc'].replace('"', "'")
            }
            return [result]
        else:
            return None
