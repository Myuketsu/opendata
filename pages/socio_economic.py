from dash import register_page, Output, Input, State, dcc, callback, html
import dash_mantine_components as dmc

from data.load_and_process_data import socio_eco_df, barri_df, pca, pca_df, inertia, kmeans_df
from view.socio_economic import (
    elbow_graph, corr_circle,
)

register_page(__name__, path="/socio-economic", name="Socio-économique", title="OPENDATA")

def layout():
    return dmc.Stack(
        [
            dmc.Title(
                    "Données socio-économiques des barris de la ville de Barcelone en 2021", order=1
                ),
            dmc.Text(
                    "Les donnéees socio-économiques permettent de décrire les caractéristiques des habitants des différents quartiers de Barcelone. Ces caractéristiques ont un impact sur la qualité de vie."
                ),
            dmc.Divider(),
            dmc.Title("ACP et classification", order=3),
            dmc.SimpleGrid(
                [
                    dmc.Text(
                            "L'éboulis des valeurs propres (elbow) permet de déterminer le nombre de composantes principales à retenir. Nous avons choisi de créer 4 clusters pour la classification des quartiers sur nos données après ACP."
                        ),
                    dcc.Graph(
                            id={"type": "graph", "index": "elbow"},
                            figure=elbow_graph(inertia),
                        ),
                ],
                cols=2,
            ),
            html.Img(
                    id={"type": "image", "index": "corr_circle"},
                    src=corr_circle(pca, pca_df, socio_eco_df),
                ),
            dmc.Text(
                    "D'après les graphiques ci-dessus, le cluster 0 regroupe les quartiers les plus riches avec un âge élevé, le cluster 1 regroupe les quartiers les plus jeunes, le cluster 2 regroupe les quartiers densément peuplés et avec un âge élevé et le cluster 3 regroupe les quartiers avec une plus grade proportion de femmes."
                ),
            html.Iframe(
                id="socio-economic-map",
                srcDoc=open(
                    f"./assets/html/socio_economic/barri_clusters.html",
                    "r",
                    encoding="utf-8",
                ).read(),
                width="100%",
                height="450px",
                style={"border": "none"},
            ),
        ]
    )