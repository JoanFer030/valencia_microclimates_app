from dash import html
from .navbar import create_navbar

nav = create_navbar()
header = html.H3("ERROR PAGE!!")

def create_page_error():
    layout = html.Div([
        nav,
        header
    ])
    return layout