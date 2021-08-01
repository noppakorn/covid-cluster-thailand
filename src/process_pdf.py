import pandas as pd
import numpy as np
import pdfplumber
import json
import os
import re
import datetime
from utils import bdday_to_date,district_correction,\
                  district_th_to_en,find_similar_word
from get_pdf import ensure_pdf


THAIMONTH_TO_MONTH = {
    "ม.ค.": "01",
    "ก.พ.": "02",
    "มี.ค.": "03",
    "เม.ย.": "04",
    "พ.ค.": "05",
    "มิ.ย.": "06",
    "ก.ค.": "07",
    "ส.ค.": "08",
    "ก.ย.": "09",
    "ต.ค.": "10",
    "พ.ย.": "11",
    "ธ.ค.": "12",
}
PROVINCE_TH_TO_EN = json.load(open("../province_details/province-th-to-en.json", encoding="utf-8"))
PROVINCE_TO_DISTRICT = json.load(open("../province_details/th-province-district.json", encoding="utf-8"))

def find_cluster_page(pdf_path : str) -> set : 
    pages = set()
    with pdfplumber.open(pdf_path) as pdf:
        for page_no in range(len(pdf.pages)):
            page_text = pdf.pages[page_no].extract_text(x_tolerance=3, y_tolerance=3)
            if page_text == None :
                continue
            page_text = page_text.split("\n")
            if "การระบาดที่พบในจังหวัดที่มีรายงานผู้ป่วยเพิ่มขึ้น" in page_text[0] :
                pages.add(page_no)
    return pages

def extract_cluster(pdf_path : str, pages : set) -> pd.DataFrame:
    df = pd.DataFrame()
    with pdfplumber.open(pdf_path) as pdf:
        for i in pages:
            pdf_page = pdf.pages[i]
            table = pdf_page.extract_table(table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"})[1:]
            df = df.append(table).reset_index(drop=True)

    df = df.rename(columns={
        0 : "PROVINCE_TH",
        1 : "DISTRICT_TH",
        2 : "PlaceOfOutbreak",
        3 : "StartDate",
        4 : "NewCases",
        5 : "Total"
    })
    df = df.replace(r'^\s*$', np.nan, regex=True)
    df["PROVINCE_TH"] = df["PROVINCE_TH"].ffill()
    df["Total"] = df["Total"].ffill()
    df = df.dropna().reset_index(drop=True)
    df["Total"] = df["Total"].str.split(expand=True)[0]
    df_startdate = df["StartDate"].str.split(expand=True)
    df_startdate[1] = df_startdate[1].replace(THAIMONTH_TO_MONTH)
    df_startdate[2] = "2021"
    df["StartDate"] = df_startdate[2] + "-" + df_startdate[1] + "-" + df_startdate[0].str.zfill(2)

    # Replace newline in cell with space
    regex_newline = re.compile(r"\n")
    df.replace(regex_newline, " ", inplace=True)

    # Correction for "ำ" cannot be read properly from PDF
    regex_aum = re.compile(r" า")
    df["PlaceOfOutbreak"].replace(regex_aum, "ำ", inplace=True)
    df["DISTRICT_TH"].replace(regex_aum, "ำ", inplace=True)

    # Province name correction (Will cover "ำ" case as well)
    province_th = PROVINCE_TH_TO_EN.keys()
    df_invalid_province = df[(~df["PROVINCE_TH"].isin(province_th))]
    if len(df_invalid_province) > 0 :
        # Replace by finding most similar province
        df_invalid_correted = df_invalid_province["PROVINCE_TH"].apply(lambda pro : find_similar_word(pro, province_th))
        df.update(df_invalid_correted)
        print("Uncorrectable Province:")
        print(df[(~df["PROVINCE_TH"].isin(province_th))])

    df["PROVINCE_EN"] = df["PROVINCE_TH"].map(PROVINCE_TH_TO_EN)
    df["PROVINCE_EN"] = df["PROVINCE_EN"].where(pd.notnull(df["PROVINCE_EN"]), None)

    # District name correction (Just in case)

    df["DISTRICT_TH"] = df.apply(lambda row : district_correction(row["DISTRICT_TH"], row["PROVINCE_TH"], PROVINCE_TO_DISTRICT), axis=1)
    # Add district in english
    df["DISTRICT_EN"] = df.apply(lambda row : district_th_to_en(row["DISTRICT_TH"], row["PROVINCE_TH"], PROVINCE_TO_DISTRICT), axis=1)

    regex_comma = re.compile(r",")
    df[["NewCases", "Total"]] = df[["NewCases", "Total"]].replace(regex_comma,"").astype(int)

    return df[["PROVINCE_TH", "PROVINCE_EN", "DISTRICT_TH", "DISTRICT_EN", "PlaceOfOutbreak", "StartDate", "NewCases", "Total"]]

def extract_cluster_at_date(dto : datetime.datetime) -> bool :
    file_name = f"{str(dto.day).zfill(2)}{str(dto.month).zfill(2)}{str(dto.year+543)[-2:]}.pdf"
    pdf_path = os.path.join("../pdf", file_name)

    ensured = ensure_pdf(file_name.split(".")[0])

    if ensured : 
        print("Processing:", pdf_path)
        file_name = pdf_path.split("/")[-1].split(".")[0]
        cluster_page = find_cluster_page(pdf_path)
        if len(cluster_page) > 0 :
            df = extract_cluster(pdf_path, cluster_page)
            if not os.path.exists("../json") : os.mkdir("../json")
            json_dict = {
                "UpdatedDate": str(dto.date()),
                "ClusterData": df.to_dict(orient="records")
            }
            with open(f"../json/cluster-data-{bdday_to_date(file_name)}.json", "w+", encoding="utf-8") as json_file :
                json.dump(json_dict, json_file, ensure_ascii=False, indent=2)
        else : 
            print("Cluster page not found:", pdf_path)
            return False

    else :
        print("PDF not avalible:", file_name)
        return False

    return True


if __name__ == "__main__":
    result = extract_cluster_at_date(datetime.datetime.now())
