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
import pickle
import gzip
import time
from bs4 import BeautifulSoup


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
        self.regions_dicts_cache = dict.fromkeys(self.regions)

    def download_data(self):
        if not os.path.exists(f"./{self.folder}"):
            os.makedirs(self.folder)
        resp = requests.get(self.url)
        zip_files = []
        soup = BeautifulSoup(resp.text, 'html.parser')
        rows = soup.find_all("tr")
        for table_row in rows:
            last_button = table_row.find_all("button")[-1]
            btntext = str(last_button)
            zip_files.append(re.search("data/.*\.zip", btntext).group(0))

        for zip_file in zip_files:
            #need only last zip in year - skip others
            with requests.get(self.url+zip_file, stream=True) as r:
                with open("./"+self.folder+"/"+zip_file.split("/")[-1], "wb") as fd:
                    for chunk in r.iter_content(chunk_size=128, decode_unicode=True):
                        fd.write(chunk)

    def get_folder_zip_files(self):
        folder_files = os.listdir("./"+self.folder)
        zip_files =  list(filter(lambda file: re.match(".*\.zip", file),folder_files))
        return zip_files

    def parse_region_data(self, region):
        if region not in self.regions.keys():
            raise ValueError("Specified region does not exist")
       
        zip_files = self.get_folder_zip_files()
        if(len(zip_files) != 6):
            self.download_data()
            zip_files = self.get_folder_zip_files()

        region_dict = dict.fromkeys(self.headers)
        for key in region_dict:
            region_dict[key] = []
        region_dict["region"] = []
        for file in zip_files:
            # open zip archive
            with zipfile.ZipFile(f"./{self.folder}/{file}", 'r') as zip:
                # open region csv file
                with zip.open(self.regions[region]+".csv", 'r') as csvfile:
                    csvreader = csv.DictReader(io.TextIOWrapper(
                        csvfile, "cp1250"), self.headers, delimiter=';')
                    for csvline in csvreader:
                        for key in csvline:
                            region_dict[key].append(csvline[key])
                        region_dict["region"].append(region)
        for key in region_dict:
            try:
              region_dict[key] = np.array(region_dict[key], dtype=int)
            except:
                try:
                    region_dict[key] = np.array(region_dict[key], dtype=float)
                except:
                    if(key != "p2a"):
                        region_dict[key] = np.array(
                            region_dict[key], dtype=str)
            # region_dict["p2a"] = np.array(region_dict["p2a"], dtype=np.datetime64)
        return region_dict

    def get_dict(self, regions=None):

        regions_dict = {}
        for region in regions:
            # check if region is in instance attr
            if self.regions_dicts_cache[region] == None:
                # check if cache file exists
                region_cache_file_name = f"./{self.folder}/{self.cache_filename.replace('{}', region)}"
                if os.path.exists(region_cache_file_name ):
                    with gzip.open(region_cache_file_name , "rb") as pickle_cache:
                        self.regions_dicts_cache[region] = pickle.load(pickle_cache)
                else:
                    region_data =  self.parse_region_data(region)
                    with gzip.open(region_cache_file_name , 'wb') as f:
                        pickle.dump(region_data,f)
                    self.regions_dicts_cache[region] = region_data
            #result dict is empty
            if not regions_dict:
                regions_dict = dict(self.regions_dicts_cache[region])
            else:
                for key in regions_dict:
                    regions_dict[key] = np.concatenate((regions_dict[key], self.regions_dicts_cache[region][key]))
        return regions_dict


if __name__ == "__main__":
    downloader = DataDownloader()
    c = downloader.get_dict(["VYS", "KVK", "JHM"])
    print("Kraje: Vysočina, Karlovarský, Jihomoravský")
    print("Počet záznamů: " + str(len(c["p1"])))
    print("Sloupce: " + ', '.join(downloader.headers))
    
    # downloader.parse_region_data("PHA")
# TODO vypsat zakladni informace pri spusteni python3 download.py (ne pri importu modulu)
