"""
웹페이지 생성 및 github 업로드
"""

from pathlib import Path
from datetime import datetime, timedelta


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

    for content in contents:
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
    # directory 가 update 일 경우 앱에 프로그램의 새로운 정보를 업데이트함
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
