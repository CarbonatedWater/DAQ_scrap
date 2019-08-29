# 콘텐츠 수집 정보 클래스

class ProgramInfo:
    def __init__(self, title, ch, on_day, on_time, cycle, description):
        self.id = ID
        self.title = title
        self.ch = ch
        self.on_day = on_day
        self.on_time = on_time
        self.cycle = cycle
        self.description = description

    
class ContentInfo(ProgramInfo):
    def __init__(self, air_num, con_title, air_date, preview_img, preview_mov):
        self.air_num = air_num
        self.con_title = con_title
        self.air_date = air_date
        self.preview_img = preview_img
        self.preview_mov = preview_mov
