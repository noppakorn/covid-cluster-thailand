import datetime

def datebd_today() -> list :
    dto = datetime.datetime.now()
    return [dto.day, dto.month, dto.year+543]
