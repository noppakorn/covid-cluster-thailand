import datetime
import difflib
from typing import Union


def datebd_today() -> list :
    """
    Return "DDMMYY" in Buddhist year
    """
    dto = datetime.datetime.now()
    return [dto.day, dto.month, dto.year+543]

def bdday_to_date(bdday : str) -> str :
    """
    Convert Buddhist year "DDMMYY" to "YYYY-MM-DD"
    """
    if len(bdday) != 6 : 
        print("Buddhist Date must be 6 digits")
        raise ValueError
    # Convert 2 digit buddhist year to 4 digit year
    year = 1957 + int(bdday[-2:])
    return f"{year}-{bdday[2:4]}-{bdday[:2]}"

def find_similar_word(word : str, template_word : Union[list,set]) -> str :
    """
    Find similar word in template_word using difflib
    Return the most similar word if there are no close matches return word.
    """
    tmp = difflib.get_close_matches(word, template_word)
    if len(tmp) == 0 : return word
    else : return tmp[0]

def district_correction(district_th : str, province_th : str, province_to_district : dict) -> str :
    """
    Correct district by getting the district name of that province.
    Use find_similar_word to compared.
    Return district if can find province and can correct
    Otherwise return district_th back without any change
    """
    if province_th in province_to_district:
        province_to_district = province_to_district[province_th].keys()
        return find_similar_word(district_th, province_to_district)
    return district_th

def district_th_to_en(district_th : str, province_th : str, province_to_district : dict) -> str :
    """
    Use province to find all of the district in that province from file "province_to_district_file"
    Then convert the district in Thai to English
    Return district name english if district name exists otherwise, return None
    """
    if province_th in province_to_district :
        map_district_th_to_en = province_to_district[province_th]
    else :
        print("Invalid Province :", province_th)
        return None

    if district_th in map_district_th_to_en :
        return map_district_th_to_en[district_th]
    else :
        print("Can't convert district to English:" ,district_th)
        return None
    