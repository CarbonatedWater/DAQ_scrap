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
    with open("./program_img_id.json", 'r') as f:
        image_urls = json.load(f)

    # tuple to list
    programs = []
    for item in tbl:
        programs.append(list(item))

    # 디스크립션의 개행기호 오류 수정
    for program in programs:
        print(program[6])
        program[6] = program[6].replace('\\n', '\n')
        print(program[6])
        # image Url 추가
        program.append(image_urls[program[1]])

    return programs


def add_program_img(program_name: str, img_name: str):
    with open("./program_img_id.json", 'r') as f:
        image_urls = json.load(f)

    image_urls[program_name] = img_name
    print(image_urls)

    with open("./program_img_id.json", 'w') as f:
        json.dump(image_urls, f)
