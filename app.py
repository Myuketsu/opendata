from dash import Dash, _dash_renderer
import dash_mantine_components as dmc

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

_dash_renderer._set_react_version("18.2.0")

from components.app_shell import create_app_shell

app = Dash(
    __name__,
    use_pages=True,
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=False,
    external_stylesheets=dmc.styles.ALL,
)

app.title = "OPENDATA"
app._favicon = "./images/favicon.png"

app.layout = dmc.MantineProvider(
    [create_app_shell(), dmc.NotificationProvider()],
    forceColorScheme="light",
    id="mantine-provider",
)

server = app.server

if __name__ == "__main__":
    app.run(debug=True)
