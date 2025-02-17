import folium
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import plotly.graph_objects as go
import json
from shapely import wkt

from data.load_and_process_data import convert_wkt_to_geometry

def trees_df() -> pd.DataFrame:
    # Load the trees data
    park_trees_df = pd.read_csv('data/trees/street_trees/2023_4T_OD_Arbrat_Viari_BCN.csv')
    street_trees_df = pd.read_csv('data/trees/street_trees/2023_4T_OD_Arbrat_Viari_BCN.csv')
    zone_trees_df = pd.read_csv('data/trees/zone_trees/2023_4T_OD_Arbrat_Zona_BCN.csv')

    all_trees_df = pd.concat([park_trees_df, street_trees_df, zone_trees_df]) # Concatenate the three DataFrames

    # Get the number of trees per district
    trees_per_district = all_trees_df[['codi_districte', 'nom_districte']].value_counts(sort=1).reset_index()
    trees_per_district.columns = ['Code', 'District', 'Number of Trees']
    trees_per_district.loc[len(trees_per_district.index)] = ['0', 'TOTAL', all_trees_df.shape[0]]

    # Create a DataFrame with the areas of each district
    district_areas_df = pd.DataFrame({
            'District': ['CIUTAT VELLA', 'EIXAMPLE', 'SANTS - MONTJUÏC', 'LES CORTS', 'SARRIÀ - SANT GERVASI', 'GRÀCIA', 'HORTA - GUINARDÓ', 'NOU BARRIS', 'SANT ANDREU', 'SANT MARTÍ', 'TOTAL'],
            'Area': [4.11, 7.46, 22.68, 6.02, 19.91, 4.19, 11.96, 8.05, 6.59, 10.39, 101.36]
        }
    )

    # Calculate the number of trees per km²
    trees_per_district = trees_per_district.merge(district_areas_df, on='District')
    trees_per_district['Trees per km²'] = trees_per_district['Number of Trees'] / trees_per_district['Area']

    return trees_per_district

def trees_map() -> folium.Map:
    trees_per_district = trees_df()
    district_df = pd.read_csv("./data/district_zone/BarcelonaCiutat_Districtes.csv")

    # Convert the WKT geometries to Shapely geometries
    district_df = convert_wkt_to_geometry(district_df, 'geometria_wgs84')
    district_df.crs = 'EPSG:4326'
    district_df = district_df.to_crs('EPSG:3857')

    # Create a GeoDataFrame with the number of trees per district
    district_df = district_df.merge(trees_per_district, left_on='Codi_Districte', right_on='Code')

    # fix the coordinates in Barcelona
    boulder_coords = [41.388790, 2.158990]

    map = folium.Map(location = boulder_coords, zoom_start = 12)

    # add geometry to the map for the districts and color them by the number of Trees per km²
    folium.Choropleth(
        geo_data=district_df,
        name='choropleth',
        data=district_df,
        columns=['District', 'Trees per km²'],
        key_on='feature.properties.District',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Trees per km²',
    ).add_to(map)

    return map.get_root().render()
