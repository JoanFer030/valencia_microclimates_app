from data import get_data
from sklearn.ensemble import RandomForestRegressor
import pickle
import numpy as np
import pandas as pd
from datetime import datetime

def exists(name):
    # Carga archivo metadatos
    with open("data/metadata.txt") as file:
        for line in file.read().splitlines():
            # Comprueba si existe 
            if line.split(",")[0] == name:
                # Entoces -> Devuelve True y info
                return (True, line.split(","))
    # Sino -> Devuelve False
    return (False, [])

def get_model_data():
    # Cargar y procesar datos
    valencia_area = 134.6 #km2
    n_trees = len(get_data("trees"))
    trees_km2_valencia = n_trees/valencia_area
    cars_per_day_valencia = np.max(get_data("traffic")["cars_per_hour"])*24
    weather_pollution = get_data("weather-pollution")
    model_data = weather_pollution.groupby("date").mean([""]).reset_index()
    model_data = model_data[["temperature", "wind_speed", "rainfall", "co", "so2", "pm2_5"]].dropna()
    model_data["cars_per_day"] = cars_per_day_valencia
    model_data["trees_per_km2"] = trees_km2_valencia
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
    X = model_data[["temperature", "wind_speed", "rainfall", "cars_per_day", "trees_per_km2"]]
    y_co, y_so2, y_pm = model_data[["co"]], model_data[["so2"]], model_data[["pm2_5"]]
    co_model = RandomForestRegressor(n_estimators = 100)
    co_model.fit(X, y_co)
    so2_model = RandomForestRegressor(n_estimators = 100)
    so2_model.fit(X, y_so2)
    pm_model = RandomForestRegressor(n_estimators = 100)
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