import os
import sys
import json
import sqlite3
import time
import random
from datetime import datetime, timedelta
from scrap import sbs, jtbc, ebs, kbs, mbc
import Upload
import query


class Updater:
    WEEK = ("월", "화", "수", "목", "금", "토", "일")
    PATH_DB = './db/program.db'
    SCRAPER = {
        'SBS': sbs.scrap, 
        'JTBC': jtbc.scrap, 
        'EBS': ebs.scrap, 
        'MBC': mbc.scrap, 
        'KBS': kbs.scrap
    }

    def __init__(self):
        self.TODAY = datetime.today().date()
        self.TODAY_DATE = self.TODAY.weekday()
        self.THISWEEK_DATE = self.TODAY - timedelta(self.TODAY.weekday())
        self.THISWEEK_LAST_DATE = self.TODAY + timedelta(days=6)
        self.conn = sqlite3.connect(self.PATH_DB)
        self.cur = self.conn.cursor()
        print("===== LOG {} =====".format(self.TODAY))


    # 방영정보 가져오기
    def get_content(self):
        self.cur.execute(query.get_thisweek_air_info.format(
            self.THISWEEK_DATE, self.THISWEEK_LAST_DATE)
        )
        return self.cur.fetchall()


    # 스크랩 / DB에 저장된 직전 정보와 비교 후 DB 인서트
    def content_check(self, ch) -> int:
        new_content_cnt = 0
        # 1. 스크랩할 프로그램 리스트 추출
        if ch != 'all':
            self.cur.execute("SELECT id, title, ch, url FROM programs WHERE ch = '{}';".format(ch))
        else:
            self.cur.execute("SELECT id, title, ch, url FROM programs;")
        lst_programs = self.cur.fetchall()

        for prog in lst_programs:
            if prog[1] == "추적 60분": # 방영 종료
                continue
            time.sleep(random.randint(3, 8))
            print('===== prog: {}'.format(prog))
            _id = prog[0]
            name = prog[1]
            ch = prog[2]
            url = prog[3]
            # 프로그램 방영일 추출
            self.cur.execute("SELECT on_day FROM programs WHERE id = {};".format(_id))
            tmp = self.cur.fetchone()
            air_dates = tmp[0].split(',')
            print("===== air date: {}".format(air_dates))
            # 방영정보 스크랩
            results = self.SCRAPER[ch](name, url, air_dates, self.WEEK)
            # 프로그램 회차 추출
            self.cur.execute(query.get_program_air_num.format(_id))
            tmp = self.cur.fetchone()
            print("===== air No.: {}".format(tmp))
            for result in results:
                #print('===== new scraped result: {}'.format(result))
                null_items = []
                for k, v in result.items():
                    if v is None:
                        null_items.append(k)
                        result[k] = 'NULL'
                    if k == 'title':
                        result[k] = v
                insert_columns = [col for col in list(result.keys()) if col not in null_items]
                insert_values = ['%s' % result[x] if x != 'air_num' else result[x] for x in insert_columns]
                if (tmp is None) or (int(result['air_num']) > tmp[0]):
                    # 기존에 없던 정보는 insert로 추가    
                    insert_query = query.insert_new_air_info.format((", ").join(insert_columns), "?, " * (len(insert_values) - 1))
                    print(insert_query)
                    final_insert_values = tuple([_id] + insert_values)
                    #print(final_insert_values)
                    self.cur.execute(insert_query, (final_insert_values))
                elif (int(result['air_num']) == tmp[0]):
                    # 기존에 있던 정보는 업데이트
                    update_query = query.update_new_air_info.format(
                        result['air_date'], result['air_num'], result['title'], 
                        result['preview_img'], result['preview_mov'], result['description'], 
                        _id, result['air_num'], result['air_date'] # WHERE 조건
                    )
                    print(update_query)
                    self.cur.execute(update_query)
                else:
                    pass
                
                self.conn.commit()
                new_content_cnt += 1

        return new_content_cnt


    # 프로그램 정보 가져오기
    def get_program_info(self, program_name):
        self.cur.execute(query.get_program_air_info_10.format(program_name))
        return self.cur.fetchall()


if __name__ == "__main__":
    updater = Updater()
    # 1. 프로그램 정보 체크
    #new_info_cnt = updater.content_check('EBS')
    new_info_cnt = updater.content_check(sys.argv[1])
    print('===== scraping completed! new preview: {}'.format(new_info_cnt))
    # 2. 이번주 방영정보 페이지 생성
    if new_info_cnt > 0:
        new_contents = updater.get_content()
        Upload.thisweek_html(new_contents, 'week')
    # 3. 프로그램별 방영리스트 페이지 생성
    with open('./program_img_id.json', 'r') as f:
        program_img_id = json.load(f)
    for program in program_img_id.items():
        program_data = updater.get_program_info(program[0])
        Upload.program_detail_html(program_data, program[1])
        print("===== {} air page is created!".format(program[0]))

    updater.cur.close()
    updater.conn.close()
