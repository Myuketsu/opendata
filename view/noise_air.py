import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import folium

CENTER_BARCELONA = {"lat": 41.3951, "lon": 2.1734}

# --- Air ---


def get_color_theme(color_scheme: str):
    return (
        pio.templates["mantine_light"]
        if color_scheme == "light"
        else pio.templates["mantine_dark"]
    )


def histo_air_rang(
    gdf: gpd.GeoDataFrame, pollutant: str, color_scheme: str = "dark"
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
    return fig


def map_air_quality(gdf: gpd.GeoDataFrame, polluant: str) -> go.Figure:
    map = folium.Map(
        location=list(CENTER_BARCELONA.values()), tiles="CartoDB Positron", zoom_start=12.3
    )

    # Define a color map for NO2 levels
    color_map = dict(zip(gdf[polluant].cat.categories, px.colors.sequential.Plasma_r))

    def style_function(feature):
        return {
            'fillColor': color_map.get(feature['properties'][polluant], 'gray'),
            'color': color_map.get(feature['properties'][polluant], 'gray'),
            'weight': 2,
            'fillOpacity': 0.6,
        }

    folium.GeoJson(
        gdf.to_json(),
        name="Air Quality",
        tooltip=folium.GeoJsonTooltip(fields=[polluant], aliases=[polluant.replace("_", ".")]),
        style_function=style_function
    ).add_to(map)

    # Add legend
    legend_html = f'''
    <div style="position: fixed; 
                top: 10px; left: 50px; 
                border: 1px solid grey; border-radius: 5px; padding: 1px 3px;
                background-color:white;
                z-index:9999; font-size:18px;
                ">
        <b>Carte de Barcelone des niveaux de {polluant.replace("_", ".")}</b>
    </div>
    <div style="position: fixed; 
                top: 50px; right: 50px; width: 120px; height: {35 + len(gdf[polluant].cat.categories) * 20}px; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color:white;
                padding: 5px 10px;
                ">
        <b>{polluant.replace("_", ".")}</b><br>
        {'<br>'.join(f'<i style="background:{color_map[cat]}">&nbsp;&nbsp;&nbsp;&nbsp;</i> {cat}' for cat in gdf[polluant].cat.categories)}<br>
    </div>
    '''

    map.get_root().html.add_child(folium.Element(legend_html))

    return map.get_root().render()