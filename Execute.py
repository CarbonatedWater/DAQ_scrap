import sys
import json
import sqlite3
import time
import random
from datetime import datetime, timedelta
from scrap import sbs, jtbc, ebs, kbs, mbc, tvn
import Upload
import query
import fcm


class Updater:
    WEEK = ("월", "화", "수", "목", "금", "토", "일")
    PATH_DB = './db/program.db'
    SCRAPER = {
        'SBS': sbs.scrap, 
        'JTBC': jtbc.scrap, 
        'EBS': ebs.scrap, 
        'MBC': mbc.scrap, 
        'KBS': kbs.scrap, 
        'TVN': tvn.scrap
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
    def content_check(self, ch_command, program_img_id) -> int:
        new_content_cnt = 0
        # 1. 스크랩할 프로그램 리스트 추출
        if ch_command != 'all':
            self.cur.execute(f"{query.get_program_info} WHERE ch = '{ch_command}';")
        else:
            self.cur.execute(query.get_program_info + ";")
        lst_programs = self.cur.fetchall()

        for prog in lst_programs:
            if prog[4] == 0: # 방영 종료
                continue
            time.sleep(random.randint(3, 8))
            print(f'===== prog: {prog}')
            _id = prog[0]
            name = prog[1]
            ch = prog[2]
            url = prog[3]
            # 프로그램 방영일 추출
            self.cur.execute(f"SELECT on_day FROM programs WHERE id = {_id};")
            tmp = self.cur.fetchone()
            air_dates = tmp[0].split(',')
            print(f"===== air date: {air_dates}")
            # 방영정보 스크랩
            results = self.SCRAPER[ch](name, url, air_dates, self.WEEK)
            if results is None:
                continue
            # 프로그램 회차 추출
            self.cur.execute(query.get_program_air_num_date.format(_id))
            tmp = self.cur.fetchone()
            print(f"===== air No. & date: {tmp} & result: {results}")
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
                try:
                    new_air_num = int(result['air_num'])
                except Exception as e:
                    print('===== error: ', e)
                    new_air_num = ''
                if tmp is None or datetime.strptime(result['air_date'], '%Y-%m-%d') > datetime.strptime(tmp[1], '%Y-%m-%d'):
                    print('===== new data!')
                    # 기존에 없던 정보는 insert로 추가    
                    insert_query = query.insert_new_air_info.format((", ").join(insert_columns), "?, " * (len(insert_values) - 1))
                    print(insert_query)
                    final_insert_values = tuple([_id] + insert_values)
                    #print(final_insert_values)
                    self.cur.execute(insert_query, (final_insert_values))
                    # 앱에 Push 알림
                    push_message = "%s 방영정보가 업데이트 되었습니다!" % name
                    topic = program_img_id[name]
                    print(f'===== topic: {topic} | message: {push_message}')
                    push_result = fcm.push_service.notify_topic_subscribers(topic_name=topic, message_body=push_message)
                    print(push_result)
                elif new_air_num == tmp[0]:
                    print('===== air num equals!')
                    # 기존에 있던 정보는 업데이트
                    update_query = query.update_new_air_info.format(
                        result['air_date'], new_air_num, result['title'], 
                        result['preview_img'], result['preview_mov'], result['description'], 
                        _id, result['air_num'], result['air_date'] # WHERE 조건
                    )
                    print(update_query)
                    self.cur.execute(update_query)
                else:
                    print('===== pass')
                    pass
                
                self.conn.commit()
                new_content_cnt += 1

        return new_content_cnt


    # 프로그램 정보 가져오기
    def get_program_info(self, program_name):
        self.cur.execute(query.get_program_air_info_10.format(program_name))
        return self.cur.fetchall()

    def get_program_ch(self, program_id):
        self.cur.execute(query.get_program_url.format(program_id))
        return self.cur.fetchall()
    

    # 프로그램 방영시간 기정보 가져오기
    def get_program_air_time(self):
        self.cur.execute(query.get_program_air_time)
        air_time_list = [x[0] for x in self.cur.fetchall()]
        air_time_result = []
        for i, item in enumerate(air_time_list):
            tmp = item.split()
            hour = int(tmp[1].replace('시', ''))
            if tmp[0] == '오후':
                hour += 12
            elif tmp[0] == '오전' and hour == 12:
                hour == '00'
            hour = str(hour)
            try:
                minute = tmp[2].replace('분', '')
                if len(minute) < 2:
                    minute = '0'+str(minute)
            except:
                minute = '00'
            air_time_result.append(
                (air_time_list[i], hour+minute)
            )
        return air_time_result


if __name__ == "__main__":
    updater = Updater()
    # 0. 프로그램 이미지 파일명 로딩
    with open('./program_img_id.json', 'r') as f:
        program_img_id = json.load(f)
    # 1. 프로그램 정보 체크
    new_info_cnt = updater.content_check(sys.argv[1], program_img_id)
    print(f'===== scraping completed! new preview: {new_info_cnt}')
    # 2. 이번주 방영정보 페이지 생성
    if new_info_cnt > 0:
        new_contents = updater.get_content()
        # 방영시간 정보 추출
        air_times = updater.get_program_air_time()
        print(air_times)
        Upload.air_html(new_contents, air_times, 'week', None, None)
    # 3. 프로그램별 방영리스트 페이지 생성
    for program in program_img_id.items():
        program_data = updater.get_program_info(program[0])
        program_url = updater.get_program_ch(program_data[0][0])
        Upload.air_html(program_data, air_times, program[1], program[0], program_url[0][0])
        print(f"===== {program[0]} air page is created!")

    updater.cur.close()
    updater.conn.close()
