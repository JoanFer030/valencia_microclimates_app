from dash import html, dcc
from dash.dependencies import Input, Output
from pages.home import create_page_home
from pages.microclimates import create_page_microclimates
from pages.future import create_page_future
from pages.error import create_page_error
from app import app

server = app.server
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname in ["", "/", "/home"]:
        return create_page_home()
    if pathname == "/microclimates":
        return create_page_microclimates()
    if pathname == "/future":
        return create_page_future()
    else:
        return create_page_error()

if __name__ == '__main__':
    app.run_server(debug=False)
