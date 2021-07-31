from process_pdf import *

if __name__ == "__main__":
    now = datetime.datetime.now()
    date_range = [now - datetime.timedelta(days=x) for x in range(1,now.day+1)]
    for date in date_range: extract_cluster_at_date(date)
