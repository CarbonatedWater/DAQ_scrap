"""
웹페이지 생성 및 github 업로드
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
import upload_program_info


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


def air_html(contents, air_times, directory):
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
        for i, col in enumerate(content):
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


def update_noti_html(version: int):
    # change_type: "new", "change"
    inner = '<h1>{}</h1>'.format(version)
    html = '{}{}{}'.format(HTML_FRONT, inner, HTML_REAR)

    p = Path('./pages') / 'update' / 'index.html'
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


def update_program():
    # 프로그램 정보 페이지 업데이트
    cont = upload_program_info.update_program_base_info()
    program_detail_html(cont, 'programs')
