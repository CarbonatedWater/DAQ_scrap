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

    # 디스크립션의 개행기호 오류 수정
    for program in programs:
        print(program[6])
        program[6] = program[6].replace('\\n', '\n')
        print(program[6])

    return programs
