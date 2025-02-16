from dash import register_page, Output, Input, State, dcc, callback, html
import dash_mantine_components as dmc

from data.load_and_process_data import gdf_air
from view.noise_air import map_air_quality, histo_air_rang

register_page(__name__, path="/noise_air", name="Bruit & Air", title="OPENDATA")


def layout():
    return dmc.Paper(
        dmc.Stack(
            [
                dmc.Title("Qualité de l'air à Barcelone en 2023", order=1),
                dmc.SegmentedControl(
                    id="SegmentedControl-air",
                    value="NO2",
                    data=[
                        {"label": "NO2", "value": "NO2"},
                        {"label": "PM2.5", "value": "PM2_5"},
                        {"label": "PM10", "value": "PM10"},
                    ],
                ),
                dmc.Divider(),
                figures(),
            ]
        ),
        withBorder=True,
        p="md",
    )


def figures():
    return dmc.Group(
        [
            html.Iframe(
                id="air-quality-map",
                srcDoc=map_air_quality(gdf_air, "NO2"),
                width="100%",
                height="450px",
                style={"border": "none"},
            ),
            dcc.Graph(
                id={"type": "graph", "index": "histo_air_rang"},
                figure=histo_air_rang(gdf_air, "NO2"),
            ),
        ],
        grow=True,
    )


# --- CALLBACKS ---


@callback(
    Output({"type": "graph", "index": "histo_air_rang"}, "figure"),
    Output("air-quality-map", "srcDoc"),
    Input("SegmentedControl-air", "value"),
    State("mantine-provider", "forceColorScheme"),
)
def select_value(polluant, color_scheme):
    map = map_air_quality(gdf_air, polluant)
    return histo_air_rang(gdf_air, polluant, color_scheme), map
