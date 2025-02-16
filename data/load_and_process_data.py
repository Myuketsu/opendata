import pandas as pd
import geopandas as gpd
from shapely import wkt

DATA_PATH = "./data/"

# --- COMMON FUNCTIONS ---


def convert_wkt_to_geometry(df: pd.DataFrame, wkt_column: str) -> gpd.GeoDataFrame:
    # Convert the GEOM_WKT column to geometry
    df["geometry"] = df[wkt_column].apply(wkt.loads)

    # Convert the DataFrame to a GeoDataFrame
    return gpd.GeoDataFrame(df.drop(wkt_column, axis="columns"), geometry="geometry")


# --- AIR DATA ---


def load_air_data() -> gpd.GeoDataFrame:
    gdfs = [
        pd.read_csv(
            DATA_PATH + "air_quality/2023/2023_tramer_no2_mapa_qualitat_aire_bcn.csv"
        )
        .rename(columns={"Rang": "NO2"})
        .astype({"NO2": "category"}),
        pd.read_csv(
            DATA_PATH + "air_quality/2023/2023_tramer_pm2-5_mapa_qualitat_aire_bcn.csv"
        )
        .rename(columns={"Rang": "PM2_5"})
        .astype({"PM2_5": "category"}),
        pd.read_csv(
            DATA_PATH + "air_quality/2023/2023_tramer_pm10_mapa_qualitat_aire_bcn.csv"
        )
        .rename(columns={"Rang": "PM10"})
        .astype({"PM10": "category"}),
    ]

    gdfs = [convert_wkt_to_geometry(gdf, "GEOM_WKT") for gdf in gdfs]
    gdf: gpd.GeoDataFrame = gdfs[0][["TRAM", "geometry"]]
    for temp_gdf in gdfs:
        gdf = gdf.merge(temp_gdf.drop(columns=["geometry"]), on="TRAM")

    gdf["NO2"] = gdf["NO2"].cat.reorder_categories(
        [
            "10-20 µg/m³",
            "20-30 µg/m³",
            "30-40 µg/m³",
            "40-50 µg/m³",
            "50-60 µg/m³",
            "60-70 µg/m³",
            ">70 µg/m³",
        ],
        ordered=True,
    )

    gdf["PM2_5"] = gdf["PM2_5"].cat.reorder_categories(
        ["5-10 µg/m³", "10-15 µg/m³", "15-20 µg/m³", "20-25 µg/m³", "25-30 µg/m³"],
        ordered=True,
    )

    gdf["PM10"] = gdf["PM10"].cat.reorder_categories(
        [
            "<=15 µg/m³",
            "15-20 µg/m³",
            "20-25 µg/m³",
            "25-30 µg/m³",
            "30-35 µg/m³",
            "35-40 µg/m³",
            "> 40 µg/m³",
        ],
        ordered=True,
    )

    return gdf.set_crs(epsg=25831).to_crs(epsg=4326)


gdf_air = load_air_data()
