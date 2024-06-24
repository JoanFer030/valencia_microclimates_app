from data import get_data
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import LinearRegression
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from utils import exists

def get_model_data():
    # Cargar y procesar datos
    stations = get_data("stations")[["name", "cars_per_day", "trees"]]
    weather_pollution = get_data("weather-pollution")
    names = {
        "Universidad Politécnica": "Politecnico",
        "Boulevar Sur": "Bulevard Sud",
        "Molí del Sol": "Moli del Sol",
        "Viveros": "Viveros",
        "Centro": "Valencia Centro",
        "Olivereta": "Conselleria Meteo",
        "Francia": "Avda. Francia",
        "Pista de Silla": "Pista Silla",
        "Dr. Lluch": "Puerto Valencia",
        "Cabanyal": "Nazaret Meteo",
        "Patraix": ""
    }
    stations["name"] = stations["name"].apply(lambda x: names[x])
    weather_pollution = weather_pollution.groupby(["station", "date"]).mean().reset_index()
    weather_pollution = weather_pollution.merge(stations, left_on = "station", right_on = "name")
    weather_pollution = weather_pollution[["temperature", "wind_speed", "rainfall", "co", "so2", "pm2_5", "cars_per_day", "trees"]]
    model_data = weather_pollution.dropna()
    return model_data

def update_models(info, models):
    path = info[3]
    # Guardar modelo
    with open(path, "wb") as file:
        pickle.dump(models, file)

def update_metadata(info):
    date = datetime.strftime(datetime.today(), "%Y-%m-%d")
    name = info[0]
    # Actualizar Archimo metadatos
    with open("data/metadata.txt", "r") as file:
        upt_info = []
        for line in file.read().splitlines():
            line = line.split(",")
            if line[0] == name:
                line[1] = "1"
                line[2] = date
            upt_info.append(",".join(line)) 
    with open("data/metadata.txt", "w") as file:
        txt = "\n".join(upt_info)
        file.write(txt)

def train_models(info):
    # Cargar datos, entrenar modelo y guardarlo
    model_data = get_model_data()
    X = model_data[["temperature", "wind_speed", "rainfall", "cars_per_day", "trees"]]
    y_co, y_so2, y_pm = model_data[["co"]], model_data[["so2"]], model_data[["pm2_5"]]
    co_model = MLPRegressor(hidden_layer_sizes = (10, 10),
                         activation = "tanh")
    co_model.fit(X, y_co)
    so2_model = MLPRegressor(hidden_layer_sizes = (10, 10),
                         activation = "tanh")
    so2_model.fit(X, y_so2)
    pm_model = MLPRegressor(hidden_layer_sizes = (10, 10),
                         activation = "tanh")
    pm_model.fit(X, y_pm)
    models = {"co": co_model, "so2": so2_model, "pm": pm_model}
    update_models(info, models)
    update_metadata(info)
    return models

def load_models(info):
    path = info[3]
    # Carga modelo y lo devuelve
    with open(path, "rb") as file:
        models = pickle.load(file)
    return models

def update_weather():
    weather = get_data("weather-pollution")
    weather = weather[["date", "temperature", "rainfall", "wind_speed", "co", "so2", "pm2_5"]]
    weather["month"] = weather["date"].apply(lambda x: x.month)
    data = weather.groupby("month").mean([""]).reset_index()
    update_metadata(["month-weather"])
    data.to_json("data/month-weather.json", indent = 4, orient = "records")

def get_weather(month):
    status, info = exists("month-weather")
    if not status:
        raise Exception("The databese does not exist")
    path = info[3]
    data = pd.read_json(path)
    month = data[data["month"] == month].to_numpy().tolist()[0][1:]
    return month

def predict(models, values):
    month = get_weather(values[0])
    values = month[1:4] + values[1:]
    predictions = {}
    values = np.array([values])
    for name, model in models.items():
        print(name)
        pred = model.predict(values)
        predictions[name] = pred
    predictions_df = pd.DataFrame({
        "label": predictions.keys(),
        "actual": month[3:],
        "model": list(float(v[0]) for v in predictions.values())
        }
    )
    return predictions_df

def get_models():
    status, info = exists("model")
    if not status:
        raise Exception("The model does not exist")
    updated = bool(int(info[1]))
    # Comprueba si el modelo está acutalizado 
    if updated:
        # Entonces -> carga y lo devuelve
        models = load_models(info)
    else:
        print("There was an update, training the model...")
        # Sino -> Carga datos, entrena, guarda y devuelve
        update_weather()
        models = train_models(info)
    return models