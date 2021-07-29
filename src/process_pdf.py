import pandas as pd
import numpy as np
import pdfplumber
import glob
import os

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
    col2name = {
        0 : "Provinces",
        1 : "District",
        2 : "PlaceOfOutbreak",
        3 : "OutbreakStart",
        4 : "NewCases",
        5 : "TotalInCluster"
    }
    df = pd.DataFrame()
    with pdfplumber.open(pdf_path) as pdf:
        for i in pages:
            pdf_page = pdf.pages[i]
            table = pdf_page.extract_table(table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"})[3:]
            df = df.append(table).reset_index(drop=True)
    df = df.replace(r'^\s*$', np.nan, regex=True)
    df[5] = df[5].ffill()
    df = df.dropna().reset_index(drop=True)
    df[5] = df[5].str.split(expand=True)[0]
    
    use_col2name = {key: values for key,values in col2name.items() if key in df.columns}
    df = df.rename(columns=use_col2name)
    return df

if __name__ == "__main__":
    if not os.path.exists("./json") : os.mkdir("./json")
    for pdf_path in sorted(glob.glob("../pdf/*")):
        print("Processing:", pdf_path)
        file_name = pdf_path.split("/")[-1].split(".")[0]
        cluster_page = find_cluster_page(pdf_path)
        if len(cluster_page) > 0 :
            df = extract_cluster(pdf_path, cluster_page)
            df.to_json(f"json/{file_name}.json", force_ascii=False, orient="records", indent=2)
        else : 
            print("Cluster page not found:", pdf_path)
