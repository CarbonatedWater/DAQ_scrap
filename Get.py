'''
프로그램 정보 가져오는 함수 모음
'''

from urllib.request import urlopen
import re
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import time


Id = '82072'

base_url = 'http://movie.daum.net/tv/episode?tvProgramId='

resp = urlopen(base_url + Id)

soup = BeautifulSoup(resp, 'html.parser')


turn = ''
day = '' 
due_date = '' # http://movie.daum.net/tv/schedule?tvProgramId=
title = ''


'''
DataBase Structure
'''

key_info = {
    'chanel':{
        'PD수첩':'KBS1', 
        '그것이알고싶다':'SBS'
    }, 
    'air_day':{
        'PD수첩':'tue', 
        '그것이알고싶다':'sat'
    }, 
    'category':{
        'PD수첩':'시사', 
        '그것이알고싶다':'시사'
    }
}

contents = {
    
}