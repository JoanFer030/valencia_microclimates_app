from dash import html, dcc
from .navbar import create_navbar
from data import get_data
from app import app
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import folium
from folium.plugins import HeatMap
import branca.colormap as cm
import numpy as np

nav = create_navbar()
text = dcc.Markdown('''
    #### Dash and Markdown
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur mattis enim eget metus vulputate ultrices. Duis aliquet turpis non magna egestas semper. Nulla vel arcu rutrum, consequat nibh ac, euismod velit. Nunc tempor, dolor suscipit dignissim interdum, justo diam efficitur est, et facilisis velit tortor sit amet mauris. Nulla sit amet imperdiet lorem. Sed imperdiet felis in euismod pellentesque. Quisque sit amet malesuada sem. Nulla id ornare risus. Morbi pellentesque, dui non ultrices euismod, nisl nisl bibendum erat, nec commodo erat mauris vel orci. Phasellus interdum, magna quis efficitur ullamcorper, elit enim facilisis lacus, sed posuere lacus mauris non lacus. Etiam quis venenatis nisl, aliquet iaculis nisl. Cras iaculis hendrerit volutpat. Vestibulum gravida nisi sed risus bibendum finibus ac quis nisl. Donec pellentesque velit in placerat porttitor.Suspendisse potenti. In congue dolor sit amet metus maximus maximus. Praesent eleifend a nisi sed vehicula. Aliquam erat volutpat. Nulla pellentesque eros mauris, at rutrum nisi ornare vel. Vivamus lobortis justo quis luctus dictum. Pellentesque dictum tristique ante nec imperdiet. Praesent consequat rhoncus enim et blandit. Pellentesque sed ullamcorper diam. Nam at nulla et mauris tempus scelerisque eget nec nisl. Ut scelerisque mi id ex rhoncus malesuada. Mauris at malesuada neque. Proin sagittis feugiat mi, quis porttitor lacus condimentum sit amet. Nulla molestie aliquam luctus.Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Fusce ornare vitae augue non lacinia. In semper venenatis laoreet. Nulla sollicitudin libero et lobortis facilisis. Etiam lorem libero, imperdiet ac porttitor ut, ultricies et massa. Proin eget diam in tellus scelerisque posuere. Proin risus enim, sagittis eget orci ut, imperdiet semper neque. In mattis accumsan lorem at bibendum.
''')
stations = get_data("stations")
trees = get_data("trees")
stations_opts = stations["name"].unique().tolist()
polls_avg = [stations["co"].mean().tolist(), stations["so2"].mean().tolist(), stations["pm"].mean().tolist()]

@app.callback(
    Output("pollution_station_map", "srcDoc"),
    [Input("station_selector", "value")])
def get_map(station):
    map_ = folium.Map(location=[39.472792543187936, -0.37898723979425947], zoom_start=12.5, tiles='CartoDB positron')
    heat_data = [[row['lat'], row['lon'], row['n']] for index, row in trees.iterrows()]
    colormap = cm.LinearColormap(['blue', 'lime', 'green'], vmin=min(trees['n']), vmax=max(trees['n']), caption='Trees')
    heat_layer = HeatMap(heat_data, radius=15, gradient={0: 'blue', 0.5: 'lime', 1: 'green'}, name="Trees")
    heat_layer.add_to(map_)
    colormap.add_to(map_)
    stations_layer = folium.FeatureGroup(name="Stations")
    for idx, row in stations.iterrows():
        popup_text = f"{row['name']}<br>Cars per day: {row['cars_per_day'] if row['cars_per_day'] >= 0 else np.nan:,}<br>Trees per km2: {row['trees']:,.0f}"
        folium.Marker(location=[row['lat'], row['lon']], 
                    popup=popup_text,
                    icon=folium.Icon(icon='cloud', prefix='fa', color='blue')).add_to(stations_layer)
    stations_layer.add_to(map_)
    folium.LayerControl().add_to(map_)
    return map_._repr_html_()

@app.callback(
    Output("pollution_station_plot", "figure"),
    [Input("station_selector", "value")])
def get_pollution(station):
    station_data = stations[stations["name"] == station]
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        value = round(station_data["co"].values[0], 3),
        mode = "number+delta",
        delta = {'reference': polls_avg[0], 'relative': True, "valueformat": ".1%",
                 "increasing.color": "red", "decreasing.color": "green"},
        number = {'suffix': " PPM"},
        title = {"text": 'CO<br>'},
        domain = {'row': 0, 'column': 0}))
    fig.add_trace(go.Indicator(
        value = round(station_data["so2"].values[0], 3),
        mode = "number+delta",
        delta = {'reference': polls_avg[1], 'relative': True, "valueformat": ".1%",
                 "increasing.color": "red", "decreasing.color": "green"},
        number = {'suffix': " PPM"},
        title = {"text": 'SO2<br>'},
        domain = {'row': 0, 'column': 1}))
    fig.add_trace(go.Indicator(
        value = round(station_data["pm"].values[0], 3),
        mode = "number+delta",
        delta = {'reference': polls_avg[2], 'relative': True, "valueformat": ".1%",
                 "increasing.color": "red", "decreasing.color": "green"},
        number = {'suffix': " PPM"},
        title = {"text": 'PM 2.5<br>'},
        domain = {'row': 0, 'column': 2}))
    fig.update_layout(
        grid = {'rows': 1, 'columns': 3, 'pattern': "independent"},
        margin=dict(l=0, r=0, t=0, b=0),
        height=150
    )
    return fig

station = dcc.Dropdown(
    id = "station_selector",
    options = stations_opts,
    value = stations_opts[0],
    clearable = False,
    multi = False,
    )

def create_page_microclimates():
    layout = html.Div([
        nav,
        html.Div([
            text
        ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        html.Div([
            html.Div([
                html.Br(),
                html.Br(),
                station
            ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            html.Div([
                dcc.Graph(id = "pollution_station_plot")
            ], style={'width': '60%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            html.Iframe(id = "pollution_station_map", width='100%', height='600')
        ], style={'width': '70%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ])
    return layout