import requests
import os

def download(pdf_url : str, pdf_out_path : str) -> bool :
    req = requests.get(pdf_url)
    if req.status_code == 404 : 
        return False

    with open(pdf_out_path, "wb+") as fout :
        fout.write(req.content)
        return True

def ensure_pdf(datebd : str) -> bool :
    day,month,year = datebd[:2],datebd[2:4],datebd[-2:]
    file_name = f"{str(day).zfill(2)}{str(month).zfill(2)}{str(year)[-2:]}.pdf"
    pdf_path = os.path.join("../pdf", file_name)
    if not os.path.exists(pdf_path) :
        pdf_url = f"https://media.thaigov.go.th/uploads/public_img/source/{file_name}"
        pdf = download(pdf_url,pdf_path)
        if pdf : print("Downloaded:", file_name)
        return pdf
    return True