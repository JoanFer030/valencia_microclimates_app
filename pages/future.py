from dash import html
from .navbar import create_navbar

nav = create_navbar()
header = html.H3("FUTURE PAGE!!")

def create_page_future():
    layout = html.Div([
        nav,
        header
    ])
    return layout