#!/usr/bin/env python3.9
# coding=utf-8
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os

# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz

""" Ukol 1:
načíst soubor nehod, který byl vytvořen z vašich dat. Neznámé integerové hodnoty byly mapovány na -1.

Úkoly:
- vytvořte sloupec date, který bude ve formátu data (berte v potaz pouze datum, tj sloupec p2a)
- vhodné sloupce zmenšete pomocí kategorických datových typů. Měli byste se dostat po 0.5 GB. Neměňte však na kategorický typ region (špatně by se vám pracovalo s figure-level funkcemi)
- implementujte funkci, která vypíše kompletní (hlubkou) velikost všech sloupců v DataFrame v paměti:
orig_size=X MB
new_size=X MB

Poznámka: zobrazujte na 1 desetinné místo (.1f) a počítejte, že 1 MB = 1e6 B. 
"""


def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    df = pd.read_pickle(filename)
    if verbose:
        print(
            f"orig_size: {(df.memory_usage(deep=True).sum()/1048576):.1f} MB")

    for col in df.columns:
        if col == "p2a":
            df["date"] = pd.to_datetime(df["p2a"])
        if col in ["p2a", "h", "i", "k", "l", "n", "o", "p", "q", "t"]:
            df[col] = pd.Categorical(df[col])

    if verbose:
        print(f"new_size: {(df.memory_usage(deep=True).sum()/1048576):.1f} MB")
    return df

# Ukol 2: počty nehod v jednotlivých regionech podle druhu silnic


def plot_roadtype(df: pd.DataFrame, fig_location: str = None,
                  show_figure: bool = False):
    
    #dataframe only for selected regions and region, p21 cols
    p21df = df.loc[df["region"].isin(["KVK", "VYS", "JHM", "ZLK"]),  ["region", "p21"]]
    graph_titles = ["Jiná komunikace", "Dvoupruhová komunikace", "Třípruhová komunikace",
                    "Čtyřpruhová komunikace", "Čtyřpruhová komunikace", "Vícepruhová komunikace", "Rychlostní komunikace"]
    #create column for facetgrid with merged 4 lane roads
    p21df["road_type"] = p21df.apply(lambda row: graph_titles[row.p21], axis=1)

    sns.set_style("darkgrid")
    g = sns.FacetGrid(p21df, col="road_type", col_wrap=3,  margin_titles=True, sharey=False, sharex=False, legend_out=True, palette="deep", hue="region", hue_order=["KVK", "VYS", "JHM", "ZLK"])
    g.map(sns.countplot, "region", order=["KVK", "VYS", "JHM", "ZLK"])
    plt.xticks=[]
    g.add_legend(title="Kraje")
    g.set_xticklabels= []
    g.set(xticks=[])
    g.set_titles(col_template = '{col_name}')
    g.set_ylabels("Počet nehod")
    g.set_xlabels("Kraj")
    g.fig.suptitle('Druhy silnic')
    g.fig.subplots_adjust(top=0.9)

    if fig_location:
        dir_path = os.path.dirname(fig_location)
        if(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        plt.savefig(fig_location)
    if show_figure:
        plt.show()

# Ukol3: zavinění zvěří


def plot_animals(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):

    
    pass





# Ukol 4: Povětrnostní podmínky


def plot_conditions(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):
    pass


if __name__ == "__main__":
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni ¨
    # funkce.
    # tento soubor si stahnete sami, při testování pro hodnocení bude existovat
    df = get_dataframe("accidents.pkl.gz")
    plot_roadtype(df, fig_location="sdf/sdff/01_roadtype.png", show_figure=True)
    plot_animals(df, "02_animals.png", True)
    plot_conditions(df, "03_conditions.png", True)
