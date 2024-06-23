from dash import html, dcc
import dash_bootstrap_components as dbc
from .navbar import create_navbar

nav = create_navbar()

def create_page_error():
    layout = html.Div([
        nav,
        html.Div([
            html.H1("404 - Page Not Found"),
            html.P("Sorry, the page you are looking for does not exist."),
            dcc.Link(dbc.Button("Back to Home", color = "primary"), href = "/")
        ], style={"textAlign": "center", "marginTop": "20%"})
    ])
    return layout