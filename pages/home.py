from dash import register_page, dcc
import dash_mantine_components as dmc
import plotly.express as px

register_page(__name__, path='/', name='Menu', title='OPENDATA')

def buttons():
    return 

def layout():
    return dmc.Paper(
        [
            dmc.Group(
                [
                    dmc.Box(
                        dmc.Group(
                            [
                                dmc.Button('Button 1', color='blue'),
                                dmc.Button('Button 2', color='red'),
                                dmc.Button('Button 3', color='green'),
                            ],
                            gap='xl',
                            align='center',
                            grow=True,
                        ),
                    ),
                    dcc.Graph(figure=px.scatter_3d(
                        px.data.iris(),
                        color='species',
                        x='sepal_width',
                        y='sepal_length',
                        z='petal_width',
                        title='Iris Dataset'
                    ), id={'type': 'graph', 'index': 'iris_line'}),
                ],
                justify='space-between',
                grow=True,
                gap='xl',
            )
        ],
        withBorder=True,
        p='md',
    )