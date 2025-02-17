from dash import register_page, Output, Input, State, dcc, callback, html
import dash_mantine_components as dmc

from data.load_and_process_data import gdf_air, gdf_noise
from view.life_quality import (
    map_air_quality,
    histo_air_rang,
    line_noise_level,
    histo_noise_sensors,
    noise_distribution,
    map_noise_sensors,
)

register_page(__name__, path="/life_quality", name="Qualité de vie", title="OPENDATA")


def layout():
    return dmc.Stack(
        [noise_level_layout(), air_quality_layout(), trees_quantity_layout()]
    )


# - NOISE LEVEL -


def noise_level_layout():
    return dmc.Paper(
        dmc.Stack(
            [
                dmc.Title(
                    "Niveau de bruit dans la ville de Barcelone en 2023", order=1
                ),
                dmc.Text(
                    "Le bruit est une nuisance environnementale majeure dans les zones urbaines, affectant la santé et le bien-être des habitants. Les niveaux de bruit sont influencés par la circulation, les activités industrielles et commerciales, les activités de loisirs.",
                ),
                dmc.Divider(),
                dmc.Title("Répartition des capteurs sonores", order=3),
                dmc.Text(
                    "L'analyse qui suit met en lumière la répartition des capteurs sonores à Barcelone en 2023, offrant un aperçu des principales sources de bruit dans la ville. Elle permet d'identifier les zones les plus exposées et d'évaluer l'impact des différentes activités urbaines sur l'environnement sonore. Cette étude s'inscrit dans une démarche plus large visant à mieux comprendre les dynamiques du bruit en milieu urbain et à envisager des stratégies d'amélioration du cadre de vie des habitants."
                ),
                generate_noise_sensors_figures(),
                dmc.Text(
                    "Les données révèlent que le bruit à Barcelone en 2023 provient majoritairement des loisirs (55,9 %) et du trafic (32,3 %), ces deux sources représentant à elles seules près de 90 % des nuisances sonores enregistrées. La carte des capteurs met en évidence une forte concentration des bruits liés aux loisirs et à la circulation dans le centre-ville et les zones côtières. D’autres sources, comme les travaux, les zones piétonnes ou les cours d’école, bien que moins présentes, contribuent également à l’environnement sonore urbain."
                ),
                dmc.Divider(),
                dmc.Title("Niveau de bruit", order=3),
                dmc.Text(
                    "L’analyse suivante s’intéresse à l’évolution des niveaux sonores à Barcelone en 2023, mettant en perspective l’intensité moyenne du bruit au fil du temps sur tout les capteurs sonores."
                ),
                generate_noise_figures(),
                dmc.Text(
                    "L’analyse de la distribution des niveaux sonores moyens à Barcelone en 2023 révèle que la majorité des enregistrements se situent entre 55 et 65 dB, correspondant à un environnement modéré à bruyant. Très peu de valeurs descendent en dessous de 50 dB, indiquant une présence sonore constante en milieu urbain. À l’inverse, certaines valeurs dépassent les 70 dB, marquant des périodes où le bruit devient plus intense, notamment lors d’événements spécifiques comme la Saint-Jean. Cette distribution souligne la difficulté d’atteindre un environnement réellement silencieux en ville, avec un niveau sonore de fond toujours présent et des pics occasionnels liés aux activités humaines."
                ),
            ]
        ),
        withBorder=True,
        p="md",
    )


def generate_noise_sensors_figures():
    return dmc.Group(
        dmc.Grid(
            [
                dmc.GridCol(
                    dmc.Container(
                        dmc.Stack(
                            [
                                dmc.Title(
                                    "Répartition des sources de bruit à Barcelone en 2023",
                                    order=5,
                                ),
                                dmc.Switch(
                                    id="switch-noise-distribution",
                                    size="md",
                                    radius="sm",
                                    label="Par disctrict",
                                    checked=False,
                                ),
                                dcc.Graph(
                                    id={"type": "graph", "index": "noise_distribution"},
                                    figure=noise_distribution(gdf_noise, False),
                                ),
                            ]
                        ),
                    ),
                    span=4,
                ),
                dmc.GridCol(
                    dmc.Container(
                        dmc.Stack(
                            [
                                dmc.Title(
                                    "Carte des capteurs de bruit à Barcelone en 2023",
                                    order=5,
                                ),
                                dcc.Graph(
                                    id={"type": "graph", "index": "map_noise_sensors"},
                                    figure=map_noise_sensors(gdf_noise),
                                ),
                            ]
                        ),
                    ),
                    span=8,
                ),
            ],
            grow=True,
            align="center",
        ),
        grow=True,
    )


def generate_noise_figures():
    return dmc.Stack(
        [
            dcc.Graph(
                id={"type": "graph", "index": "line_noise_level"},
                figure=line_noise_level(gdf_noise),
            ),
            dmc.Text(
                [
                    "L’évolution du niveau de bruit moyen à Barcelone en 2023 montre une relative stabilité tout au long de l’année, avec une oscillation régulière qui traduit un cycle jour-nuit bien marqué, en lien avec les périodes d’activité humaine. Toutefois, un pic sonore exceptionnel est observé le 24 juin, correspondant aux festivités de la ",
                    dmc.Anchor(
                        "Saint-Jean",
                        href="https://espagne-tourisme.com/la-saint-jean-en-espagne-une-celebration-enflammee-a-travers-les-regions/",
                        target="_blank",
                    ),
                    ", un événement caractérisé par des célébrations bruyantes, notamment des feux d’artifice et des rassemblements festifs. Cette tendance met en évidence l’influence des rythmes urbains et des événements ponctuels sur l’environnement sonore de la ville.",
                ]
            ),
            dmc.Select(
                label="Type de bruit",
                id="select-noise-source",
                data=[
                    {"group": "Tous type de bruit", "items": ["TOUS"]},
                    {
                        "group": "Type de bruit",
                        "items": list(gdf_noise["source"].unique()),
                    },
                ],
                value="TOUS",
                w=300,
            ),
            dcc.Graph(
                id={"type": "graph", "index": "histo_noise_sensors"},
                figure=histo_noise_sensors(gdf_noise, "TOUS"),
            ),
        ],
    )


# - AIR QUALITY -


def air_quality_layout():
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
                create_air_quality_regulations_table(),
                dmc.Divider(),
                generate_air_quality_figures(),
            ]
        ),
        withBorder=True,
        p="md",
    )


def create_air_quality_regulations_table():
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


def generate_air_quality_figures():
    return dmc.Group(
        [
            html.Iframe(
                id="air-quality-map",
                srcDoc=open(
                    f"./assets/html/air_quality/air_quality_NO2.html",
                    "r",
                    encoding="utf-8",
                ).read(),
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


# - TREES QUANTITY -


def trees_quantity_layout():
    return dmc.Paper(
        dmc.Stack(
            [
                dmc.Title("Nombre d'arbres à Barcelone", order=1),
                dmc.Text(
                    "Barcelone est une ville verte avec de nombreux arbres. La carte suivante illustre la densité d’arbres par kilomètre carré dans les divers secteurs de la ville, mettant en évidence les variations de couverture végétale selon les zones.",
                    id="text-nature",
                ),
                dmc.Group(
                    html.Iframe(
                        id="trees-map",
                        srcDoc=open(
                            f"./assets/html/trees/trees_per_km2.html",
                            "r",
                            encoding="utf-8",
                        ).read(),
                        width="100%",
                        height="450px",
                        style={"border": "none"},
                    ),
                    grow=True,
                ),
                dmc.Text(
                    "L’analyse du graphique révèle que le centre-ville et les quartiers situés au nord de Barcelone présentent une densité d’arbres plus élevée, atteignant jusqu’à 6 400 arbres par km². Cette concentration est probablement due à une politique de verdissement renforcée dans ces zones, ainsi qu'à la présence de parcs et d'espaces verts aménagés. En revanche, les quartiers situés en périphérie sud et sud-ouest affichent une couverture arborée plus faible, avec des densités avoisinant 1 400 à 3 000 arbres par km². "
                ),
            ]
        ),
        withBorder=True,
        p="md",
    )


# --- CALLBACKS ---


@callback(
    Output({"type": "graph", "index": "noise_distribution"}, "figure"),
    Input("switch-noise-distribution", "checked"),
    State("mantine-provider", "forceColorScheme"),
    prevent_initial_call=True,
)
def noise_callback(checked, color_scheme):
    return noise_distribution(gdf_noise, checked, color_scheme)


@callback(
    Output({"type": "graph", "index": "histo_noise_sensors"}, "figure"),
    Input("select-noise-source", "value"),
    State("mantine-provider", "forceColorScheme"),
    prevent_initial_call=True,
)
def noise_callback(source, color_scheme):
    return histo_noise_sensors(gdf_noise, source, color_scheme)


@callback(
    Output("text-air", "children"),
    Output("table-regulations-air", "data"),
    Output("air-quality-map", "srcDoc"),
    Output({"type": "graph", "index": "histo_air_rang"}, "figure"),
    Input("SegmentedControl-air", "value"),
    State("mantine-provider", "forceColorScheme"),
    prevent_initial_call=True,
)
def air_callback(polluant, color_scheme):
    map = open(
        f"./assets/html/air_quality/air_quality_{polluant}.html", "r", encoding="utf-8"
    ).read()

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
