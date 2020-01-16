
get_program_info = "SELECT id, title, ch, url, on_air FROM programs"

get_thisweek_air_info = """
SELECT * FROM contents WHERE air_date >= '{}' AND air_date <= '{}' ORDER BY air_date;
"""
get_program_air_num_date = "SELECT air_num, air_date FROM contents WHERE id = {} ORDER BY air_num DESC LIMIT 1;"

get_program_air_info_10 = """
    SELECT * FROM contents 
    WHERE id = (SELECT id FROM programs WHERE title = '{}')
    ORDER BY air_date DESC 
    LIMIT 10;
"""

insert_new_air_info = "INSERT INTO contents (id, {}) VALUES (?, {}?)"

update_new_air_info = """
UPDATE contents 
SET 
air_date = '{}', 
air_num = {},
title =  "{}", 
preview_img = '{}', 
preview_mov = '{}', 
description = "{}" 
WHERE id = {} AND air_num = {} AND air_date = '{}';
"""

get_program_air_time = "SELECT on_time FROM programs ORDER BY id;"

"""
새로운 프로그램 정보 등록
INSERT INTO programs 
(id, title, ch, on_day, on_time, cycle, description, on_air, url) 
VALUES 
(19, '다큐 인사이트', 'KBS', '목', '오후 10시', 'week', '소재와 형식을 뛰어넘은 다큐멘터리의 즐거운 뒤집기 <다큐 인사이트> 프로젝트', 1, 'http://program.kbs.co.kr/1tv/culture/docuinsight/pc/index.html');
"""
