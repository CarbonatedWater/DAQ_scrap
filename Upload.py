"""
웹페이지 생성 및 github 업로드
"""

import git
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


def thisweek_html(contents, directory):
    inner = ''

    for content in contents:
        tmp_td = ''
        for col in content:
            tmp_td += "<td>{}</td>".format(col)
        inner += "<tr>{}</tr>".format(tmp_td)
    
    html = '{}{}{}'.format(HTML_FRONT, inner, HTML_REAR)

    p = Path(directory) / 'week' / 'index.html'
    p.write_text(html)


def commit_push(directory):
    repo = git.Repo(directory)
    add_list = repo.untracked_files
    if add_list:
        repo.index.add(add_list)
        new = 'Upload regular content info!'
        repo.index.commit(new)
        print(repo.index.commit(new).message)
        repo.git.push('origin', master)
