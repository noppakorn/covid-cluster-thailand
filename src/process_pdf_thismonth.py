from process_pdf import *

if __name__ == "__main__":
    now = datetime.datetime.now()
    date_range = pd.date_range(start=now.replace(day=1), end=now)
    for date in date_range: 
        extract_cluster_at_date(date)
