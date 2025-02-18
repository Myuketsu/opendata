from dash import register_page, Output, Input, State, dcc, callback, html
import dash_mantine_components as dmc

from data.load_and_process_data import (
    gdf_transport_age,
    gdf_transport_age_json,
    df_transport_age_pie,
    gdf_transport_type,
    gdf_transport_type_json,
    df_transport_type_pie,
    gdf_transport_pop,
    gdf_transport_pop_json,
    df_transport_pop_hist,
    gdf_transport_kmeans,
    gdf_transport_kmeans_json,
    pourcentage_vehicules_20_ans,
    pourcentage_vehicules_verts,
    nombre_vehicules_par_100_habitants,
)
from view.transport import (
    map_transport_age,
    pie_transport_age,
    map_transport_type,
    pie_transport_type,
    map_transport_kmeans,
    map_transport_pop,
    hist_transport_pop,
)

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
                        get_transport_stats_table(
                            pourcentage_vehicules_20_ans, pourcentage_vehicules_verts
                        ),
                        dmc.Text(
                            "Les cartes interactives ci-dessous illustrent la répartition des véhicules de plus de 20 ans, "
                            "des véhicules verts par district et la densité de véhicules par habitant."
                        ),
                    ]
                ),
                dmc.Divider(),
                transport_age_section(),
                dmc.Divider(),
                transport_type_section(),
                dmc.Divider(),
                transport_pop_section(),
                dmc.Divider(),
                transport_kmeans_section(),
            ]
        ),
        withBorder=True,
        p="md",
    )


def get_transport_stats_table(
    pourcentage_vehicules_20_ans: float, pourcentage_vehicules_verts: float
) -> dmc.Center:
    return dmc.Center(
        dmc.Table(
            id="table-stats-transport",
            highlightOnHover=True,
            withTableBorder=True,
            withColumnBorders=True,
            data={
                "caption": "Tableau des statistiques sur le transport à Barcelone",
                "head": ["Catégorie", "Valeur"],
                "body": [
                    [
                        "Pourcentage de véhicules de plus de 20 ans",
                        f"{pourcentage_vehicules_20_ans:.2f}%",
                    ],
                    [
                        "Pourcentage de véhicules verts",
                        f"{pourcentage_vehicules_verts:.2f}%",
                    ],
                    [
                        "Nombre de véhicules par 100 habitants",
                        f"{nombre_vehicules_par_100_habitants:.2f}",
                    ],
                ],
            },
            # style={"width": "75%"},
        )
    )


def transport_age_section():
    return dmc.Stack(
        [
            dmc.SimpleGrid(
                [
                    dmc.SimpleGrid(
                        [
                            dmc.Text(
                                [
                                    html.H4(
                                        "🚗 Analyse de l'âge des véhicules",
                                        className="card-title",
                                    ),
                                    html.P(
                                        "Cette carte montre le pourcentage de véhicules de plus de 20 ans par district. "
                                        "Les véhicules anciens sont un facteur clé de pollution atmosphérique, "
                                        "contribuant aux particules fines et aux oxydes d’azote (NOx).",
                                        className="card-text",
                                    ),
                                    html.P(
                                        "Les zones affichant des pourcentages élevés indiquent une flotte vieillissante, "
                                        "ce qui peut être un indicateur de pollution accrue.",
                                        className="card-text",
                                    ),
                                ],
                                id="transportation-age-text",
                            ),
                            dcc.Graph(
                                id="transportation-age-pie",
                                figure=pie_transport_age(df_transport_age_pie),
                            ),
                        ],
                    ),
                    dcc.Graph(
                        id="transportation-age-map",
                        figure=map_transport_age(
                            gdf_transport_age, gdf_transport_age_json
                        ),
                    ),
                ],
                cols=2,
                style={"height": "100%"},
            ),
        ],
    )


def transport_type_section():
    return dmc.Stack(
        [
            dmc.SimpleGrid(
                [
                    dcc.Graph(
                        id="transportation-type-map",
                        figure=map_transport_type(
                            gdf_transport_type, gdf_transport_type_json
                        ),
                    ),
                    dmc.SimpleGrid(
                        [
                            dmc.Text(
                                [
                                    html.H4(
                                        "🌱 Analyse des véhicules verts",
                                        className="card-title",
                                    ),
                                    html.P(
                                        "Cette carte montre le pourcentage de véhicules écologiques par district. "
                                        "Les véhicules hybrides et électriques réduisent les émissions de CO₂ et "
                                        "de polluants atmosphériques, contribuant à une ville plus durable.",
                                        className="card-text",
                                    ),
                                    html.P(
                                        "Les zones avec un fort pourcentage de véhicules verts montrent une adoption "
                                        "plus rapide des solutions de transport propres.",
                                        className="card-text",
                                    ),
                                ],
                                id="transportation-type-text",
                            ),
                            dcc.Graph(
                                id="transportation-type-pie",
                                figure=pie_transport_type(df_transport_type_pie),
                            ),
                        ],
                    ),
                ],
                cols=2,
                style={"height": "100%"},
            ),
        ],
    )


def transport_pop_section():
    return dmc.Stack(
        [
            dmc.SimpleGrid(
                [
                    dmc.SimpleGrid(
                        [
                            dmc.Text(
                                [
                                    html.H4(
                                        "🚗 Analyse de la densité de véhicules",
                                        className="card-title",
                                    ),
                                    html.P(
                                        "Cette carte montre le nombre de véhicules par 100 habitants par district. "
                                        "Les zones avec une forte densité de véhicules peuvent être sujettes à une "
                                        "pollution atmosphérique plus élevée et à des embouteillages.",
                                        className="card-text",
                                    ),
                                    html.P(
                                        "Les quartiers avec une densité de véhicules élevée peuvent bénéficier de "
                                        "solutions de transport en commun et de mobilité douce.",
                                        className="card-text",
                                    ),
                                ],
                                id="transportation-pop-text",
                            ),
                            dcc.Graph(
                                id="transportation-pop-hist",
                                figure=hist_transport_pop(df_transport_pop_hist),
                            ),
                        ],
                    ),
                    dcc.Graph(
                        id="transportation-pop-map",
                        figure=map_transport_pop(
                            gdf_transport_pop, gdf_transport_pop_json
                        ),
                    ),
                ],
                cols=2,
                style={"height": "100%"},
            ),
        ],
    )


def transport_kmeans_section():
    return dmc.Stack(
        [
            dmc.SimpleGrid(
                [
                    dcc.Graph(
                        id="transportation-kmeans-map",
                        figure=map_transport_type(
                            gdf_transport_type, gdf_transport_type_json
                        ),
                    ),
                    dmc.Text(
                        [
                            html.H4(
                                "📊 Analyse des clusters de transport",
                                className="card-title",
                            ),
                            html.P(
                                "Cette carte regroupe les districts en trois clusters en fonction de l'âge "
                                "des véhicules et de leur caractère écologique.",
                                className="card-text",
                            ),
                            html.Ul(
                                [
                                    html.Li(
                                        "Cluster 0 : Zones avec une forte proportion de véhicules anciens et polluants."
                                    ),
                                    html.Li(
                                        "Cluster 1 : Districts en transition entre ancien et moderne."
                                    ),
                                    html.Li(
                                        "Cluster 2 : Quartiers où les véhicules verts et neufs sont dominants."
                                    ),
                                ]
                            ),
                            html.P(
                                "Cette classification permet de cibler les efforts pour réduire la pollution et "
                                "promouvoir des alternatives durables.",
                                className="card-text",
                            ),
                        ],
                        id="transportation-kmeans-text",
                    ),
                ],
                style={"height": "100%"},
            ),
        ],
    )


# --- CALLBACKS ---


@callback(
    Output("transportation-age-map", "figure"),
    Output("transportation-age-pie", "figure"),
    Output("transportation-type-map", "figure"),
    Output("transportation-type-pie", "figure"),
    Output("transportation-pop-map", "figure"),
    Output("transportation-pop-hist", "figure"),
    Output("transportation-kmeans-map", "figure"),
    Input("mantine-provider", "forceColorScheme"),
    # prevent_initial_call=True,
)
def select_value(color_scheme):
    map = map_transport_age(gdf_transport_age, gdf_transport_age_json, color_scheme)
    pie = pie_transport_age(df_transport_age_pie, color_scheme)
    map2 = map_transport_type(gdf_transport_type, gdf_transport_type_json, color_scheme)
    pie2 = pie_transport_type(df_transport_type_pie, color_scheme)
    map3 = map_transport_pop(gdf_transport_pop, gdf_transport_pop_json, color_scheme)
    hist3 = hist_transport_pop(df_transport_pop_hist, color_scheme)
    map4 = map_transport_kmeans(
        gdf_transport_kmeans, gdf_transport_kmeans_json, color_scheme
    )
    return map, pie, map2, pie2, map3, hist3, map4
