import geopandas as gpd
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

CENTER_BARCELONA = {"lat": 41.3951, "lon": 2.1334}


def get_color_theme(color_scheme: str):
    return (
        pio.templates["mantine_light"]
        if color_scheme == "light"
        else pio.templates["mantine_dark"]
    )


# --- Transport ---


def map_transport_age(
    gdf: gpd.GeoDataFrame, gdf_json: str, color_scheme: str = "dark"
) -> go.Figure:
    fig = go.Figure(
        go.Choroplethmapbox(
            geojson=gdf_json,
            locations=gdf.index,
            z=gdf["Percentage"].astype(float),
            colorscale="OrRd",
            marker_opacity=0.7,
            marker_line_width=0.5,
            colorbar_title="Pourcentage (%)",
            text=gdf["Nom_Districte"]
            + "<br>Pourcentage: "
            + gdf["Percentage"].astype(str)
            + "%",
        )
    )

    fig.update_layout(
        title_text="Carte: Pourcentage de véhicules de 20 ans ou plus par district",
        title_x=0,
        mapbox_zoom=10.5,
        mapbox_center=CENTER_BARCELONA,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
    )

    if color_scheme != "dark":
        fig.update_layout(
            mapbox_style="carto-positron",
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="black"),
        )

    else:
        fig.update_layout(
            mapbox_style="carto-darkmatter",
            paper_bgcolor="#242424",
            plot_bgcolor="#242424",
            font=dict(color="white"),
        )

    return fig


def pie_transport_age(df: pd.DataFrame, color_scheme: str = "dark") -> px.pie:
    fig = px.pie(
        df,
        names="Antiguitat",
        values="Nombre",
        title="Répartition d'acienneté des véhicules",
        color_discrete_sequence=px.colors.sequential.Reds,
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(title_x=0)

    if color_scheme != "dark":
        fig.update_layout(
            template="plotly",
            paper_bgcolor="white",
            plot_bgcolor="white",
        )
    else:
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#242424",
            plot_bgcolor="#242424",
            font=dict(color="white"),
        )

    return fig


def map_transport_type(
    gdf: gpd.GeoDataFrame, gdf_json: str, color_scheme: str = "dark"
) -> go.Figure:
    fig = go.Figure(
        go.Choroplethmapbox(
            geojson=gdf_json,
            locations=gdf.index,
            z=gdf["Percentage"].astype(float),
            colorscale="greens",
            marker_opacity=0.7,
            marker_line_width=0.5,
            colorbar_title="Percentage (%)",
            text=gdf["Nom_Districte"]
            + "<br>Percentage: "
            + gdf["Percentage"].astype(str)
            + "%",
            # reversescale=True,
        )
    )

    fig.update_layout(
        title_text="Carte: Pourcentage de véhicules vertes par district",
        title_x=0,
        mapbox_zoom=10.5,
        mapbox_center=CENTER_BARCELONA,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
    )

    if color_scheme != "dark":
        fig.update_layout(
            mapbox_style="carto-positron",
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="black"),
        )

    else:
        fig.update_layout(
            mapbox_style="carto-darkmatter",
            paper_bgcolor="#242424",
            plot_bgcolor="#242424",
            font=dict(color="white"),
        )

    return fig


def pie_transport_type(df: pd.DataFrame, color_scheme: str = "dark") -> px.pie:
    fig = px.pie(
        df,
        names="Tipus_Propulsio",
        values="Nombre",
        title="Répartition des véhicules par type de combustible",
        color_discrete_sequence=px.colors.sequential.Greens_r,
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(title_x=0)

    if color_scheme != "dark":
        fig.update_layout(
            template="plotly",
            paper_bgcolor="white",
            plot_bgcolor="white",
        )
    else:
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#242424",
            plot_bgcolor="#242424",
            font=dict(color="white"),
        )

    return fig


def map_transport_pop(
    gdf: gpd.GeoDataFrame, gdf_json: str, color_scheme: str = "dark"
) -> go.Figure:
    fig = go.Figure(
        go.Choroplethmapbox(
            geojson=gdf_json,
            locations=gdf.index,
            z=gdf["Vehicles_Per_100"].astype(float),
            colorscale="purples",
            marker_opacity=0.7,
            marker_line_width=0.5,
            colorbar_title="Nombre de véhicules (%)",
            text=gdf["Nom_Districte"]
            + "<br>véhicules: "
            + gdf["Vehicles_Per_100"].astype(str)
            + "%",
        )
    )

    fig.update_layout(
        title_text="Carte: Nombre de véhicules par 100 habitants par district",
        title_x=0,
        mapbox_zoom=10.5,
        mapbox_center=CENTER_BARCELONA,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
    )

    if color_scheme != "dark":
        fig.update_layout(
            mapbox_style="carto-positron",
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="black"),
        )

    else:
        fig.update_layout(
            mapbox_style="carto-darkmatter",
            paper_bgcolor="#242424",
            plot_bgcolor="#242424",
            font=dict(color="white"),
        )

    return fig


def hist_transport_pop(df: pd.DataFrame, color_scheme: str = "dark") -> px.histogram:
    fig = px.bar(
        df,
        x="Nom_Districte",
        y="Valor",
        title="Histogramme de papulation et de superficie (ha) par district",
        labels={"Nom_Districte": "District", "Valor": "Valeur"},
        color="Superficie (ha)",
        color_continuous_scale="purples",
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        title_x=0,
    )

    if color_scheme != "dark":
        fig.update_layout(
            mapbox_style="carto-positron",
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="black"),
        )

    # else:
    #     fig.update_layout(
    #         mapbox_style="carto-darkmatter",
    #         paper_bgcolor="#242424",
    #         plot_bgcolor="#242424",
    #         font=dict(color="white"),
    #     )

    return fig


def map_transport_kmeans(
    gdf: gpd.GeoDataFrame, gdf_json: str, color_scheme: str = "dark"
) -> go.Figure:
    cluster_colors = {
        "0": "#1E3A8A",
        "1": "#3B82F6",
        "2": "#60A5FA",
    }

    gdf["Cluster"] = gdf["Cluster"].astype(str)

    colorscale = [
        (i / (len(cluster_colors) - 1), color)
        for i, color in enumerate(cluster_colors.values())
    ]

    fig = go.Figure(
        go.Choroplethmapbox(
            geojson=gdf_json,
            locations=gdf.index,
            z=gdf["Cluster"].astype(int),
            colorscale=colorscale,
            marker_opacity=0.7,
            marker_line_width=0.5,
            showscale=False,
            colorbar_title="Clusters",
            text=gdf["Nom_Districte"] + "<br>Cluster: " + gdf["Cluster"],
        )
    )

    for cluster, color in cluster_colors.items():
        fig.add_trace(
            go.Scattermapbox(
                lat=[None],
                lon=[None],
                mode="markers",
                marker=dict(size=15, color=color),
                name=f"Cluster {cluster}",
            )
        )

    fig.update_layout(
        title_text="Carte: K-means clustering des districts en fonction de l'âge des véhicules, du pourcentage de véhicules verts et du nombre de véhicules par 100 habitants",
        title_x=0,
        mapbox_zoom=10.5,
        mapbox_center=CENTER_BARCELONA,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        legend=dict(title="Clusters"),
    )

    if color_scheme != "dark":
        fig.update_layout(
            mapbox_style="carto-positron",
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="black"),
        )

    else:
        fig.update_layout(
            mapbox_style="carto-darkmatter",
            paper_bgcolor="#242424",
            plot_bgcolor="#242424",
            font=dict(color="white"),
        )

    return fig
