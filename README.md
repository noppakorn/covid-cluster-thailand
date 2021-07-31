# Thailand COVID-19 Cluster Data Extraction
![fetch-cluster-today](https://github.com/noppakorn/covid-cluster-thailand/actions/workflows/fetch-cluster-today.yml/badge.svg)
# About
- Extract Clusters from [Thailand Daily COVID-19 briefing PDF](https://www.thaigov.go.th/news/contents/details/29299)
- Download latest data [Here](https://raw.github.com/wiki/noppakorn/covid-cluster-thailand/cluster-data.json).
- Data will be updated daily at `13:00 (UTC+7)`.
- Historical data is stored in the root of the wiki with the file name `cluster-data-{YYYY}-{MM}-{DD}.json`. For example `cluster-data-2021-07-01.json`.
- Historical data dates back to `2021-07-01`.
# Requirements
- requests
- pandas
- numpy
- pdfplumber
# Data Sources
- [Daily COVID-19 briefing PDF](https://www.thaigov.go.th/news/contents/details/29299)
- [The Humanitarian Data Exchange](https://data.humdata.org/dataset/thailand-administrative-boundaries).
  License : [Creative Commons Attribution for Intergovernmental Organisations](https://data.humdata.org/about/license)
