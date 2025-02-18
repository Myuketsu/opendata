import numpy as np
import pandas as pd
import geopandas as gpd
import json

from shapely import wkt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

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


gdf_noise: gpd.GeoDataFrame = pd.read_pickle("./data/noise_monitoring/noise_data.pkl")


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


gdf_air: gpd.GeoDataFrame = pd.read_pickle("./data/air_quality/air_data.pkl")


# --- LIFE QUALITY DATA ---


def load_life_quality_data() -> gpd.GeoDataFrame:
    df = pd.read_csv(DATA_PATH + "quality_of_life/quality_of_life_per_district.csv")
    return df


df_life_quality = load_life_quality_data()

# --- Transport DATA ---


# def load_transport_age_data() -> gpd.GeoDataFrame:
#     vage_df = pd.read_csv(
#         DATA_PATH + "/age_of_vehicle/2023/2023_Antiguitat_tipus_vehicle.csv"
#     )
#     district_df = pd.read_csv(
#         DATA_PATH + "/district_zone/BarcelonaCiutat_Districtes.csv"
#     )

#     total_vehicles_per_district = (
#         vage_df.groupby(["Nom_Districte"]).Nombre.sum().reset_index()
#     )
#     total_vehicles_per_district.columns = ["Nom_Districte", "Total_Vehicles"]

#     old_vehicles_per_district = (
#         vage_df[vage_df.Antiguitat == "MÃ©s de 20 anys"]
#         .groupby(["Nom_Districte"])
#         .Nombre.sum()
#         .reset_index()
#     )
#     old_vehicles_per_district.columns = ["Nom_Districte", "Vehicles_20_Any"]

#     merged = total_vehicles_per_district.merge(
#         old_vehicles_per_district, on="Nom_Districte", how="left"
#     )
#     merged["Percentage"] = (merged["Vehicles_20_Any"] / merged["Total_Vehicles"]) * 100
#     merged["Percentage"] = merged["Percentage"].map("{:,.2f}".format)
#     merged = merged[merged.Nom_Districte != "No consta"]
#     merged["Percentage"] = merged["Percentage"].astype(float)

#     gdf = convert_wkt_to_geometry(district_df, "geometria_wgs84")
#     gdf = gdf.rename(columns={"nom_districte": "Nom_Districte"})

#     gdf_merged = gdf.merge(merged, on="Nom_Districte", how="left")

#     return gdf_merged, json.loads(gdf_merged.to_json())


# def load_transport_type_data() -> gpd.GeoDataFrame:
#     vtype_df = pd.read_csv(
#         DATA_PATH + "/type_of_vehicle/2023/2023_Parc_vehicles_tipus_propulsio.csv"
#     )
#     district_df = pd.read_csv(
#         DATA_PATH + "/district_zone/BarcelonaCiutat_Districtes.csv"
#     )

#     vehuicles_per_district = (
#         vtype_df.groupby(["Nom_Districte"]).Nombre.sum().reset_index()
#     )
#     vehuicles_per_district.columns = ["Nom_Districte", "Total_Vehicles"]

#     green_vehicles_per_district = (
#         vtype_df[
#             (vtype_df.Tipus_Propulsio == "Elèctrica")
#             | (vtype_df.Tipus_Propulsio == "Híbrid")
#         ]
#         .groupby(["Nom_Districte"])
#         .Nombre.sum()
#         .reset_index()
#     )
#     green_vehicles_per_district.columns = ["Nom_Districte", "Green_Vehicles"]

#     merged = vehuicles_per_district.merge(
#         green_vehicles_per_district, on="Nom_Districte", how="left"
#     )
#     merged["Percentage"] = (merged["Green_Vehicles"] / merged["Total_Vehicles"]) * 100
#     merged["Percentage"] = merged["Percentage"].map("{:,.2f}".format)

#     gdf = convert_wkt_to_geometry(district_df, "geometria_wgs84")
#     gdf = gdf.rename(columns={"nom_districte": "Nom_Districte"})

#     gdf_merged = gdf.merge(merged, on="Nom_Districte", how="left")

#     return gdf_merged, json.loads(gdf_merged.to_json())


# def load_transport_pop_data() -> gpd.GeoDataFrame:
#     vtype_df = pd.read_csv(
#         DATA_PATH + "/type_of_vehicle/2023/2023_Parc_vehicles_tipus_propulsio.csv"
#     )
#     district_df = pd.read_csv(
#         DATA_PATH + "/district_zone/BarcelonaCiutat_Districtes.csv"
#     )
#     pop_df = pd.read_csv(DATA_PATH + "/population/2023/2023_pad_mdbas.csv")

#     pop_per_district = pop_df.groupby(["Nom_Districte"]).Valor.sum().reset_index()
#     pop_per_district.columns = ["Nom_Districte", "Population"]

#     vehuicles_per_district = (
#         vtype_df.groupby(["Nom_Districte"]).Nombre.sum().reset_index()
#     )
#     vehuicles_per_district.columns = ["Nom_Districte", "Total_Vehicles"]

#     merged = vehuicles_per_district.merge(
#         pop_per_district, on="Nom_Districte", how="left"
#     )
#     merged["Vehicles_Per_100"] = (merged["Total_Vehicles"] / merged["Population"]) * 100
#     merged = merged[merged.Nom_Districte != "No consta"]
#     merged["Vehicles_Per_100"] = merged["Vehicles_Per_100"].map("{:,.2f}".format)

#     gdf = convert_wkt_to_geometry(district_df, "geometria_wgs84")
#     gdf = gdf.rename(columns={"nom_districte": "Nom_Districte"})

#     gdf_merged = gdf.merge(merged, on="Nom_Districte", how="left")

#     return gdf_merged, json.loads(gdf_merged.to_json())


# def load_kmeans_data(
#     transport_age: gpd.GeoDataFrame,
#     transport_type: gpd.GeoDataFrame,
#     transport_pop: gpd.GeoDataFrame,
# ) -> gpd.GeoDataFrame:
#     gdf_age = transport_age.copy()
#     gdf_type = transport_type.copy()
#     gdf_pop = transport_pop.copy()

#     gdf_age = gdf_age.rename(columns={"Percentage": "Age_Percentage"})
#     gdf_type = gdf_type.rename(columns={"Percentage": "Green_Percentage"})
#     gdf_pop = gdf_pop.rename(columns={"Vehicles_Per_100": "Vehicles_Per_100"})

#     gdf_age = gdf_age[["Nom_Districte", "Age_Percentage"]]
#     gdf_type = gdf_type[["Nom_Districte", "Green_Percentage"]]
#     gdf_pop = gdf_pop[["Nom_Districte", "Vehicles_Per_100"]]

#     gdf_kmean = gdf_age.merge(gdf_type, on="Nom_Districte", how="left")
#     gdf_kmean = gdf_kmean.merge(gdf_pop, on="Nom_Districte", how="left")

#     kmeans = KMeans(n_clusters=3, random_state=42).fit(
#         gdf_kmean[["Age_Percentage", "Green_Percentage", "Vehicles_Per_100"]]
#     )

#     gdf_kmean["Cluster"] = kmeans.labels_

#     district_df = pd.read_csv(
#         DATA_PATH + "/district_zone/BarcelonaCiutat_Districtes.csv"
#     )

#     gdf = convert_wkt_to_geometry(district_df, "geometria_wgs84")
#     gdf = gdf.rename(columns={"nom_districte": "Nom_Districte"})

#     gdf_merged = gdf.merge(gdf_kmean, on="Nom_Districte", how="left")

#     return gdf_merged, json.loads(gdf_merged.to_json())


# def load_transport_age_pie_data() -> pd.DataFrame:
#     vage_df = pd.read_csv(
#         DATA_PATH + "age_of_vehicle/2023/2023_Antiguitat_tipus_vehicle2.csv"
#     )

#     return vage_df[["Antiguitat", "Nombre"]].groupby("Antiguitat", as_index=False).sum()


# def load_transport_type_pie_data() -> pd.DataFrame:
#     vtype_df = pd.read_csv(
#         DATA_PATH + "type_of_vehicle/2023/2023_Parc_vehicles_tipus_propulsio2.csv"
#     )

#     return (
#         vtype_df[["Tipus_Propulsio", "Nombre"]]
#         .groupby("Tipus_Propulsio", as_index=False)
#         .sum()
#     )


# def load_transport_pop_hist_data() -> pd.DataFrame:
#     pop_df = pd.read_csv(DATA_PATH + "population/2023/2023_pad_mdbas.csv")
#     superficie_df = pd.read_csv(DATA_PATH + "superficie/2021_superficie.csv")
#     superficie_df = superficie_df.rename(
#         columns={"SuperfÃ­cie (ha)": "Superficie (ha)"}
#     )

#     pop_grouped = (
#         pop_df[["Nom_Districte", "Valor"]]
#         .groupby("Nom_Districte", as_index=False)
#         .sum()
#     )
#     superficie_grouped = (
#         superficie_df[["Nom_Districte", "Superficie (ha)"]]
#         .groupby("Nom_Districte", as_index=False)
#         .sum()
#     )

#     return pop_grouped.merge(superficie_grouped, on="Nom_Districte", how="left")


# gdf_transport_age, gdf_transport_age_json = load_transport_age_data()
# df_transport_age_pie = load_transport_age_pie_data()
# df_transport_type_pie = load_transport_type_pie_data()
# gdf_transport_type, gdf_transport_type_json = load_transport_type_data()
# gdf_transport_pop, gdf_transport_pop_json = load_transport_pop_data()
# df_transport_pop_hist = load_transport_pop_hist_data()
# gdf_transport_kmeans, gdf_transport_kmeans_json = load_kmeans_data(
#     gdf_transport_age, gdf_transport_type, gdf_transport_pop
# )

# pourcentage_vehicules_20_ans = (
#     gdf_transport_age.Vehicles_20_Any.sum()
#     / gdf_transport_age.Total_Vehicles.sum()
#     * 100
# )
# pourcentage_vehicules_verts = (
#     gdf_transport_type.Green_Vehicles.sum()
#     / gdf_transport_type.Total_Vehicles.sum()
#     * 100
# )
# nombre_vehicules_par_100_habitants = (
#     gdf_transport_pop.Total_Vehicles.sum() / gdf_transport_pop.Population.sum() * 100
# )

# # --- Socio-economic DATA ---

# def load_socio_economic_data() -> pd.DataFrame:
#     pop_df = pd.read_csv(DATA_PATH + '/pred/2021_pad_mdba_sexe_edat-1.csv')
#     income_df = pd.read_csv(DATA_PATH + '/pred/2021_renda_disponible_llars_per_persona.csv')
#     household_df = pd.read_csv(DATA_PATH + '/pred/2021_pad_dom_mdbas_n-persones.csv')
#     area_df = pd.read_csv(DATA_PATH + '/pred/2021_superficie.csv')

#     # Remplacement des valeurs censurées (inférieures à 5) par 2 (arbitraire)
#     pop_df['Valor'] = pop_df['Valor'].str.replace('..', '2').astype(int)

#     # Calcul l'âge moyen pour chaque barri
#     df: pd.DataFrame = pop_df.groupby(['Codi_Barri', 'Nom_Barri']).apply(lambda x: np.average(x['EDAT_1'], weights=x['Valor']), include_groups=False).sort_values(ascending=False).reset_index(name='Age_Mean')

#     # Calcul la proportion de femmes pour chaque barri
#     df = df.merge(pop_df.groupby('Codi_Barri').apply(lambda x: np.average(x['SEXE']-1, weights=x['Valor']), include_groups=False).sort_values(ascending=False).reset_index(name='Gender_Proportion'), on='Codi_Barri')

#     # Calcul la population de chaque barri
#     df = df.merge(pop_df.groupby('Codi_Barri')['Valor'].sum().sort_values(ascending=False).reset_index(name='Population'), on='Codi_Barri')

#     # Calcul le revenu disponible moyen pour les foyers de chaque barri
#     df = df.merge(income_df.groupby('Codi_Barri')['Import_Euros'].mean().sort_values(ascending=False).reset_index(name='Income_Mean'), on='Codi_Barri')

#     # Calcul le nombre moyen de personnes par foyer pour chaque barri
#     df =  df.merge(household_df.groupby('Codi_Barri').apply(lambda x: np.average(x['N_PERSONES_AGG'], weights=x['Valor']), include_groups=False).sort_values(ascending=False).reset_index(name='N_People_per_Household'), on='Codi_Barri')

#     # Ajout de la superficie de chaque barri
#     df = df.merge(area_df[['Codi_Barri', 'Superfície (ha)']], on='Codi_Barri')

#     # Calcul la densité de population pour chaque barri
#     df['Pop_Density'] = df['Population'] / df['Superfície (ha)']

#     # drop les colonnes inutiles
#     df = df.drop(columns=['Population', 'Superfície (ha)'])

#     return df


# def load_barri_data() -> gpd.GeoDataFrame:
#     barri_df = pd.read_csv('data/pred/BarcelonaCiutat_Barris.csv')
#     barri_df = convert_wkt_to_geometry(barri_df, 'geometria_wgs84')
#     barri_df.crs = 'EPSG:4326'

#     return barri_df


# def socio_economic_pca(df: pd.DataFrame) -> tuple:
#     # Standardize the data
#     X = df[['Age_Mean', 'Gender_Proportion', 'Income_Mean', 'N_People_per_Household', 'Pop_Density']].values
#     X = (X - X.mean(axis=0)) / X.std(axis=0)

#     # Apply PCA
#     pca = PCA(n_components=2)
#     X_pca = pca.fit_transform(X)

#     # Create a DataFrame with the PCA results
#     pca_df = pd.DataFrame(data=X_pca, columns=['PC1', 'PC2'])

#     return pca, pca_df


# def inertia_kmeans(df: pd.DataFrame) -> list:
#     # Calculate the sum of squared distances for a range of cluster numbers
#     inertia = []
#     K = range(1, 11)
#     for k in K:
#         kmeans = KMeans(n_clusters=k, random_state=0).fit(df)
#         inertia.append(kmeans.inertia_)

#     return inertia


# def socio_economic_kmeans(df: pd.DataFrame) -> pd.DataFrame:
#     kmeans_pca = KMeans(n_clusters=4, random_state=0).fit(df[['PC1', 'PC2']])
#     df['Cluster'] = kmeans_pca.labels_

#     return df

# socio_eco_df = load_socio_economic_data()
# barri_df = load_barri_data()
# pca, pca_df = socio_economic_pca(socio_eco_df)
# inertia = inertia_kmeans(pca_df)
# kmeans_df = socio_economic_kmeans(pca_df)
# map_df = barri_df.merge(pca_df, left_on='codi_barri', right_on='Codi_Barri')