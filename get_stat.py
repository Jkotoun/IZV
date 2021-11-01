#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import os
import argparse

# povolene jsou pouze zakladni knihovny (os, sys) a knihovny numpy, matplotlib a argparse

from download import DataDownloader


def plot_stat(data_source, fig_location=None, show_figure=False):
    import numpy as np

    right_of_way_accident = ["Přerušovaná žlutá",  "Semafor mimo provoz",
                             "Dopravní značky",   "Přenosné dopravní značky",  "Nevyznačena", "Žádná úprava"]
    regions = ["HKK",
               "JHC",
               "JHM",
               "KVK",
               "LBK",
               "MSK",
               "OLK",
               "PAK",
               "PHA",
               "PLK",
               "STC",
               "ULK",
               "VYS",
               "ZLK", ]

    data_absolute = np.empty((len(regions), 6))
    data_relative = np.empty((len(regions), 6))

    fig_data = data_source["p24"]

    i = 0
    for region in regions:
        bool_indexing_arr = data_source["region"] == region
        region_data = fig_data[bool_indexing_arr]
        count_arr = np.bincount(region_data)
        count_arr = np.roll(count_arr, -1)
        data_absolute[i] = count_arr
        i = i+1

    accident_causes_sums = data_absolute.sum(axis=0)

    data_relative = (data_absolute/accident_causes_sums)*100
    data_absolute[data_absolute == 0.0] = np.nan
    data_relative[data_relative == 0.0] = np.nan

    fig = plt.figure(figsize=(8, 6))
    ax1 = fig.add_subplot(211)
    ax1.title.set_text("Absolutně")
    im1 = ax1.imshow(data_absolute.T, interpolation='None',
                     norm=LogNorm(vmin=1e0, vmax=1e5))
    ax1.set_xticks(np.arange(len(regions)))
    ax1.set_yticks(np.arange(len(right_of_way_accident)))
    ax1.set_xticklabels(regions)
    ax1.set_yticklabels(right_of_way_accident)
    cbar = fig.colorbar(im1)
    cbar.set_label('Počet nehod')

    ax2 = fig.add_subplot(212)
    ax2.title.set_text("Relativně vůči příčině")
    im2 = ax2.imshow(data_relative.T, interpolation='None',
                     vmin=0, vmax=100,  cmap=plt.get_cmap("plasma"))
    ax2.set_xticks(np.arange(len(regions)))
    ax2.set_yticks(np.arange(len(right_of_way_accident)))
    ax2.set_xticklabels(regions)
    ax2.set_yticklabels(right_of_way_accident)
    cbar2 = fig.colorbar(im2)
    cbar2.set_label('Podíl nehod pro danou příčinu [%]')
    fig.tight_layout(pad=3.0)

    if fig_location:
        dir_path = os.path.dirname(fig_location)
        if(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        plt.savefig(fig_location)

    if show_figure:
        plt.show()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--fig_location', dest="fig_location", default = None, help='Relative location to store figure')
    parser.add_argument('--show_figure', dest='show_figure', action="store_true", help='sum the integers (default: find the max)')
    args = parser.parse_args()
    data_source = DataDownloader().get_dict()
    plot_stat(data_source, fig_location=args.fig_location, show_figure=args.show_figure)
