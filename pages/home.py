from dash import register_page, dcc, html
import dash_mantine_components as dmc
import plotly.express as px

register_page(__name__, path="/", name="Menu", title="OPENDATA")


def buttons():
    return


def layout():
    return dmc.Paper(
        dmc.Stack(
            [
                dmc.Center(
                    dmc.Text(
                        "OPENDATA BARCELONE",
                        c="blue",
                        style={"fontSize": 80},
                    )
                ),
                dmc.Group(
                    [
                        html.A(
                            dmc.Tooltip(
                                dmc.Avatar(
                                    src="https://media.licdn.com/dms/image/v2/D4E35AQFSpIJW2hjW2A/profile-framedphoto-shrink_400_400/profile-framedphoto-shrink_400_400/0/1732919545126?e=1740456000&v=beta&t=GfbyYnSJ-ZbIpdTebBMQO92Cz-ZXFaoTMmejRXBt6jM",
                                    size="xl",
                                    radius="xl",
                                ),
                                label="Louis Delignac",
                                position="bottom",
                                opened=True,
                                withArrow=True,
                            ),
                            href="https://www.linkedin.com/in/louis-delignac/",
                            target="_blank",
                        ),
                        html.A(
                            dmc.Tooltip(
                                dmc.Avatar(
                                    src="https://media.licdn.com/dms/image/v2/D5603AQET8bVptdt2Zg/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1669659984554?e=1745452800&v=beta&t=g-shxnYzX8fM9M1svwnsHjqG0XqvcBEL8a1Vx8DbJiQ",
                                    size="xl",
                                    radius="xl",
                                ),
                                label="Alexandre Leys",
                                position="bottom",
                                opened=True,
                                withArrow=True,
                            ),
                            href="https://www.linkedin.com/in/alexandre-leys-bdx/",
                            target="_blank",
                        ),
                        html.A(
                            dmc.Tooltip(
                                dmc.Avatar(
                                    src="https://media.licdn.com/dms/image/v2/D4E03AQEK9KHQbK11_Q/profile-displayphoto-shrink_400_400/profile-displayphoto-shrink_400_400/0/1721858475999?e=1745452800&v=beta&t=m4YgzLM6c02MywW3WrU5YOpYMZw8OD65LDdhK0Gzy_I",
                                    size="xl",
                                    radius="xl",
                                ),
                                label="Hamad Tria",
                                position="bottom",
                                opened=True,
                                withArrow=True,
                            ),
                            href="https://www.linkedin.com/in/hamadtria/",
                            target="_blank",
                        ),
                    ],
                    justify="center",
                    gap="64px",
                    top="lg",
                ),
                dmc.Center(
                    html.Img(
                        src="https://swello.com/fr/blog/wp-content/uploads/2019/11/barcelone-swello.jpg",
                        width="650px",
                        height="400px",
                        style={"borderRadius": "10px", "marginTop": "50px"},
                    ),
                ),
            ],
            h="70vh",
        ),
        withBorder=False,
        p="md",
    )
