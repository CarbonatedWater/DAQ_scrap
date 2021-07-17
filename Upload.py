"""
웹페이지 생성 및 github 업로드
"""

import os
from pathlib import Path
from bs4 import BeautifulSoup
import upload_program_info
from pages import share_proto


HTML_FRONT = '''
<!DOCTYPE html>
<html>
    <head>
    </head>
    <body>
        <table>
'''
HTML_REAR = '''        
</table>
</body>
</html>
'''
PATH_GIT_REPO = r'path\to\your\project\folder\.git'

CH_COLOR = {"EBS": "green", "KBS": "royalblue", "JTBC": "orange", "MBC": "black", "SBS": "royalred", "TVN": "red"}

def air_html(contents, air_times, directory, prog_name, program_url):
    inner = ''
    # 프로그램 방영순서로 정렬
    sorted_contents = []
    for content in contents:
        tmp = list(content)
        tmp.append(tmp[3] + air_times[content[0]-1][1])
        sorted_contents.append(tmp)
    sorted_contents = sorted(sorted_contents, key=lambda x: x[-1])
    for content in sorted_contents:
        tmp_td = ''
        program_id = None
        # 방영 공유 페이지 생성
        if directory != 'week':
            create_share_html(content, air_times, prog_name, directory, program_url)
        for i, col in enumerate(content):
            # 방영정보 리스트 테이블 생성
            if i == 3:
                program_air_time = air_times[program_id-1][0]
                tmp_td += "<td>{} {}</td>".format(col, program_air_time)
            else:
                if i == 0:
                    # 프로그램 id 저장
                    program_id = col
                tmp_td += "<td>{}</td>".format(col)
        inner += "<tr>{}</tr>".format(tmp_td)
    
    html = '{}{}{}'.format(HTML_FRONT, inner, HTML_REAR)

    if directory == 'week':
        p = Path('./pages') / directory / 'index.html'
    else:
        p = Path('./pages/airlist') / directory / 'index.html'
    p.write_text(html)


def create_share_html(content, air_times, prog_name, directory, program_url):
    ch = directory.split("_")[0]
    if content[4].startswith("http"):
        img_url = content[4]
    else:
        img_url = f"https://carbonatedwater.github.io/images/program/{directory}.jpg"
    html = share_proto.html.format(prog_name, content[2], content[2], content[1], 
    prog_name, CH_COLOR[ch], ch, content[3], air_times[content[0]-1][0], 
    img_url, content[6], program_url)
    p = Path('./pages/airlist') / directory / '{}.html'.format(content[1])
    print(p)
    p.write_text(html)


def program_detail_html(contents, directory):
    inner = ''

    for content in contents:
        tmp_td = ''
        for col in content:
            tmp_td += "<td>{}</td>".format(col)
        inner += "<tr>{}</tr>".format(tmp_td)
    
    html = '{}{}{}'.format(HTML_FRONT, inner, HTML_REAR)

    p = Path('./pages') / directory / 'index.html'
    p.write_text(html)


def update_noti_html(ch_change, version=None):
    p = Path('./pages') / 'update' / 'index.html'
    if version is None:
        raw = p.read_text()
        soup = BeautifulSoup(raw)
        num = soup.select_one('h1').text
        val = int(num) + 1
    else:
        val = version
    # 채널 추가기능을 위한 업데이트 넘버 체크
    if ch_change and val // 2 == 1:
        val += 2
    elif not(ch_change) and val // 2 == 0:
        val += 1

    # change_type: "new", "change"
    inner = '<h1>{}</h1>'.format(val)
    html = '{}{}{}'.format(HTML_FRONT, inner, HTML_REAR)

    p.write_text(html)


def setup_program(prog_name: str, img_name: str):
    # 1. 이미지파일명 json 만들기
    upload_program_info.add_program_img(prog_name, img_name)
    # 2. 방영정보 폴더 만들기
    air_dir = os.path.join('./pages/airlist', img_name)
    if not os.path.exists(air_dir):
        os.mkdir(air_dir)
    # 3. 프로그램 정보 페이지 업데이트
    cont = upload_program_info.update_program_base_info()
    program_detail_html(cont, 'programs')
