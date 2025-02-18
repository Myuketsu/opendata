import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import folium

CENTER_BARCELONA = {"lat": 41.3951, "lon": 2.1734}


def get_color_theme(color_scheme: str):
    return (
        pio.templates["mantine_light"]
        if color_scheme == "light"
        else pio.templates["mantine_dark"]
    )


# --- Noise ---


def map_noise_sensors(gdf: gpd.GeoDataFrame, color_scheme: str = "dark") -> go.Figure:
    gdf_map = gdf.drop_duplicates("id")
    fig = px.scatter_mapbox(
        gdf_map,
        lat=gdf_map.geometry.y,
        lon=gdf_map.geometry.x,
        color="source",
        hover_name="source",
        hover_data=["noise_level", "district_name", "area_name"],
        center=CENTER_BARCELONA,
        zoom=12,
        width=800,
        template=get_color_theme(color_scheme),
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        legend_title_text="Type de bruit",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )
    return fig


def noise_distribution(
    gdf: gpd.GeoDataFrame, has_district: bool, color_scheme: str = "dark"
) -> go.Figure:
    if has_district:
        fig = px.sunburst(
            gdf.drop_duplicates("id"),
            path=["district_name", "source"],
            template=get_color_theme(color_scheme),
            height=400,
            width=400,
        )
        fig.update_traces(textinfo="label+percent entry")
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
        )
        return fig

    fig = px.pie(
        gdf.drop_duplicates("id").value_counts("source").reset_index(),
        names="source",
        values="count",
        height=400,
        width=400,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label", hole=0.3)
    fig.update_layout(
        showlegend=False,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )
    return fig


def line_noise_level(gdf: gpd.GeoDataFrame, color_scheme: str = "dark") -> go.Figure:
    fig = px.line(
        gdf.groupby("date")["noise_level"].mean().reset_index(),
        x="date",
        y="noise_level",
        title="Niveaux de bruit moyen à Barcelone en 2023",
        template=get_color_theme(color_scheme),
    )

    return fig


def histo_noise_sensors(
    gdf: gpd.GeoDataFrame, source: str, color_scheme: str = "dark"
) -> go.Figure:
    gdf = gdf[gdf["source"] == source] if source != "TOUS" else gdf
    title = (
        f"Distribution des niveaux de bruit moyen des capteurs {source} à Barcelone en 2023"
        if source != "TOUS"
        else f"Distribution des niveaux de bruit moyen des capteurs à Barcelone en 2023"
    )
    fig = px.histogram(
        gdf.groupby(["date"], observed=False)["noise_level"].mean().reset_index(),
        x="noise_level",
        marginal="box",
        title=title,
        template=get_color_theme(color_scheme),
    )

    fig = fig.update_layout(
        xaxis_title="Niveau sonore moyen [dB]",
    )

    # Ajouter les lignes verticales sans annotation dans add_vline
    fig.add_vline(x=40, line_dash="dash", line_color="#0037A7")
    fig.add_vline(x=50, line_dash="dash", line_color="#0097A7")
    fig.add_vline(x=60, line_dash="dash", line_color="#74BE41")
    fig.add_vline(x=70, line_dash="dash", line_color="#D5DE20")
    fig.add_vline(x=80, line_dash="dash", line_color="#EF4429")
    fig.add_vline(x=90, line_dash="dash", line_color="#FF0000")

    # Ajouter des annotations manuelles en dehors du graphique principal
    annotations = [
        dict(
            x=40,
            y=1.1,
            xref="x",
            yref="paper",
            text="Très Faible",
            showarrow=False,
            font=dict(color="#0037A7"),
        ),
        dict(
            x=50,
            y=1.1,
            xref="x",
            yref="paper",
            text="Faible",
            showarrow=False,
            font=dict(color="#0097A7"),
        ),
        dict(
            x=60,
            y=1.1,
            xref="x",
            yref="paper",
            text="Modéré à silencieux",
            showarrow=False,
            font=dict(color="#74BE41"),
        ),
        dict(
            x=70,
            y=1.1,
            xref="x",
            yref="paper",
            text="Bruyant",
            showarrow=False,
            font=dict(color="#D5DE20"),
        ),
        dict(
            x=80,
            y=1.1,
            xref="x",
            yref="paper",
            text="Très Bruyant",
            showarrow=False,
            font=dict(color="#EF4429"),
        ),
        dict(
            x=90,
            y=1.1,
            xref="x",
            yref="paper",
            text="Assourdissant",
            showarrow=False,
            font=dict(color="#FF0000"),
        ),
    ]

    fig.update_layout(annotations=annotations)

    return fig


# --- Air ---


def histo_air_rang(
    gdf: gpd.GeoDataFrame, pollutant: str, x: list[float], color_scheme: str = "dark"
) -> go.Figure:
    if pollutant not in ["NO2", "PM2_5", "PM10"]:
        raise ValueError(f"pollutant {pollutant} not in available pollutants.")

    pollutant_display = pollutant.replace("_", ".")
    fig = px.histogram(
        gdf.value_counts(pollutant).reset_index(),
        x=pollutant,
        y="count",
        category_orders={pollutant: gdf[pollutant].cat.categories},
        title=f"Distribution de la fourchette de valeurs du polluant {pollutant_display} en 2023 à Barcelone",
        template=get_color_theme(color_scheme),
    )
    fig = fig.update_layout(
        yaxis_title=f"Somme des valeurs du polluant {pollutant_display}",
        xaxis_title=f"Fourchette de valeurs du polluant {pollutant_display}, en moyenne annuelle [µg/m3]",
    )
    fig.add_vline(
        x=x[0],
        line_dash="dash",
        line_color="orange",
        annotation_text=" Valeurs guides de l’OMS",
        annotation_position="top",
    )
    fig.add_vline(
        x=x[1],
        line_dash="dash",
        line_color="red",
        annotation_text=" Normes de l’Union européenne",
        annotation_position="top right",
    )
    return fig


def map_air_quality(gdf: gpd.GeoDataFrame, gdf_json: str, polluant: str) -> go.Figure:
    map = folium.Map(
        location=list(CENTER_BARCELONA.values()),
        tiles="CartoDB Positron",
        zoom_start=12.3,
        prefer_canvas=True,
    )

    # Define a color map for NO2 levels
    color_map = dict(zip(gdf[polluant].cat.categories, px.colors.sequential.Plasma_r))

    def style_function(feature):
        return {
            "fillColor": color_map.get(feature["properties"][polluant], "gray"),
            "color": color_map.get(feature["properties"][polluant], "gray"),
            "weight": 2,
            "fillOpacity": 0.6,
        }

    folium.GeoJson(
        gdf_json,
        name="Air Quality",
        tooltip=folium.GeoJsonTooltip(
            fields=[polluant], aliases=[polluant.replace("_", ".")]
        ),
        style_function=style_function,
    ).add_to(map)

    # Add legend
    legend_html = f"""
    <div style="position: fixed; 
                top: 10px; left: 50px; 
                border: 1px solid grey; border-radius: 5px; padding: 1px 3px;
                background-color:white;
                z-index:9999; font-size:18px;
                ">
        <b>Carte de Barcelone des niveaux de {polluant.replace("_", ".")}</b>
    </div>
    <div style="position: fixed; 
                top: 50px; right: 50px; width: 130px; height: {35 + len(gdf[polluant].cat.categories) * 20}px; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color:white;
                padding: 5px 10px;
                ">
        <b>{polluant.replace("_", ".")}</b><br>
        {'<br>'.join(f'<i style="background:{color_map[cat]}">&nbsp;&nbsp;&nbsp;&nbsp;</i> {cat}' for cat in gdf[polluant].cat.categories)}<br>
    </div>
    """

    map.get_root().html.add_child(folium.Element(legend_html))

    return map.get_root().render()

# --- Life Quality ---

def corrplot_score(df: pd.DataFrame, color_scheme: str = "dark") -> go.Figure:
    # Calculate the correlation matrix and round to 2 decimals
    corr_matrix = df[["score_NO2", "score_PM10", "score_PM2_5", "score_noise", "score_trees", "score_hospitals"]].corr().round(2)

    # Create a heatmap using plotly
    fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", title="Matrice de corrélation des scores de qualité de vie")

    # Show the plot
    return fig