#!/usr/bin/python3.8
# coding=utf-8
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np
import os
import sklearn.cluster as skl
from mpl_toolkits.axes_grid1 import make_axes_locatable

# muzete pridat vlastni knihovny

def save_and_show(fig_location: str = None, show_figure: bool = False):
    """Ulozeni a zobrazeni obrazku podle zadanych parametru"""
    if fig_location:
        dir_path = os.path.dirname(fig_location)
        if(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        plt.savefig(fig_location)
    if show_figure:
        plt.show()

def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    """ Konvertovani dataframe do geopandas.GeoDataFrame se spravnym kodovani"""
    df.dropna(subset=["d", "e"], inplace=True)
    df["date"] = pd.to_datetime(df["p2a"])
    #s-jtsk format
    return  geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df["d"], df["e"]), crs="EPSG:5514")


def plot_geo(
    gdf: geopandas.GeoDataFrame, fig_location: str = None, show_figure: bool = False
):
    """Vykresleni grafu s sesti podgrafy podle lokality nehody
    (dalnice vs prvni trida) pro roky 2018-2020"""

    gdf = gdf.loc[gdf["region"] == "VYS", ["date", "geometry", "p36"]]
    #convert to webmap format
    gdf.to_crs(epsg=3857, inplace=True)
    #x and y limits
    minx, miny, maxx, maxy = gdf.geometry.total_bounds
    fig, ax = plt.subplots(3, 2, figsize=(13,17))
    #3 rows, 1 for each year
    for index, year in enumerate([2018,2019,2020]):
        #left col for highway and right col for 1st class road
        for j, road in enumerate(
            [
                {"name": "dálnice", "color": "green", "dataset_num":0}, 
                {"name": "silnice první třídy", "color": "darkred", "dataset_num":1}
            ]
        ):
            gdf[(gdf["p36"] == road["dataset_num"]) & (gdf["date"].dt.year == year)].plot(ax=ax[index, j], color=road["color"], markersize=2)
            ax[index, j].axis("off")
            ax[index, j].set_xlim(minx, maxx)
            ax[index, j].set_ylim(miny, maxy)
            ctx.add_basemap(ax=ax[index, j], crs=gdf.crs.to_string(), source=ctx.providers.Stamen.TonerLite)
            ax[index, j].set_title(f"Kraj Vysočina: {road['name']} {year}")
    fig.tight_layout(pad=2.0)
    save_and_show(fig_location, show_figure)
    


def plot_cluster(
    gdf: geopandas.GeoDataFrame, fig_location: str = None, show_figure: bool = False
):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do clusteru """
    #convert to webmap format
    gdf.to_crs(epsg=3857, inplace=True)
    filtered_gdf = gdf.loc[(gdf["p36"]==1) & (gdf["region"] == "VYS")]
    
    #get coords array
    coords_list = np.dstack([filtered_gdf.geometry.x, filtered_gdf.geometry.y]).reshape(-1, 2)

    #pro rozdělení do clusterů byla zvolena metoda KMeans, protože se jedná o nejběžněji používanou metodu
    #Hodnota 25 přehledně zobrazuje úseky s různou úrovní nehodovosti
    #Byly vyzkoušeny hodnoty v jednotkách clusterů, které nebyly dostatečné pro znázornění a hodnoty kolem 50 - 100, u kterých
    #úseky s vyšší nehodovostí nejsou tak výrazné
    clusters = sklearn.cluster.MiniBatchKMeans(n_clusters=25).fit(coords_list)

    #dissolve by clusters
    clustered_gdf = filtered_gdf.copy() 
    clustered_gdf["cluster"] = clusters.labels_
    clustered_gdf = clustered_gdf.dissolve(by="cluster", aggfunc={"p1": "count"})
    
    #plot graph
    fig, ax = plt.subplots(1,1, figsize=(15,15))
    ax.set_title("Nehody v kraji Vysočina na silnicích 1. třídy")
    ax.axis("off")
    #adjust size of legend
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    clustered_gdf.plot(column="p1", ax=ax, legend=True, markersize=3, cax=cax)
    ctx.add_basemap(ax=ax, crs=clustered_gdf.crs.to_string() ,source=ctx.providers.Stamen.TonerLite)

    save_and_show(fig_location, show_figure)



if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png", False)
    plot_cluster(gdf, "geo2.png", False)
