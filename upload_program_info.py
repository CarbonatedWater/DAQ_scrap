import os
import sys
import json
import sqlite3
import Upload
import re

PATH_DB = './db/program.db'


def update_program_base_info() -> list:
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

    return programs
