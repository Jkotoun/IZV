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


    col_data_types = [int, int, int, np.datetime64, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, 
    int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, float, 
    float, float, float, float, float, str, str, int, str, str, str, str, str, str, int, int, str, int, str]
                  
    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pkl.gz"):
        """Init creates folder if it does not exist
        'url' - url from where zip files should be downloaded
        'folder' - folder relative path to store zip files
        'cache_filename' - name of cache file names for region cache files. Should contain {}, so it can be replaced with name of region"""
        self.folder = folder
        self.url = url
        self.cache_filename = cache_filename
        os.makedirs(self.folder, exist_ok=True)
        self.regions_dicts_cache = dict.fromkeys(self.regions)

    def download_data(self):
        """Downloads zip files from end of each year from url given by url property"""
        resp = requests.get(self.url)
        zip_files = []
        soup = BeautifulSoup(resp.text, 'html.parser')
        rows = soup.find_all("tr")
        for table_row in rows:
            last_button = table_row.find_all("button")[-1]
            btntext = str(last_button)
            zip_files.append(re.search("data/.*\.zip", btntext).group(0))

        for zip_file in zip_files:
            # need only last zip in year - skip others
            with requests.get(self.url+zip_file, stream=True) as r:
                with open("./"+self.folder+"/"+zip_file.split("/")[-1], "wb") as fd:
                    for chunk in r.iter_content(chunk_size=128, decode_unicode=True):
                        fd.write(chunk)

    def get_folder_zip_files(self):
        """Returns list of zip files in folder property"""
        folder_files = os.listdir("./"+self.folder)
        zip_files = list(filter(lambda file: re.match(".*\.zip", file), folder_files))
        return zip_files

    def parse_region_data(self, region):
        """Returns dict for specified region with column names as keys and numpy array of col values as value"""
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
            with zipfile.ZipFile(f"./{self.folder}/{file}", 'r') as zip_file:
                # open region csv file
                with zip_file.open(self.regions[region]+".csv", 'r') as csvfile:
                    csvreader = csv.reader(io.TextIOWrapper(csvfile, "cp1250"), delimiter=';')
                    for csvline in csvreader:
                        for col_index in range(len(csvline)):
                            try:
                                region_dict[self.headers[col_index]].append(self.col_data_types[col_index ](csvline[col_index]))
                            except ValueError:
                                if self.col_data_types[col_index] == int:
                                    region_dict[self.headers[col_index]].append(-1)
                                elif self.col_data_types[col_index == float]:
                                    region_dict[self.headers[col_index]].append(np.nan)
                        region_dict["region"].append(region)
        #create np array from lists
        for key in region_dict:
            region_dict[key] = np.array(region_dict[key], dtype=type(region_dict[key][0]))
        unique, counts = np.unique(region_dict["p1"], return_counts=1)
        # remove duplicit data
        if np.count_nonzero(counts > 1):
            indices = np.argwhere(counts > 1)
            for key in region_dict:
                region_dict[key] = np.delete(region_dict[key], indices )
        return region_dict

    def get_dict(self, regions=None):
        """Returns merged dict for all specified regions"""
        regions_dict = {}
        if regions is None or regions == []:
            regions = self.regions.keys()
        for region in regions:
            # check if region is in instance attr
            if self.regions_dicts_cache[region] is None:
                # check if cache file exists
                region_cache_file_name = f"./{self.folder}/{self.cache_filename.replace('{}', region)}"
                if os.path.exists(region_cache_file_name):
                    with gzip.open(region_cache_file_name, "rb") as pickle_cache:
                        self.regions_dicts_cache[region] = pickle.load(pickle_cache)
                else:
                    region_data = self.parse_region_data(region)
                    with gzip.open(region_cache_file_name, 'wb') as f:
                        pickle.dump(region_data, f)
                    self.regions_dicts_cache[region] = region_data
            # result dict is empty
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
