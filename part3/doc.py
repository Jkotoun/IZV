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
    
    stats(df, df1)


    df1["labels"] = ["Nevěnování se řízení", "Nesprávné otáčení nebo couvání",  "Jiný druh nesprávného způsobu jízdy", "Nedodržení bezpečné vzdálenosti","Nepřízpůsobení rychlosti vlastnostem vozidla"]
    g = sns.catplot(data=df1, x="labels", y="pocet", kind="bar", aspect=3 , margin_titles=True)
    g.fig.suptitle("5 nejčastějčích příčin u nehod zaviněných řidičem")
    g.set_ylabels("Počet nehod")
    g.set_xlabels("Hlavní příčina nehody")
    plt.savefig("fig.png")




def table(df: pd.DataFrame):
    df = df.loc[df["p10"]==1]
    df2 = df.groupby(["region","p12"]).size().reset_index(name="count").sort_values(by="count", ascending=False).groupby(["region"]).head(1)
    causes = {
        516: "Jiný druh nesprávného způsobu jízdy",
        508: "Řidič se plně nevěnoval řízení vozidla",
        504: "Nepsrávné otáčení nebo couvání",
        511: "Nezvládnutí řízení vozidla"
    }
    df2["p12"] = df2["p12"].map(causes)
    
    # df2["procento"] = df2["count"]/len(df.loc[df["region"]==df2["region"]])
    # df2["procento_nehod"] = (df2["pocet"]/len(df))*100
    df2 = df2.rename(columns={"region":"Kraj", "p12": "Příčina nehody", "count": "Počet nehod"})
    print(df2.to_markdown(index=False))

def stats(df:pd.DataFrame, dftop: pd.DataFrame):
    dftop["procent_nehod"] = (dftop["pocet"]/len(df))*100
    print(dftop)


if __name__ == "__main__":
    df = pd.read_pickle("accidents.pkl.gz")
    plot_graph(df)
    # table(df)
