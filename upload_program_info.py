import os
import sys
import json
import sqlite3
import Upload
import re

PATH_DB = './db/program.db'
conn = sqlite3.connect(PATH_DB)
cur = conn.cursor()

cur.execute("SELECT * FROM programs;")
tbl = cur.fetchall()
cur.close()

# tuple to list
programs = []
for item in tbl:
    programs.append(list(item))


# SBS, KBS의 링크 수정
programs[0][8] = "http://program.sbs.co.kr/builder/programMainList.do?pgm_id=00000311936"
programs[1][8] = "http://program.sbs.co.kr/builder/programMainList.do?pgm_id=00000339666"
programs[2][8] = "http://program.sbs.co.kr/builder/programMainList.do?pgm_id=00000010101"
programs[10][8] = "http://news.kbs.co.kr/vod/program.do?bcd=0039"
programs[11][8] = "http://www.kbs.co.kr/1tv/sisa/k_special/index.html"
programs[12][8] = "http://program.kbs.co.kr/2tv/culture/storyhunter/pc/?section_id=1759"
programs[13][8] = "http://program.kbs.co.kr/1tv/news/worldreport/pc/?section_id=1759"
programs[14][8] = "http://program.kbs.co.kr/2tv/culture/worlddocu/pc/?section_id=1761"

# 디스크립션의 개행기호 오류 수정
for program in programs:
    print(program[6])
    program[6] = program[6].replace('\\n', '\n')
    print(program[6])


# SBS 프로그램 타이틀 제목 수정
cur.execute("SELECT * FROM contents WHERE id BETWEEN 1 AND 3;")
df = cur.fetchall()
result = []
for info in df:
    print(info)
    tmp = list(info)
    tmp[2] = tmp[2].replace("[{}회] ".format(tmp[1]), "")
    print(tmp)
    result.append(tmp)

amend_query = """
UPDATE contents 
SET 
title = '{}' 
WHERE id = {} AND air_num = {};
"""


for r in result:
    print(r[2])
    UPDATE_QUERY = amend_query.format(
        r[2], r[0], r[1] # WHERE 조건
    )
    print(UPDATE_QUERY)
    cur.execute(UPDATE_QUERY)
    conn.commit()


# KBS 제보자들 회차 타이틀 수정
cur.execute("SELECT * FROM contents WHERE id = 14;")
raw = cur.fetchall()
result = []
for info in raw:
    print(info)
    tmp = list(info)
    tmp[1] = int(tmp[2].replace("회", ""))
    tmp[2] = ''
    print(tmp)
    result.append(tmp)

amend_query = """
UPDATE contents 
SET 
air_num = {}, 
title = '{}' 
WHERE id = {} AND air_date = '{}';
"""

for r in result:
    print(r[2])
    UPDATE_QUERY = amend_query.format(
        r[1], 
        r[2], 
        r[0], r[3] # WHERE 조건
    )
    print(UPDATE_QUERY)
    cur.execute(UPDATE_QUERY)
    conn.commit()
# 본문 수정
test = result[-1]
re.compile(r"(\d+회방송일시.+)첫 번째").search(test[-1]).group(1)


amend_query = """
UPDATE contents 
SET 
description = '{}' 
WHERE id = {} AND air_num = '{}';
"""

result2 = []
for tmp in raw:
    print(tmp[1])
    info = list(tmp)
    if re.compile(r"^.+내용■ ").search(info[6]) is not None:
        delpadding = re.compile(r"^(.+내용■ )").search(info[6]).group(1)
        print(delpadding)
        info[6] = info[6].replace(delpadding, "")
        result2.append(info)



amend_query = """
UPDATE contents 
SET 
description = '{}' 
WHERE id = {} AND air_num = {};
"""

for r in result2:
    print(r[1])
    UPDATE_QUERY = amend_query.format(
        r[6], 
        r[0], r[1] # WHERE 조건
    )
    print(UPDATE_QUERY)
    cur.execute(UPDATE_QUERY)
    conn.commit()




UPDATE_QUERY = amend_query.format(
    result[-2][6], 
    result[-2][0], result[-2][1] # WHERE 조건
)

