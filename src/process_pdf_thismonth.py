from process_pdf import *

if __name__ == "__main__":
    if not os.path.exists("../json") : os.mkdir("./json")

    day,month,year = datebd_today()
    for d in range(1, day+1):
        file_name = f"{str(d).zfill(2)}{str(month).zfill(2)}{str(year)[-2:]}.pdf"
        pdf_path = os.path.join("../pdf", file_name)

        ensured = ensure_pdf(file_name.split(".")[0])

        if ensured : 
            print("Processing:", pdf_path)
            file_name = pdf_path.split("/")[-1].split(".")[0]
            cluster_page = find_cluster_page(pdf_path)
            if len(cluster_page) > 0 :
                df = extract_cluster(pdf_path, cluster_page)
                if not os.path.exists("../json") : os.mkdir("../json")
                df.to_json(f"../json/cluster-data-{bdday_to_date(file_name)}.json", force_ascii=False, orient="records", indent=2)
            else : 
                print("Cluster page not found:", pdf_path)

        else :
            print("PDF not avalible:", file_name)
