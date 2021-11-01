#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import IntEnum
import numpy as np
import io
import zipfile
import os
import requests
import re
import csv


import time



# Kromě vestavěných knihoven (os, sys, re, requests …) byste si měli vystačit s: gzip, pickle, csv, zipfile, numpy, matplotlib, BeautifulSoup.
# Další knihovny je možné použít po schválení opravujícím (např ve fóru WIS).


class DataDownloader:
    """ TODO: dokumentacni retezce 

    Attributes:
        headers    Nazvy hlavicek jednotlivych CSV souboru, tyto nazvy nemente!  
        regions     Dictionary s nazvy kraju : nazev csv souboru
    """

    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
               "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
               "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a"]



    regions = {
        "PHA": "00",
        "STC": "01",
        "JHC": "02",
        "PLK": "03",
        "ULK": "04",
        "HKK": "05",
        "JHM": "06",
        "MSK": "07",
        "OLK": "14",
        "ZLK": "15",
        "VYS": "16",
        "PAK": "17",
        "LBK": "18",
        "KVK": "19",
    }

    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pkl.gz"):
        self.folder = folder
        self.url = url
        self.cache_filename = cache_filename

    def download_data(self):
        if not os.path.exists(f"./{self.folder}"):
            os.makedirs(self.folder)
        resp = requests.get(self.url)
        zip_files = re.findall("data/[^.]*\.zip", resp.text)
        for zip_file in zip_files:
            with requests.get(self.url+zip_file, stream=True) as r:
                with open("./"+self.folder+"/"+zip_file.split("/")[-1], "wb") as fd:
                    for chunk in r.iter_content(chunk_size=128, decode_unicode=True):
                        fd.write(chunk)

    def get_cumulated_data_zips(self):
        all_zip_files = os.listdir("./"+self.folder)
        cumulated_data_zips = list(filter(lambda file: re.match(
            ".*rok.*\.zip", file) or file == "data-gis-2020.zip" or file == "datagis2016.zip", all_zip_files))
        cumulated_data_zips.append(
            list(filter(lambda file: re.match(".*2021\.zip", file), all_zip_files))[-1])
        return cumulated_data_zips

    def parse_region_data(self, region):
        if region not in self.regions.keys():
            raise ValueError("Specified region does not exist")
        cumulated_data_zips = self.get_cumulated_data_zips()
        if(len(cumulated_data_zips) != 6):
            self.download_data()
            cumulated_data_zips = self.get_cumulated_data_zips()


        region_dict = dict.fromkeys(self.headers)
        for key in region_dict:
            region_dict[key] = []
            region_dict["region"] = []
        for file in cumulated_data_zips:
            # open zip archive
            with zipfile.ZipFile(f"./{self.folder}/{file}", 'r') as zip:
                with zip.open(self.regions[region]+".csv", 'r') as csvfile:  # open region csv file
                    csvreader = csv.DictReader(io.TextIOWrapper(csvfile,"cp1250"), self.headers, delimiter=';')
                    for csvline in csvreader:
                        for key in csvline:
                            region_dict[key].append(csvline[key])
        for key in region_dict:
            try:
              region_dict[key] = np.array(region_dict[key], dtype=int)
            except:
                try:
                    region_dict[key] = np.array(region_dict[key], dtype=float)
                except:
                    if(key != "p2a"):
                        region_dict[key] = np.array(region_dict[key], dtype=str)
            region_dict["p2a"] = np.array(region_dict["p2a"], dtype=np.datetime64)
            region_dict["region"].append(region)
        
        
        return region_dict


    def get_dict(self, regions=None):
        pass


if __name__ == "__main__":
    downloader = DataDownloader()
    downloader.parse_region_data("PHA")

    # downloader.parse_region_data("PHA")
# TODO vypsat zakladni informace pri spusteni python3 download.py (ne pri importu modulu)
