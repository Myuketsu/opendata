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


# --- NOISE DATA ---


def load_noise_data() -> gpd.GeoDataFrame:
    df_values = pd.concat(
        [
            pd.read_csv(
                filepath_or_buffer="./data/noise_monitoring/2023/2023_1S_XarxaSoroll_EqMonitor_Dades_1Hora.csv",
            ),
            pd.read_csv(
                filepath_or_buffer="./data/noise_monitoring/2023/2023_2S_XarxaSoroll_EqMonitor_Dades_1Hora.csv",
            ),
        ]
    )

    df_values["date"] = pd.to_datetime(
        df_values["Any"].astype(str)
        + "-"
        + df_values["Mes"].astype(str)
        + "-"
        + df_values["Dia"].astype(str)
        + " "
        + df_values["Hora"].astype(str)
    )

    df_values = df_values.drop(columns=["Any", "Mes", "Dia", "Hora"])

    df_insta = pd.read_csv(
        "./data/noise_monitoring/XarxaSoroll_EquipsMonitor_Instal.csv"
    )
    df_insta = df_insta[df_insta["Id_Instal"].isin(df_values["Id_Instal"].unique())]

    df_insta = df_insta[
        [
            "Id_Instal",
            "Codi_Barri",
            "Nom_Barri",
            "Codi_Districte",
            "Nom_Districte",
            "Longitud",
            "Latitud",
            "Font",
        ]
    ]

    df = df_values.merge(df_insta, on="Id_Instal")

    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df["Longitud"], df["Latitud"]), crs="EPSG:4326"
    ).drop(columns=["Longitud", "Latitud"])

    gdf = gdf.rename(
        columns={
            "Id_Instal": "id",
            "Nivell_LAeq_1h": "noise_level",
            "Codi_Barri": "area_code",
            "Nom_Barri": "area_name",
            "Codi_Districte": "district_code",
            "Nom_Districte": "district_name",
            "Font": "source",
        }
    )

    gdf = gdf.astype(
        {
            "id": "category",
            "noise_level": "float32",
            "area_code": "category",
            "area_name": "category",
            "district_code": "category",
            "district_name": "category",
            "source": "category",
        }
    )

    gdf["source"] = gdf["source"].cat.rename_categories(
        {
            "ACTIVITATS / INFRASTRUCTURES ESPORTIVES": "ACTIVITÉS SPORTIVES / INFRASTRUCTURES",
            "ANIMALS": "ANIMAUX",
            "NETEJA": "NETTOYAGE",
            "OBRES": "TRAVAUX",
            "OCI": "LOISIRS",
            "PATIS D'ESCOLA": "COURS D'ÉCOLE",
            "TRÀNSIT": "TRAFIC",
            "XARXA DE TRANSPORT PÚBLIC": "RÉSEAU DE TRANSPORT PUBLIC",
            "ZONES PEATONALS": "ZONES PIÉTONS",
        }
    )

    return gdf


gdf_noise = load_noise_data()


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
# gdf_air_json = gdf_air.to_json()


# --- TREES DATA ---


def load_trees_data() -> gpd.GeoDataFrame:
    park_trees_df = pd.read_csv(
        DATA_PATH + "trees/street_trees/2023_4T_OD_Arbrat_Viari_BCN.csv"
    )
    street_trees_df = pd.read_csv(
        DATA_PATH + "trees/street_trees/2023_4T_OD_Arbrat_Viari_BCN.csv"
    )
    zone_trees_df = pd.read_csv(
        DATA_PATH + "trees/zone_trees/2023_4T_OD_Arbrat_Zona_BCN.csv"
    )

    all_trees_df = pd.concat(
        [park_trees_df, street_trees_df, zone_trees_df]
    )  # Concatenate the three DataFrames

    # Get the number of trees per district
    trees_per_district = (
        all_trees_df[["codi_districte", "nom_districte"]]
        .value_counts(sort=1)
        .reset_index()
    )
    trees_per_district.columns = ["Code", "District", "Number of Trees"]
    trees_per_district.loc[len(trees_per_district.index)] = [
        "0",
        "TOTAL",
        all_trees_df.shape[0],
    ]

    # Create a DataFrame with the areas of each district
    district_areas_df = pd.DataFrame(
        {
            "District": [
                "CIUTAT VELLA",
                "EIXAMPLE",
                "SANTS - MONTJUÏC",
                "LES CORTS",
                "SARRIÀ - SANT GERVASI",
                "GRÀCIA",
                "HORTA - GUINARDÓ",
                "NOU BARRIS",
                "SANT ANDREU",
                "SANT MARTÍ",
                "TOTAL",
            ],
            "Area": [
                4.11,
                7.46,
                22.68,
                6.02,
                19.91,
                4.19,
                11.96,
                8.05,
                6.59,
                10.39,
                101.36,
            ],
        }
    )

    # Calculate the number of trees per km²
    trees_per_district = trees_per_district.merge(district_areas_df, on="District")
    trees_per_district["Trees per km²"] = (
        trees_per_district["Number of Trees"] / trees_per_district["Area"]
    )

    district_df = pd.read_csv(
        DATA_PATH + "district_zone/BarcelonaCiutat_Districtes.csv"
    )

    # Convert the WKT geometries to Shapely geometries
    district_df = convert_wkt_to_geometry(district_df, "geometria_wgs84").set_crs(
        epsg=4326
    )

    # Create a GeoDataFrame with the number of trees per district
    district_df = district_df.merge(
        trees_per_district, left_on="Codi_Districte", right_on="Code"
    ).drop(columns=["geometria_etrs89", "District"])

    gdf_trees = district_df.rename(
        columns={
            "Codi_Districte": "district_code",
            "nom_districte": "district_name",
        }
    )[
        [
            "district_code",
            "district_name",
            "Number of Trees",
            "Trees per km²",
            "geometry",
        ]
    ]

    gdf_trees = gdf_trees.astype(
        {
            "district_code": "category",
            "district_name": "category",
            "Number of Trees": "int32",
            "Trees per km²": "float32",
        }
    )

    return gdf_trees


gdf_trees = load_trees_data()
