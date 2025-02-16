from dash import register_page, Output, Input, State, dcc, callback, html
import dash_mantine_components as dmc

from data.load_and_process_data import gdf_air, gdf_json
from view.noise_air import map_air_quality, histo_air_rang

register_page(__name__, path="/noise_air", name="Bruit & Air", title="OPENDATA")


def layout():
    return dmc.Paper(
        dmc.Stack(
            [
                dmc.Title("Qualité de l'air à Barcelone en 2023", order=1),
                dmc.Text(
                    [
                        "La qualité de l'air à Barcelone en 2023 est une préoccupation majeure en raison des niveaux de pollution observés dans la ville. Les concentrations de particules fines, notamment le PM10, varient selon les zones urbaines, influencées par la circulation, l'activité industrielle et les conditions météorologiques. Bien que la plupart des mesures restent en dessous de la de l'objectif de qualité et la limite de protection de la santé humaine indiqué par l'OMS et l'Union Européenne [",
                        dmc.Anchor(
                            "source",
                            href="https://www.europarl.europa.eu/RegData/etudes/STUD/2018/625114/EPRS_STU(2018)625114_FR.pdf#page=33",
                            target="_blank",
                        ),
                        "], certaines zones dépassent l’objectif de qualité recommandé.",
                    ]
                ),
                dmc.SegmentedControl(
                    id="SegmentedControl-air",
                    value="NO2",
                    data=[
                        {"label": "NO2", "value": "NO2"},
                        {"label": "PM10", "value": "PM10"},
                        {"label": "PM2.5", "value": "PM2_5"},
                    ],
                ),
                dmc.Title(
                    [
                        "Brève description du polluants [",
                        dmc.Anchor(
                            "source",
                            href="https://www.europarl.europa.eu/RegData/etudes/STUD/2018/625114/EPRS_STU(2018)625114_FR.pdf#page=15",
                            target="_blank",
                            style={"fontSize": "var(--mantine-h3-font-size)"},
                        ),
                        "]",
                    ],
                    order=3,
                ),
                dmc.Text(
                    "Le dioxyde d’azote (NO2) est émis au cours de la combustion de combustibles, par exemple, dans les sites industriels et le secteur des transports (principalement des véhicules à moteur diesel). Voici un tableau résumant les normes de qualité de l'air pour celui-ci :",
                    id="text-air",
                ),
                get_regulations_table(),
                dmc.Divider(),
                figures(),
            ]
        ),
        withBorder=True,
        p="md",
    )


def get_regulations_table():
    return dmc.Center(
        dmc.Table(
            id="table-regulations-air",
            highlightOnHover=True,
            withTableBorder=True,
            withColumnBorders=True,
            data={
                "caption": "Tableau des normes Qualité de l'Air du NO2",
                "head": ["Catégorie", "Valeur"],
                "body": [
                    ["Valeurs guides de l’OMS", "40 μg/m³ (moyenne annuelle)"],
                    [
                        "Normes de l’Union européenne",
                        "40 μg/m³ (moyenne annuelle)",
                    ],
                ],
            },
            # style={"width": "75%"},
        )
    )


def figures():
    return dmc.Group(
        [
            html.Iframe(
                id="air-quality-map",
                srcDoc=map_air_quality(gdf_air, gdf_json, "NO2"),
                width="100%",
                height="450px",
                style={"border": "none"},
            ),
            dcc.Graph(
                id={"type": "graph", "index": "histo_air_rang"},
                figure=histo_air_rang(gdf_air, "NO2", [2.5, 2.5]),
            ),
        ],
        grow=True,
    )


# --- CALLBACKS ---


@callback(
    Output("text-air", "children"),
    Output("table-regulations-air", "data"),
    Output("air-quality-map", "srcDoc"),
    Output({"type": "graph", "index": "histo_air_rang"}, "figure"),
    Input("SegmentedControl-air", "value"),
    State("mantine-provider", "forceColorScheme"),
    prevent_initial_call=True,
)
def select_value(polluant, color_scheme):
    map = map_air_quality(gdf_air, gdf_json, polluant)

    if polluant == "NO2":
        text = "Le dioxyde d’azote (NO2) est émis au cours de la combustion de combustibles, par exemple, dans les sites industriels et le secteur des transports (principalement des véhicules à moteur diesel). Voici un tableau résumant les normes de qualité de l'air pour celui-ci :"
    elif polluant == "PM10":
        text = "Des particules solides ou liquides, de taille et composition chimique variables. Les PM10 sont inférieures ou égales à 10 micromètres. Les PM primaires sont directement émises par des sources naturelles (le sel marin, la poussière naturellement en suspension, le pollen et les cendres volcaniques) et par des sources anthropiques (provenant de la combustion, des systèmes de chauffage, des transports, de l’industrie, de l’agriculture, ainsi que de l’usure des pneus et des routes). Voici un tableau résumant les normes de qualité de l'air pour celui-ci :"
    else:
        text = "Des particules solides ou liquides, de taille et composition chimique variables. Les PM2.5 sont inférieures ou égales à 2.5 micromètres. Les PM primaires sont directement émises par des sources naturelles (le sel marin, la poussière naturellement en suspension, le pollen et les cendres volcaniques) et par des sources anthropiques (provenant de la combustion, des systèmes de chauffage, des transports, de l’industrie, de l’agriculture, ainsi que de l’usure des pneus et des routes). Voici un tableau résumant les normes de qualité de l'air pour celui-ci :"

    objectif = {"NO2": 40, "PM10": 30, "PM2_5": 10}[polluant]
    limite = {"NO2": 40, "PM10": 40, "PM2_5": 20}[polluant]
    x = {"NO2": [2.5, 2.5], "PM10": [3.5, 5.5], "PM2_5": [0.5, 2.5]}[polluant]
    data_table = {
        "caption": f"Tableau des normes Qualité de l'Air du {polluant.replace('_', '.')}",
        "head": ["Catégorie", "Valeur"],
        "body": [
            ["Valeurs guides de l’OMS", f"{objectif} μg/m³ (moyenne annuelle)"],
            [
                "Normes de l’Union européenne",
                f"{limite} μg/m³ (moyenne annuelle)",
            ],
        ],
    }
    return text, data_table, map, histo_air_rang(gdf_air, polluant, x, color_scheme)
