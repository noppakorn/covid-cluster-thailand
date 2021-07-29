import requests
import os
from utils import datebd_today

def download(pdf_url : str, pdf_out_folder : str = "../pdf"):
    req = requests.get(pdf_url)
    if req.status_code == 404 : 
        return None

    out_path = os.path.join(pdf_out_folder, pdf_url.split("/")[-1])
    with open(out_path, "wb+") as fout :
        fout.write(req.content)
        return out_path

if __name__ == "__main__":
    if not os.path.exists("../pdf") : os.mkdir("../pdf")
    day, month, year = datebd_today()
    for d in range(1, day):
        file_name = f"{str(d).zfill(2)}{str(month).zfill(2)}{str(year)[-2:]}.pdf"
        PDF_URL_BASE = f"https://media.thaigov.go.th/uploads/public_img/source/{file_name}"
        pdf = download(PDF_URL_BASE)
        if not pdf :
            print("PDF not avalible", file_name)
