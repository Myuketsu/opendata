from dash import (
    dcc,
    page_container,
    Input,
    Output,
    State,
    callback,
    clientside_callback,
    ALL,
    Patch,
    callback_context,
)
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.io as pio

# --- THEME TOGGLE --- #

dmc.add_figure_templates(default="mantine_dark")


def theme_toggle() -> dmc.Switch:
    """
    Creates a theme toggle switch component using Dash Mantine Components.
    The switch toggles between a sun icon (light mode) and a moon icon (dark mode).
    The icons are provided by DashIconify and are styled with specific colors from the default theme.

    Returns
    -------
    dmc.Switch
        A Dash Mantine Components Switch element configured for theme toggling.
    """
    return dmc.Switch(
        offLabel=DashIconify(
            icon="radix-icons:sun",
            width=15,
            color=dmc.DEFAULT_THEME["colors"]["yellow"][8],
        ),
        onLabel=DashIconify(
            icon="radix-icons:moon",
            width=15,
            color=dmc.DEFAULT_THEME["colors"]["yellow"][6],
        ),
        size="md",
        id="color-scheme-toggle",
        persistence=True,
        color="gray",
    )


# --- APP SHELL --- #


def create_app_shell_header() -> dmc.Group:
    """
    Creates the header component for the app shell.

    Returns
    -------
    dmc.Group
        A Dash Mantine Components (dmc) Group containing the header elements.
        The header includes a burger menu button, a title link to the homepage,
        and a theme toggle button. The elements are arranged with space between
        them and styled to occupy the full height and specified padding.
    """
    return dmc.Group(
        [
            dmc.Group(
                [
                    dmc.Burger(
                        id="burger",
                        size="sm",
                        hiddenFrom="sm",
                        opened=False,
                    ),
                    dcc.Link(
                        [
                            dmc.Group(
                                [
                                    dmc.Title("OPENDATA BARCELONE", c="blue"),
                                ]
                            )
                        ],
                        href="/",
                        style={"textDecoration": "none"},
                    ),
                ]
            ),
            theme_toggle(),
        ],
        justify="space-between",
        style={"flex": 1},
        h="100%",
        px="md",
    )


def create_app_shell_navbar_children() -> list[dmc.NavLink, dmc.Divider]:
    """
    Create a list of navigation bar children components for the app shell.

    Returns
    -------
    list
        A list of Dash Mantine Components (dmc) NavLink and Divider components.
    """
    return [
        dmc.NavLink(
            label="Données",
            leftSection=DashIconify(
                icon="material-symbols:info-outline-rounded",
                width=23,
                color=dmc.DEFAULT_THEME["colors"]["blue"][6],
            ),
            href="/readme",
            id={"type": "navlink_navbar", "index": "/readme"},
        ),
        dmc.Divider(
            label=dmc.Group(
                [
                    DashIconify(
                        icon="material-symbols-light:feature-search-outline-rounded",
                        width=20,
                    ),
                    dmc.Text("Thèmes"),
                ],
                gap="xs",
                pb=5,
            ),
            labelPosition="left",
            mt="md",
        ),
        dmc.NavLink(
            label="Qualité de vie",
            leftSection=DashIconify(
                icon="game-icons:life-tap",
                width=23,
                color=dmc.DEFAULT_THEME["colors"]["blue"][6],
            ),
            href="/life_quality",
            id={"type": "navlink_navbar", "index": "/life_quality"},
        ),
        dmc.NavLink(
            label="Transport",
            leftSection=DashIconify(
                icon="material-symbols:commute-outline-rounded",
                width=23,
                color=dmc.DEFAULT_THEME["colors"]["blue"][6],
            ),
            href="/transport",
            id={"type": "navlink_navbar", "index": "/transport"},
        ),
        dmc.NavLink(
            label="Socio-économique",
            leftSection=DashIconify(
                icon="streamline:decent-work-and-economic-growth",
                width=23,
                color=dmc.DEFAULT_THEME["colors"]["blue"][6],
            ),
            href="/socio-economic",
            id={"type": "navlink_navbar", "index": "/socio-economic"},
        ),
    ]


def create_app_shell() -> dmc.AppShell:
    """
    Create and return an AppShell component for the application.
    The AppShell component includes a header, main content area, and a navbar.
    The header height is set to 60 pixels, and the navbar has a width of 250 pixels
    with a breakpoint at 'sm' and is collapsed on mobile devices. Padding for the
    AppShell is set to 'sm'.

    Returns
    -------
    dmc.AppShell
        The configured AppShell component.
    """
    return dmc.AppShell(
        [
            dmc.AppShellHeader(create_app_shell_header()),
            dmc.AppShellMain(page_container.children, id="page-content"),
            dmc.AppShellNavbar(
                id="navbar",
                children=create_app_shell_navbar_children(),
                p="md",
            ),
        ],
        header={"height": 60},
        padding="sm",
        navbar={
            "width": 250,
            "breakpoint": "sm",
            "collapsed": {"mobile": True},
        },
        id="appshell",
    )


# --- CALLBACKS --- #


@callback(
    Output("appshell", "navbar"),
    Input("burger", "opened"),
    State("appshell", "navbar"),
)
def navbar_is_open(opened, navbar) -> dict:
    """
    Update the navbar dictionary to reflect whether it is open or collapsed on mobile.

    Parameters
    ----------
    opened : bool
        A boolean indicating whether the navbar is open (True) or closed (False).
    navbar : dict
        A dictionary representing the current state of the navbar.

    Returns
    -------
    dict
        The updated navbar dictionary with the 'collapsed' state set for mobile.
    """
    navbar["collapsed"] = {"mobile": not opened}
    return navbar


clientside_callback(
    """ 
    (switchOn) => {
       document.documentElement.setAttribute('data-mantine-color-scheme', switchOn ? 'dark' : 'light');  
       return (switchOn ? 'dark' : 'light');
    }
    """,
    Output("mantine-provider", "forceColorScheme"),
    Input("color-scheme-toggle", "checked"),
)


@callback(
    Output({"type": "navlink_navbar", "index": ALL}, "active"),
    Input("_pages_location", "pathname"),
)
def update_navlink(pathname) -> list[bool]:
    """
    Update the navigation link status based on the given pathname.

    Parameters
    ----------
    pathname : str
        The current pathname to compare against the navigation links.

    Returns
    -------
    list of bool
        A list of boolean values indicating whether each navigation link matches the given pathname.
    """
    return [
        control["id"]["index"] == pathname for control in callback_context.outputs_list
    ]


@callback(
    Output({"type": "graph", "index": ALL}, "figure", allow_duplicate=True),
    Input("mantine-provider", "forceColorScheme"),
    State({"type": "graph", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def update_figure(theme, ids) -> list[Patch]:
    # template must be template object rather than just the template string name
    template = (
        pio.templates["mantine_light"]
        if theme == "light"
        else pio.templates["mantine_dark"]
    )
    patched_figures = []
    for _ in ids:
        patched_fig = Patch()
        patched_fig["layout"]["template"] = template
        patched_figures.append(patched_fig)

    return patched_figures
