import dash_bootstrap_components as dbc


def create_navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Microclimates", href="/microclimates")),
            dbc.NavItem(dbc.NavLink("Future", href="/future")),
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="More",
                children=[
                    dbc.DropdownMenuItem("Source Code", href = "https://github.com/JoanFer030/valencia_microclimates_app", target = "_blank"),
                    dbc.DropdownMenuItem(divider=True)
                ],
            ),
        ],
        brand="Urban Microclimates - Valencia",
        brand_href="/",
        sticky="top",
        color="dark",  # Change this to change color of the navbar e.g. "primary", "secondary" etc.
        dark=True,  # Change this to change color of text within the navbar (False for dark text)
    )

    return navbar
