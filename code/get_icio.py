"""
This file downloads all available IO-Tables (1995-2010) from the OECD website
(https://www.oecd.org/en/data/datasets/inter-country-input-output-tables.html)
and puts the csv files into the /data/icio/ folder
"""

import requests, zipfile, io, os

url = {'1995-2000':'https://stats.oecd.org/wbos/fileview2.aspx?IDFile=d26ad811-5b58-4f0c-a4e3-06a1469e475c',
       '2001-2005':'https://stats.oecd.org/wbos/fileview2.aspx?IDFile=7cb93dae-e491-4cfd-ac67-889eb7016a4a',
       '2006-2010':'https://stats.oecd.org/wbos/fileview2.aspx?IDFile=ea165bfb-3a85-4e0a-afee-6ba8e6c16052',
       '2011-2015':'https://stats.oecd.org/wbos/fileview2.aspx?IDFile=1f791bc6-befb-45c5-8b34-668d08a1702a',
       '2016-2020':'https://stats.oecd.org/wbos/fileview2.aspx?IDFile=d1ab2315-298c-4e93-9a81-c6f2273139fe'}

def download(url=url):
       counter = 1
       for year,link in url.items():
              if os.path.exists(f'../data/icio/{year.split('-')[0]}_SML.csv'):
                     print(f"Data for {year} already exists (file {counter}/{len(url)})")
              else:
                     r = requests.get(link)
                     z = zipfile.ZipFile(io.BytesIO(r.content))
                     z.extractall('../data/icio/')
                     print(f"Data for {year} downloaded (file {counter}/{len(url)})")
              counter += 1