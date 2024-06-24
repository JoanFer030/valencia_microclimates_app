from dash import html, dcc
from .navbar import create_navbar
from dash.dependencies import Input, Output
import plotly.express as px
from app import app
from data import get_data

nav = create_navbar()
text = dcc.Markdown('''
    #### Dash and Markdown
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur mattis enim eget metus vulputate ultrices. Duis aliquet turpis non magna egestas semper. Nulla vel arcu rutrum, consequat nibh ac, euismod velit. Nunc tempor, dolor suscipit dignissim interdum, justo diam efficitur est, et facilisis velit tortor sit amet mauris. Nulla sit amet imperdiet lorem. Sed imperdiet felis in euismod pellentesque. Quisque sit amet malesuada sem. Nulla id ornare risus. Morbi pellentesque, dui non ultrices euismod, nisl nisl bibendum erat, nec commodo erat mauris vel orci. Phasellus interdum, magna quis efficitur ullamcorper, elit enim facilisis lacus, sed posuere lacus mauris non lacus. Etiam quis venenatis nisl, aliquet iaculis nisl. Cras iaculis hendrerit volutpat. Vestibulum gravida nisi sed risus bibendum finibus ac quis nisl. Donec pellentesque velit in placerat porttitor.Suspendisse potenti. In congue dolor sit amet metus maximus maximus. Praesent eleifend a nisi sed vehicula. Aliquam erat volutpat. Nulla pellentesque eros mauris, at rutrum nisi ornare vel. Vivamus lobortis justo quis luctus dictum. Pellentesque dictum tristique ante nec imperdiet. Praesent consequat rhoncus enim et blandit. Pellentesque sed ullamcorper diam. Nam at nulla et mauris tempus scelerisque eget nec nisl. Ut scelerisque mi id ex rhoncus malesuada. Mauris at malesuada neque. Proin sagittis feugiat mi, quis porttitor lacus condimentum sit amet. Nulla molestie aliquam luctus.Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Fusce ornare vitae augue non lacinia. In semper venenatis laoreet. Nulla sollicitudin libero et lobortis facilisis. Etiam lorem libero, imperdiet ac porttitor ut, ultricies et massa. Proin eget diam in tellus scelerisque posuere. Proin risus enim, sagittis eget orci ut, imperdiet semper neque. In mattis accumsan lorem at bibendum.
''')

weather_pollution = get_data("weather-pollution")
grouped = weather_pollution.groupby(["station", "date"]).mean().reset_index()
stations = list(weather_pollution["station"].unique())
weather_opts = ["Temperature", "Humidity", "Rainfall", "Wind Speed"]
weather_mag = ["ºC", "%", "mm", "km/h"]
pollution_opts = ["NO", "NO2", "O3", "CO", "SO2", "PM 2.5", "PM 10"]

@app.callback(
    Output("weather_plot", "figure"),
    [Input("stations_selector", "value"), Input("measure_weather_selector", "value")])
def get_weather_plot(stations, measure):
    if isinstance(stations, str):
        stations = [stations]
    filtered = grouped[grouped["station"].isin(stations)]
    measure_ = measure.replace(" ", "_").lower()
    fig = px.line(filtered, x = "date", y = measure_, color = "station")
    fig.update_layout(
        title = "Climate measures",
        xaxis_title = "Date",
        yaxis_title = f"{measure} ({weather_mag[weather_opts.index(measure)]})",
        showlegend = False,
        height = 550
    )
    fig.update_traces(mode="lines", hovertemplate=None)
    fig.update_layout(hovermode="x unified")
    return fig

@app.callback(
    Output("pollution_plot", "figure"),
    [Input("stations_selector", "value"), Input("measure_pollution_selector", "value")])
def get_pollution_plot(stations, measure):
    if isinstance(stations, str):
        stations = [stations]
    filtered = grouped[grouped["station"].isin(stations)]
    measure_ = measure.replace(" ", "").replace(".", "_").lower()
    fig = px.line(filtered, x = "date", y = measure_, color = "station")
    fig.update_layout(
        title = "Contaminant measures",
        xaxis_title = "Date",
        yaxis_title = f"{measure} (PPM)",
        showlegend = False,
        height = 550
    )
    fig.update_traces(mode="lines", hovertemplate=None)
    fig.update_layout(hovermode="x unified")
    return fig

stations_selc = dcc.Dropdown(
    id = "stations_selector",
    options = stations,
    value = stations[6],
    clearable = True,
    multi = True,
    )
weather = dcc.Dropdown(
    id = "measure_weather_selector",
    options = weather_opts,
    value = weather_opts[0],
    clearable = False,
    multi = False,
    )
pollution = dcc.Dropdown(
    id = "measure_pollution_selector",
    options = pollution_opts,
    value = pollution_opts[0],
    clearable = False,
    multi = False,
    )

def create_page_home():
    layout = html.Div([
        nav,
        text,
        html.Div([
            dcc.Graph(id = "weather_plot",
                      style = {'height': 'auto'}),
        ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        html.Div([
            html.Br(),
            html.P("Select station:"),
            stations_selc,
            html.Br(),
            html.Br(),
            html.P("Select climate measure:"),
            weather,
            html.Br(),
            html.Br(),
            html.P("Select contaminant measure:"),
            pollution
        ], style={'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        html.Div([
            dcc.Graph(id = "pollution_plot",
                      style = {'height': 'auto'}),
        ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ])
    return layout