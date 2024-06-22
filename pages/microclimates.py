from dash import html
from .navbar import create_navbar

nav = create_navbar()
header = html.H3("MICROCLIMATES PAGE!!")

def create_page_microclimates():
    layout = html.Div([
        nav,
        header
    ])
    return layout