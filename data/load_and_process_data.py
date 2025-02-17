from sklearn.cluster import KMeans
import pandas as pd
import geopandas as gpd
from shapely import wkt
import json

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
gdf_json = gdf_air.to_json()


# --- Transport DATA ---


def load_transport_age_data() -> gpd.GeoDataFrame:
    vage_df = pd.read_csv(
        DATA_PATH + "/age_of_vehicle/2023/2023_Antiguitat_tipus_vehicle.csv"
    )
    district_df = pd.read_csv(
        DATA_PATH + "/district_zone/BarcelonaCiutat_Districtes.csv"
    )

    total_vehicles_per_district = (
        vage_df.groupby(["Nom_Districte"]).Nombre.sum().reset_index()
    )
    total_vehicles_per_district.columns = ["Nom_Districte", "Total_Vehicles"]

    old_vehicles_per_district = (
        vage_df[vage_df.Antiguitat == "MÃ©s de 20 anys"]
        .groupby(["Nom_Districte"])
        .Nombre.sum()
        .reset_index()
    )
    old_vehicles_per_district.columns = ["Nom_Districte", "Vehicles_20_Any"]

    merged = total_vehicles_per_district.merge(
        old_vehicles_per_district, on="Nom_Districte", how="left"
    )
    merged["Percentage"] = (merged["Vehicles_20_Any"] / merged["Total_Vehicles"]) * 100
    merged["Percentage"] = merged["Percentage"].map("{:,.2f}".format)
    merged = merged[merged.Nom_Districte != "No consta"]
    merged["Percentage"] = merged["Percentage"].astype(float)

    gdf = convert_wkt_to_geometry(district_df, "geometria_wgs84")
    gdf = gdf.rename(columns={"nom_districte": "Nom_Districte"})

    gdf_merged = gdf.merge(merged, on="Nom_Districte", how="left")

    return gdf_merged, json.loads(gdf_merged.to_json())


def load_transport_type_data() -> gpd.GeoDataFrame:
    vtype_df = pd.read_csv(
        DATA_PATH + "/type_of_vehicle/2023/2023_Parc_vehicles_tipus_propulsio.csv"
    )
    district_df = pd.read_csv(
        DATA_PATH + "/district_zone/BarcelonaCiutat_Districtes.csv"
    )

    vehuicles_per_district = (
        vtype_df.groupby(["Nom_Districte"]).Nombre.sum().reset_index()
    )
    vehuicles_per_district.columns = ["Nom_Districte", "Total_Vehicles"]

    green_vehicles_per_district = (
        vtype_df[
            (vtype_df.Tipus_Propulsio == "Elèctrica")
            | (vtype_df.Tipus_Propulsio == "Híbrid")
        ]
        .groupby(["Nom_Districte"])
        .Nombre.sum()
        .reset_index()
    )
    green_vehicles_per_district.columns = ["Nom_Districte", "Green_Vehicles"]

    merged = vehuicles_per_district.merge(
        green_vehicles_per_district, on="Nom_Districte", how="left"
    )
    merged["Percentage"] = (merged["Green_Vehicles"] / merged["Total_Vehicles"]) * 100
    merged["Percentage"] = merged["Percentage"].map("{:,.2f}".format)

    gdf = convert_wkt_to_geometry(district_df, "geometria_wgs84")
    gdf = gdf.rename(columns={"nom_districte": "Nom_Districte"})

    gdf_merged = gdf.merge(merged, on="Nom_Districte", how="left")

    return gdf_merged, json.loads(gdf_merged.to_json())


def load_kmeans_data(
    transport_age: gpd.GeoDataFrame, transport_type: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    gdf_age = transport_age.copy()
    gdf_type = transport_type.copy()

    gdf_age = gdf_age.rename(columns={"Percentage": "Age_Percentage"})
    gdf_type = gdf_type.rename(columns={"Percentage": "Green_Percentage"})

    gdf_age = gdf_age[["Nom_Districte", "Age_Percentage"]]
    gdf_type = gdf_type[["Nom_Districte", "Green_Percentage"]]

    gdf_kmean = gdf_age.merge(gdf_type, on="Nom_Districte", how="left")

    kmeans = KMeans(n_clusters=3, random_state=0).fit(
        gdf_kmean[["Age_Percentage", "Green_Percentage"]]
    )

    gdf_kmean["Cluster"] = kmeans.labels_

    district_df = pd.read_csv(
        DATA_PATH + "/district_zone/BarcelonaCiutat_Districtes.csv"
    )

    gdf = convert_wkt_to_geometry(district_df, "geometria_wgs84")
    gdf = gdf.rename(columns={"nom_districte": "Nom_Districte"})

    gdf_merged = gdf.merge(gdf_kmean, on="Nom_Districte", how="left")

    return gdf_merged, json.loads(gdf_merged.to_json())


gdf_transport_age, gdf_transport_age_json = load_transport_age_data()
gdf_transport_type, gdf_transport_type_json = load_transport_type_data()
gdf_transport_kmeans, gdf_transport_kmeans_json = load_kmeans_data(
    gdf_transport_age, gdf_transport_type
)

pourcentage_vehicules_20_ans = (
    gdf_transport_age.Vehicles_20_Any.sum()
    / gdf_transport_age.Total_Vehicles.sum()
    * 100
)
pourcentage_vehicules_verts = (
    gdf_transport_type.Green_Vehicles.sum()
    / gdf_transport_type.Total_Vehicles.sum()
    * 100
)
