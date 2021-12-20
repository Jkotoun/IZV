#!/usr/bin/python3.8
# coding=utf-8
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def map_causes(df:pd.DataFrame):
    """Create label column for most common accident causes"""
    most_common_causes = {
        503: "Nedodržení bezpečné vzdálenosti",
        204: "Nepřizpůsobení rychlosti stavu vozovky",
        516: "Jiný druh nesprávného způsobu jízdy",
        508: "Řidič se plně nevěnoval řízení vozidla",
        504: "Nesprávné otáčení nebo couvání",
        511: "Nezvládnutí řízení vozidla"
    }
    df["cause_label"] = df["p12"].map(most_common_causes)
    return df

def top5_by_causes(df: pd.DataFrame):
    """returns count of accidents, labels and accidents percentage of 5 most common causes"""
    top5 = df.groupby(["p12"]).size().reset_index(name="pocet").sort_values(by=['pocet'], ascending=False)[:5]
    top5 = map_causes(top5)
    #percentage of accidents caused by given cause
    top5["percentage"] = round((top5["pocet"]/len(df))*100, 1)
    return top5

def most_common_causes_republic(df: pd.DataFrame):
    """get 5 most common causes of accidents in republic, which were caused by driver"""
    df["date"] = pd.to_datetime(df["p2a"])
    #accidents, which were caused by driver
    df = df.loc[df["p10"]==1]
    #top 5 causes
    result= top5_by_causes(df)
    return result


def plot_accidents_causes(df: pd.DataFrame):
    """Plot accident causes and labels to horizontal barplot"""
    sns.set(font_scale=1.2)
    sns.set_style("darkgrid")
    sns.set_palette("bright")
    g = sns.catplot(data=df, y="cause_label", x="pocet", kind="bar" ,aspect=2.5, margin_titles=True, orient="h")
    g.fig.suptitle("5 nejčastějčích příčin u nehod zaviněných řidičem")
    g.set_xlabels("Počet nehod")
    g.set_ylabels("Hlavní příčina nehody")
    g.fig.subplots_adjust(top=0.9)
    plt.show()
    plt.savefig("fig.png")




def print_regions_overview_table(df: pd.DataFrame):
    """print latex table with count and percentage of most common accidents in each region, caused by driver"""
    #caused by driver
    df = df.loc[df["p10"]==1]
    #get most common cause for each region
    df2 = df.groupby(["region","p12"]).size().reset_index(name="count").sort_values(by="count", ascending=False).groupby(["region"]).head(1)
    #calculate what percentage of accidents in region was caused by most common cause 
    for i, row in df2.iterrows():
        df2.at[i,'percentage'] = round((row["count"]/len(df.loc[df["region"]==row["region"]]))*100,1)
    df2 = map_causes(df2)
    df2 = df2.rename(columns={"region":"Kraj", "p12" : "číslo příčiny", "cause_label": "Příčina nehody", "count": "Počet nehod", "percentage": "Procento nehod"})
    print(df2.to_latex(index=False))



def print_stats(df:pd.DataFrame, df_most_common_republic: pd.DataFrame):
    """Print some values needed for doc.pdf"""

    most_common = df_most_common_republic.loc[df_most_common_republic['p12'] == 508]['percentage'].iloc[0]
    second_most_common = (df_most_common_republic.loc[df_most_common_republic['p12'] == 504])['percentage'].iloc[0]
    print(f"Procento nehod způsobených nevěnování se řízení v celé ČR: {most_common }")
    print(f"Procento nehod způsobených nesprávným otáčením nebo couváním v celé ČR : {second_most_common}")
    
    #caused by driver
    df = df.loc[df["p10"]==1]
    df_in = df.loc[df["p5a"] == 1]
    df_out = df.loc[df["p5a"] == 2]
    df_in_most = top5_by_causes(df_in).iloc[0]
    df_out_most =  top5_by_causes(df_out).iloc[0]

    print(f"Nejčastější příčina nehody v obci: příčina č. {df_in_most['p12']} - {df_in_most['cause_label']}. Procento nehod - {df_in_most['percentage']}")
    print(f"Nejčastější příčina nehody mimo obec: příčina č. {df_out_most['p12']} - {df_out_most['cause_label']}. Procento nehod - {df_out_most['percentage']}")
    
    
if __name__ == "__main__":
    df = pd.read_pickle("accidents.pkl.gz")
    top5_causes_df = most_common_causes_republic(df)
    plot_accidents_causes(top5_causes_df)
    print_regions_overview_table(df)
    print_stats(df, top5_causes_df)

