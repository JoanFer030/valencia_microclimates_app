from dash import html, dcc
from .navbar import create_navbar
import plotly.express as px
from model import get_models, predict
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from data import get_data
from app import app

nav = create_navbar()
models = get_models()
weather = get_data("month-weather")[["month", "temperature", "rainfall", "wind_speed"]]
months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

@app.callback(
    Output("actual_model_plot", "figure"),
    [Input("month_selector", "value"), Input("trees_selector", "value"), Input("cars_selector", "value")])
def get_barplot(month, trees, cars):
    predictions = predict(models, [months.index(month)+1, trees[0], cars[0]])
    fig = px.bar(predictions, x = "label", y = ["actual", "model"], 
             barmode = "group", hover_data = {"label":False, "variable": False, "value": ":.4f"},
             labels = {"value": "Value"})
    fig.update_layout(
        title = "Actual vs. Future Pollution",
        xaxis_title = "Pollutant",
        yaxis_title = "PPM",
        legend_title = "Source",
        height = 500
    )
    fig.update_xaxes(
        tickvals = ["co", "so2", "pm"],
        ticktext = ["CO", "SO2", "PM 2.5"]   
    )
    fig.for_each_trace(lambda t: t.update(name={'actual': 'Actual', 'model': 'Model'}.get(t.name, t.name)))
    return fig

@app.callback(
    Output("weather_month_plot", "figure"),
    [Input("month_selector", "value")])
def get_weather(month):
    month_data = weather[weather["month"] == months.index(month)+1]
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        value = round(month_data["temperature"].values[0], 1),
        number = {'suffix': " ºC"},
        title = {"text": 'Temperature<br>'},
        domain = {'row': 0, 'column': 0}))
    fig.add_trace(go.Indicator(
        value = round(month_data["rainfall"].values[0], 2),
        number = {'suffix': " mm"},
        title = {"text": 'Rainfall<br>'},
        domain = {'row': 0, 'column': 1}))
    fig.add_trace(go.Indicator(
        value = round(month_data["wind_speed"].values[0], 1),
        number = {'suffix': " km/h"},
        title = {"text": 'Wind Speed<br>'},
        domain = {'row': 0, 'column': 2}))
    fig.update_layout(
        grid = {'rows': 1, 'columns': 3, 'pattern': "independent"},
        margin=dict(l=0, r=0, t=0, b=0),
        height=150
    )
    return fig

n_trees = dcc.RangeSlider(
    id = "trees_selector",
    min = 500,
    max = 3000,
    value = [1200],
    step = 50,
    tooltip={"placement": "bottom", "always_visible": False},
    marks={
        500: {'label': '500', 'style': {'color': '#ff051a'}},
        1000: {'label': '1K'},
        1500: {'label': '1.5K'},
        2000: {'label': '2K'},
        2500: {'label': '2.5K'},
        3000: {'label': '3K', 'style': {'color': '#17f702'}}
    }
)
n_cars = dcc.RangeSlider(
    id = "cars_selector",
    min = 50000,
    max = 500000,
    step = 12500,
    value = [150000],
    tooltip={"placement": "bottom", "always_visible": False},
    marks={
        50000: {'label': '50K'},
        100000: {'label': '100K'},
        150000: {'label': '150K'},
        200000: {'label': '200K'},
        250000: {'label': '250K'},
        300000: {'label': '300K'},
        350000: {'label': '350K'},
        400000: {'label': '400K'},
        450000: {'label': '450K'},
        500000: {'label': '500K'}
    }
)
month = dcc.Dropdown(
    id = "month_selector",
    options = months,
    value = months[0],
    clearable = False,
    )

title = html.H3("Urban Microclimates")
text = html.P("The machine learning model designed aims to estimate how climate, the number of cars in daily circulation and the density of trees per square kilometer affect the concentration of specific pollutants considered highly dangerous: nitrogen dioxide (NO2), carbon monoxide (CO) and fine particulate matter (PM2.5).")
text2 = html.P("First of all, climate is a crucial factor as it influences the dispersion and stability of pollutants in the atmosphere. Meteorological conditions such as temperature, humidity and wind speed can affect how these pollutants disperse and accumulate in specific areas of a city.")
text3 = html.P("The number of cars in daily circulation represents a direct source of pollutant emissions, especially NO2 and CO, which come mainly from vehicle exhaust. The amount of traffic significantly influences the concentration of these pollutants in the air, being a key indicator for the model. On the other hand, the density of trees per square kilometer plays a crucial role in the mitigation of these pollutants. Trees act as natural filters by absorbing carbon dioxide and other substances, as well as trapping suspended particles in their leaves and branches.")

def create_page_future():
    layout = html.Div([
        nav,
        html.Div([
                title, 
                html.Br(),
                text, text2, text3
            ], style = {"margin": "1em"}),
        html.Div([
            html.P("Select month:"),
            month,
            html.Br(),
            dcc.Graph(id = "weather_month_plot",
                      style = {'height': 'auto'}),
            html.Br(),
            html.P("Select tree density(nº/km²):"),
            n_trees,
            html.Br(),
            html.Br(),
            html.P("Select daily car traffic(nº/day):"),
            n_cars
        ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', "margin": "1%"}),
        html.Div([
            dcc.Graph(id = "actual_model_plot",
                      style = {'height': 'auto'}),
        ], style={'width': '67%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ])
    return layout