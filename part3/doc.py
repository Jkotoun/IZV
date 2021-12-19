#!/usr/bin/python3.8
# coding=utf-8
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def plot_graph(df: pd.DataFrame):
    df["date"] = pd.to_datetime(df["p2a"])
    df = df.loc[df["p10"]==1]
    df1 = df.groupby(["p12"]).size().reset_index(name="pocet").sort_values(by=['pocet'], ascending=False)[:5]
    
    df1["labels"] = ["Nevěnování se řízení", "Nesprávné otáčení nebo couvání",  "Jiný druh nesprávného způsobu jízdy", "Nedodržení bezpečné vzdálenosti","Nepřízpůsobení rychlosti vlastnostem vozidla"]
    g = sns.catplot(data=df1, x="labels", y="pocet", kind="bar", aspect=3 , margin_titles=True)
    g.fig.suptitle("5 nejčastějčích příčin u nehod zaviněných řidičem")
    g.set_ylabels("Počet nehod")
    g.set_xlabels("Hlavní příčina nehody")
    plt.savefig("fig.png")



if __name__ == "__main__":
    df = pd.read_pickle("accidents.pkl.gz")
    plot_graph(df)
