import pandas as pd
import numpy as np
import pdfplumber
import json
import os
import re
import datetime
from utils import bdday_to_date, district_correction, \
    district_th_to_en, find_similar_word
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


def find_cluster_page(pdf_path: str) -> set:
    pages = set()
    with pdfplumber.open(pdf_path) as pdf:
        for page_no in range(len(pdf.pages)):
            page_text = pdf.pages[page_no].extract_text(x_tolerance=3, y_tolerance=3)
            if page_text == None:
                continue
            page_text = page_text.split("\n")
            if "การระบาดที่พบในจังหวัดที่มีรายงานผู้ป่วยเพิ่มขึ้น" in page_text[0]:
                pages.add(page_no)
    return pages


def extract_cluster(pdf_path: str, pages: set) -> pd.DataFrame:
    df = pd.DataFrame()
    with pdfplumber.open(pdf_path) as pdf:
        for i in pages:
            pdf_page = pdf.pages[i]
            table = pdf_page.extract_table(
                table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"})[1:]
            df = df.append(table).reset_index(drop=True)

    df = df.rename(columns={
        0: "province_th",
        1: "district_th",
        2: "place_of_outbreak",
        3: "start_date",
        4: "new_cases",
        5: "total"
    })
    df = df.replace(r'^\s*$', np.nan, regex=True)
    df["province_th"] = df["province_th"].ffill()
    df["total"] = df["total"].ffill()
    df = df.dropna().reset_index(drop=True)
    df["total"] = df["total"].str.split(expand=True)[0]
    df_startdate = df["start_date"].str.split(expand=True)
    df_startdate[1] = df_startdate[1].replace(THAIMONTH_TO_MONTH)
    df_startdate[2] = "2021"
    df["start_date"] = df_startdate[2] + "-" + df_startdate[1] + "-" + df_startdate[0].str.zfill(2)

    # Replace newline in cell with space
    regex_newline = re.compile(r"\n")
    df.replace(regex_newline, " ", inplace=True)

    # Correction for "ำ" cannot be read properly from PDF
    regex_aum = re.compile(r" า")
    df["place_of_outbreak"].replace(regex_aum, "ำ", inplace=True)
    df["district_th"].replace(regex_aum, "ำ", inplace=True)

    # Province name correction (Will cover "ำ" case as well)
    province_th = PROVINCE_TH_TO_EN.keys()
    df_invalid_province = df[(~df["province_th"].isin(province_th))]
    if len(df_invalid_province) > 0:
        # Replace by finding most similar province
        df_invalid_correted = df_invalid_province["province_th"].apply(lambda pro: find_similar_word(pro, province_th))
        df.update(df_invalid_correted)
        print("Uncorrectable Province:")
        print(df[(~df["province_th"].isin(province_th))])

    df["province_en"] = df["province_th"].map(PROVINCE_TH_TO_EN)
    df["province_en"] = df["province_en"].where(pd.notnull(df["province_en"]), None)

    # District name correction (Just in case)

    df["district_th"] = df.apply(
        lambda row: district_correction(row["district_th"], row["province_th"], PROVINCE_TO_DISTRICT), axis=1)
    # Add district in english
    df["district_en"] = df.apply(
        lambda row: district_th_to_en(row["district_th"], row["province_th"], PROVINCE_TO_DISTRICT), axis=1)

    regex_comma = re.compile(r",")
    #df[["new_cases", "total"]] =
    df[["new_cases", "total"]] = df[["new_cases", "total"]].replace(regex_comma, "")
    df["new_cases"] = df["new_cases"].str.split(expand=True)[0]
    df[["new_cases", "total"]] = df[["new_cases", "total"]].astype(int)


    return df[
        ["province_th", "province_en", "district_th", "district_en", "place_of_outbreak", "start_date", "new_cases",
         "total"]]


def extract_cluster_at_date(dto: datetime.datetime) -> bool:
    file_name = f"{str(dto.day).zfill(2)}{str(dto.month).zfill(2)}{str(dto.year + 543)[-2:]}.pdf"
    pdf_path = os.path.join("../pdf", file_name)

    ensured = ensure_pdf(file_name.split(".")[0])

    if ensured:
        print("Processing:", pdf_path)
        file_name = pdf_path.split("/")[-1].split(".")[0]
        cluster_page = find_cluster_page(pdf_path)
        if len(cluster_page) > 0:
            df = extract_cluster(pdf_path, cluster_page)
            if not os.path.exists("../json"): os.mkdir("../json")
            json_dict = {
                "updated_date": str(dto.date()),
                "cluster_data": df.to_dict(orient="records")
            }
            with open(f"../json/cluster-data-{bdday_to_date(file_name)}.json", "w+", encoding="utf-8") as json_file:
                json.dump(json_dict, json_file, ensure_ascii=False, indent=2)
        else:
            print("Cluster page not found:", pdf_path)
            return False

    else:
        print("PDF not avalible:", file_name)
        return False

    return True


if __name__ == "__main__":
    result = extract_cluster_at_date(datetime.datetime.now())
