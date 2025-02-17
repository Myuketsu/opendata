from dash import register_page, html, dash_table as dt
import dash_mantine_components as dmc

from view.nature import trees_df, trees_map

register_page(__name__, path="/nature", name="Nature", title="OPENDATA")

def layout():
    return dmc.Paper(
        dmc.Stack(
            [
                dmc.Title("Nature à Barcelone en 2023", order=1),
                dmc.Text("La nature à Barcelone en 2023 est une préoccupation majeure en raison des niveaux de pollution observés dans la ville. Les arbres bénéficient à la ville et aux habitants en protégeant contre le bruit, en absorbant le CO2 et en créant des espaces ombragés. Ils ont aussi une fonction ornementale."),
                dmc.Title("Nombre d'arbres à Barcelone", order=3),
                dmc.Text(
                    "Barcelone est une ville verte avec de nombreux arbres. Voici un tableau résumant le nombre d'arbres par quartier (hors forêts) :",
                    id="text-nature",
                ),
                get_trees_table(),
                dmc.Text(
                    "Ce tableau ne prend pas en compte les forêts de la ville. Ce qui peut expliquer la différence entre le nombre d'arbres et la superficie des quartiers du Nord-Ouest de la ville.",
                    id="text-nature",
                ),
                dmc.Divider(),
                dmc.Title("Heatmap", order=3),
                dmc.Text(
                    "Voici une carte de la densité d'arbres par quartier à Barcelone :",
                    id="text-nature",
                ),
                get_trees_map(),
            ]
        ),
        withBorder=True,
        p="md",
    )


def get_trees_table():
    return dmc.Container(
        dt.DataTable(
            trees_df().to_dict("records"),
            columns=[{"name": i, "id": i} for i in trees_df().columns],
            style_filter={'backgroundColor': '#242424'}, # TODO: automatically manage the theme
            style_header={'backgroundColor': '#242424'},
            style_cell={'backgroundColor': '#242424', 'color': '#C9C9C9'}
        ),
    )

def get_trees_map():
    return dmc.Container(
        html.Iframe(
            id="trees-map",
            srcDoc=trees_map(),
            width="100%",
            height="450px",
            style={"border": "none"},
        )
    )