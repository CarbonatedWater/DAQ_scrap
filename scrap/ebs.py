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
    '다큐 시선': '{617E3A57-A40A-11E7-A50E-376259EF559C}'
}


def scrap(prog_name, URL, original_air_date, week):
    s = utils.sess(REFER)
    resp = s.get(URL)
    soup = BeautifulSoup(resp.text, 'lxml')
    new_item = soup.select('tbody#itemList > tr')[0]
    title = new_item.select_one('td.subject span').text
    sub_link = requests.compat.urljoin(REFER, new_item.select_one('td.subject a')['href'])
    if prog_name == '다큐 시선':
        air_num_tmp = re.search(r"\[([0-9]+)화\]", title)
        air_num = air_num_tmp.group(1)
        date_tmp = re.search(r"\([0-9]{1,2}\/[0-9]{1,2}\)", title)
        title = title.replace(air_num_tmp.group(0), "").replace(date_tmp.group(), "").strip()
        time.sleep(3)
        # 뉴 방송 페이지 접속
        resp = s.get(sub_link)
        soup = BeautifulSoup(resp.text, 'lxml')
        content = soup.select_one('div.con_txt')
        preview_mov = content.select_one('video')['src']
        preview_img = ''
        cont_text_tmp = [x.text for x in content.select('div') if (x.attrs == {}) and (x.text != '')]
        cont_text_tmp.extend([x.text for x in content.select('p') if x.text != ''])
        description = '\n'.join(cont_text_tmp)
        air_date_tmp = ''
        for text in cont_text_tmp:
            if re.search("EBS", text):
                air_date_tmp = re.search(r"[0-9]{4}년 ?[0-9]{1,2}월 ?[0-9]{1,2}일", text).group()
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
                preview_img = btv_info['content']['hd_series'][0]['thumb_image'].\
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
    elif prog_name == '다큐프라임':
        title = "<%s>" % title
        air_num = new_item.select_one('td').text
        lst_air_date = (new_item.select('td')[2].text.strip()).split(' ~ ')
        print(lst_air_date)
        year = ''
        air_dates = []
        for date in lst_air_date:
            year_tmp = re.compile(r"[0-9]{4}").search(date)
            if year_tmp is not None:
                year = year_tmp.group()
            month = re.compile(r"([0-9]{2})월").search(date).group(1)
            day = re.compile(r"([0-9]{2})일").search(date).group(1)
            air_date = '-'.join([year, month, day])
            air_dates.append(air_date)
        # 마지막 방영날짜와 처음 방영날짜의 차이가 2일 경우 중간 날짜 추가
        last_date = datetime.strptime(air_dates[-1], '%Y-%m-%d')
        first_date = datetime.strptime(air_dates[0], '%Y-%m-%d')
        if (last_date - first_date).days == 2:
            middle_date = last_date - timedelta(days=1)
            air_dates.insert(1, str(middle_date)[:10])
        # 뉴 방송 페이지 접속
        resp = s.get(sub_link)
        soup = BeautifulSoup(resp.text, 'lxml')
        preview_img = soup.select_one('div.view_con > div.gallery img')['src']
        try:
            preview_mov = soup.select_one('div.view_con > div.gallery > div.owl-carousel a')['data-src']
        except KeyError:
            preview_mov = ''
        ## 서브 타이틀명 추출
        sub_titles_tag = soup.select('div.b_date > div > font > div')
        if len(sub_titles_tag) <= 3:
            sub_titles_tag = sub_titles_tag[:2]
            sub_titles_tag.extend(soup.select('div.b_date > div > font > div:nth-of-type(3) > div'))
        sub_titles = []
        for sub_title_tmp in sub_titles_tag[2:]:
            sub_titles.append(sub_title_tmp.select_one('b').text.strip())
        ## 회차설명 추출
        descriptions = []
        for desc in soup.select('div.summary > div.con_detail')[1:]:
            if desc.select('div'):
                descriptions.append(desc.select('div')[2].text)
            elif desc.select('p'):
                descriptions.append(desc.select('p')[2].text)
        results = []
        for i in range(len(air_dates)):
            results.append({
                'air_date': air_dates[i], 
                'air_num': air_num, 
                'title': '{} - {}'.format(title, sub_titles[i]), 
                'preview_img': preview_img, 
                'preview_mov': preview_mov, 
                'description': descriptions[i].replace('"', "'")
            })

        return results
