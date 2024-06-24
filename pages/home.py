from dash import html, dcc
from .navbar import create_navbar
from dash.dependencies import Input, Output
import plotly.express as px
from app import app
from data import get_data

nav = create_navbar()
title = html.H3("Environmental measurement Stations in Valencia")
text = html.P("Pollution measurement stations in Valencia are essential for monitoring air quality and its components, such as particulate matter (PM10, PM2.5), nitrogen oxides (NOx), sulfur dioxide (SO2), ozone (O3) and carbon monoxide (CO). This information is crucial for understanding air pollution levels and their effects on public health and the environment.")
text2 = html.P("The importance of these stations lies in several key aspects: First, they help control the adverse effects of pollution on local ecosystems, including parks and urban green areas, as well as nearby water resources. They also provide the data needed to develop effective environmental management policies and sustainable urban planning. This includes the creation of green zones, restrictions on vehicular traffic in sensitive areas, and the promotion of cleaner forms of transportation.")

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
        html.Div([
            title, 
            html.Br(),
            text, text2
        ], style = {"margin": "1em"}),
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