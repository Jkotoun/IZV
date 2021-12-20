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
        504: "Nesprávné otáčení nebo couvání",
        511: "Nezvládnutí řízení vozidla"
    }
    df2["p12"] = df2["p12"].map(causes)
    for i, row in df2.iterrows():
        df2.at[i,'procento'] = round((row["count"]/len(df.loc[df["region"]==row["region"]]))*100,1)

    df2 = df2.rename(columns={"region":"Kraj", "p12": "Příčina nehody", "count": "Počet nehod", "procento": "Procento nehod s touto příčinou v daném kraji"})
    print(df2.to_markdown(index=False))

def stats(df:pd.DataFrame, dftop: pd.DataFrame):
    dftop["percentage"] = (dftop["pocet"]/len(df) )*100
    print(f"Procento nehod způsobených nevěnování se řízení: {dftop['percentage'].iloc[0]}")
    print(f"Procento nehod způsobených nesprávným otáčením nebo couváním : {dftop['percentage'].iloc[1]}")
    df_obec = df.loc[df["p5a"] == 1]
    df_mimo = df.loc[df["p5a"] == 2]
    
    accidents_obec = len(df_obec)
    accidents_mimo = len(df_mimo)

    df_obec = df_obec.groupby(["p12"]).size().reset_index(name="pocet").sort_values(by=['pocet'], ascending=False).head(5)
    df_obec["percentage"] = (df_obec["pocet"]/accidents_obec)*100
    
    df_mimo = df_mimo.groupby(["p12"]).size().reset_index(name="pocet").sort_values(by=['pocet'], ascending=False).head(5)
    df_mimo["percentage"] = (df_mimo["pocet"]/accidents_mimo)*100
    print(f"Nejčastější příčina nehody mimo obec: příčina č. {df_mimo['p12'].iloc[0]} - nepřízpůsobení rychlosti stavu vozovky. Procento nehod - {round(df_mimo['percentage'].iloc[0],1)}")
    print(f"Nejčastější příčina nehody v obci: příčina č. {df_obec['p12'].iloc[0]} - nevěnování se řízení. Procento nehod - {round(df_obec['percentage'].iloc[0],0)}")
    
    
if __name__ == "__main__":
    df = pd.read_pickle("accidents.pkl.gz")
    plot_graph(df)
    table(df)
