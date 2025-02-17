from dash import register_page, Output, Input, State, dcc, callback, html
import dash_mantine_components as dmc

from data.load_and_process_data import (
    gdf_transport_age,
    gdf_transport_age_json,
    gdf_transport_type,
    gdf_transport_type_json,
)
from view.transport import map_transport_age, map_transport_type

register_page(__name__, path="/transport", name="Transport", title="OPENDATA")


def layout():
    return dmc.Paper(
        dmc.Stack(
            [
                dmc.Title("Le transport à Barcelone en 2023", order=1),
                dmc.Stack(
                    [
                        dmc.Text(
                            "Le transport à Barcelone joue un rôle clé dans la qualité de l’air de la ville.\
                                La circulation dense et l’activité industrielle contribuent aux niveaux de pollution,\
                                notamment aux concentrations de particules fines (PM10),\
                                qui varient selon les districts et les conditions météorologiques.\
                                L’analyse des données permet de mieux comprendre l’impact des véhicules anciens et des transports propres sur l’environnement urbain."
                        ),
                        dmc.Text(
                            "Les cartes interactives ci-dessous illustrent la répartition des véhicules de plus de 20 ans et des véhicules verts par district."
                        ),
                    ]
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
            dcc.Graph(
                id="transportation-age-map",
                figure=map_transport_age(gdf_transport_age, gdf_transport_age_json),
            ),
            dcc.Graph(
                id="transportation-type-map",
                figure=map_transport_type(gdf_transport_type, gdf_transport_type_json),
            ),
        ],
        grow=True,
    )


# --- CALLBACKS ---


@callback(
    Output("transportation-age-map", "figure"),
    Output("transportation-type-map", "figure"),
    Input("mantine-provider", "forceColorScheme"),
    prevent_initial_call=True,
)
def select_value(color_scheme):
    map = map_transport_age(gdf_transport_age, gdf_transport_age_json, color_scheme)
    map2 = map_transport_type(gdf_transport_type, gdf_transport_type_json, color_scheme)
    return map, map2
