"""
TVN 프로그램 수집
"""

from scrap import utils

def scrap(prog_name, url, original_air_date, week):
    # DAUM 정보 보완
    result_daum = utils.get_daum_info(prog_name)
    if not(result_daum):
        return None
    else:
        result = {
            'air_date': result_daum['air_date'], 
            'air_num': result_daum['air_num'], 
            'title': result_daum['sub_title'].replace('"', "'"), 
            'preview_img': result_daum['preview_img'], 
            'preview_mov': "", 
            'description': result_daum['desc'].replace('"', "'")
        }

        return [result]
