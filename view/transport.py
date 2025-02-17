import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go

CENTER_BARCELONA = {"lat": 41.3951, "lon": 2.1234}

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
