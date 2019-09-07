
get_thisweek_air_info = """
SELECT * FROM contents WHERE air_date >= '{}' AND air_date <= '{}' ORDER BY air_date;
"""
get_program_air_num = "SELECT air_num FROM contents WHERE id = {} ORDER BY air_num DESC LIMIT 1;"

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
air_date = {}, 
air_num = {},
title =  '{}', 
preview_img = '{}', 
preview_mov = '{}', 
description = "{}" 
WHERE id = {} AND air_num = {} AND air_date = '{}';
"""
