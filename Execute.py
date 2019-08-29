import os
import sys
import json
import sqlite3
import time
import random
from datetime import datetime, timedelta
from scrap import sbs, jtbc, ebs, kbs, mbc
import Upload


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
        self.conn = sqlite3.connect(self.PATH_DB)
        self.cur = self.conn.cursor()
        print("===== LOG {} =====".format(self.TODAY))


    # 방영정보 가져오기
    def get_content(self):
        self.cur.execute("SELECT * FROM contents WHERE air_date >= '{}' ORDERY BY air_date;".format(self.THISWEEK_DATE))
        return self.cur.fetchall()


    # 스크랩 / DB에 저장된 직전 정보와 비교 후 DB 인서트
    def content_check(self, ch) -> int:
        new_content_cnt = 0
        # 1. 스크랩할 프로그램 리스트 추출
        if ch != 'all':
            self.cur.execute("SELECT id, title, ch, url FROM programs WHERE ch = '{}';".format(ch))
        else:
            self.cur.execute("SELECT id, title, ch, url FROM programs;")
        LST_PROGRAMS = self.cur.fetchall()

        for prog in LST_PROGRAMS:
            time.sleep(random.randint(3, 8))
            print('===== prog: {}'.format(prog))
            ID = prog[0]
            NAME = prog[1]
            CH = prog[2]
            URL = prog[3]
            # 프로그램 방영일 추출
            self.cur.execute("SELECT on_day FROM programs WHERE id = {};".format(ID))
            tmp = self.cur.fetchone()
            air_dates = tmp[0].split(',')
            print("===== air date: {}".format(air_dates))
            # 방영정보 스크랩
            results = self.SCRAPER[CH](NAME, URL, air_dates, self.WEEK)
            # 프로그램 회차 추출
            self.cur.execute("SELECT air_num FROM contents WHERE id = {} ORDER BY air_num DESC LIMIT 1;".format(ID))
            tmp = self.cur.fetchone()
            print("===== air No.: {}".format(tmp))
            for result in results:
                if (tmp is None) or (int(result['air_num']) > tmp[0]):
                    print('===== new scraped result: {}'.format(result))
                    null_items = []
                    for k, v in result.items():
                        if v is None:
                            null_items.append(k)
                            result[k] = 'NULL'
                        if k == 'title':
                            result[k] = v
                    insert_columns = [col for col in list(result.keys()) if col not in null_items]
                    insert_values = ['%s' % result[x] if x != 'air_num' else result[x] for x in insert_columns]
                    INSERT_QUERY = "INSERT INTO contents (id, {}) VALUES (?, {}?)".format((", ").join(insert_columns), "?, " * (len(insert_values) - 1))
                    print(INSERT_QUERY)
                    final_insert_values = tuple([ID] + insert_values)
                    print(final_insert_values)
                    self.cur.execute(INSERT_QUERY, (final_insert_values))
                    self.conn.commit()
                    new_content_cnt += 1

        return new_content_cnt



if __name__ == "__main__":
    updater = Updater()
    # 1. 프로그램 정보 체크
    new_info_cnt = updater.content_check(sys.argv[1])    
    print('===== scraping completed! new preview: {}'.format(new_info_cnt))
    # 2. 페이지 생성
    if new_info_cnt > 0:
        new_contents = updater.get_content()
        Upload.thisweek_html(new_contents, './pages')
    
    updater.cur.close()
    updater.conn.close()
