import datetime
import difflib


def datebd_today() -> list :
    dto = datetime.datetime.now()
    return [dto.day, dto.month, dto.year+543]

def bdday_to_date(bdday : str) -> str :
    if len(bdday) != 6 : 
        print("Buddhist Date must be 6 digits")
        raise ValueError
    year = 1957 + int(bdday[-2:])
    return f"{year}-{bdday[2:4]}-{bdday[:2]}"

def find_similar_word(word : str, template_word : set) -> str :
    tmp = difflib.get_close_matches(word, template_word)
    if len(tmp) == 0 : return word
    else : return tmp[0]
