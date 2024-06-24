import json
import requests
import pandas as pd
from datetime import datetime
from utils import exists, calculate_tree_density, calculate_traffic

def get_json_data(id_name, type_request = "get"):
    # Descarga los datos y los devuelve
    if type_request == "get":
        url = f"https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/{id_name}/exports/json?lang=es&timezone=Europe%2FBerlin"
    elif type_request == "info":
        url = f"https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/catalogo-de-datos-abiertos/records?select=modified&where=dataset_id%3D%22{id_name}%22&limit=20"
    r = requests.get(url)
    if r.status_code == 200:
        data = json.loads(r.content)
    else:
        raise Exception("Only existing name can be used")
    return data

def last_update(info):
    id_name = info[1]
    if id_name in ["0", "1"]:
        return datetime.strptime(info[2], "%Y-%m-%d")
    # Devuelve la fecha de actualización
    info_data = get_json_data(id_name, "info")
    date = info_data["results"][0]["modified"]
    date = date.split("T")[0]
    date = datetime.strptime(date, "%Y-%m-%d")
    return date

def update_metadata(info, api_last_update):
    date = datetime.strftime(api_last_update, "%Y-%m-%d")
    id_name = info[1]
    # Actualizar Archimo metadatos
    with open("data/metadata.txt", "r") as file:
        upt_info = []
        for line in file.read().splitlines():
            line = line.split(",")
            if line[1] == id_name:
                line[2] = date
            if line[0] in ["model", "month-weather"]:
                line[1] = "0"
            upt_info.append(",".join(line)) 
    with open("data/metadata.txt", "w") as file:
        txt = "\n".join(upt_info)
        file.write(txt)

def update_data(data, path):
    data.to_json(path, indent = 4, orient = "records")

def load_data(info):
    # Carga los datos y los devuelve 
    path = info[3]
    data = pd.read_json(path)
    return data

def download_data(info, api_last_update):
    id_name = info[1]
    # Descargar 
    data_json_raw = get_json_data(id_name)
    data_raw = pd.DataFrame.from_dict(data_json_raw)
    # Preprocesar
    if info[0] == "trees":
        data = data_raw[["nom_comu_c"]]
        data["lon"]  = data_raw["geo_point_2d"].apply(lambda x: dict(x)["lon"])
        data["lat"]  = data_raw["geo_point_2d"].apply(lambda x: dict(x)["lat"])
        data["lon"] = data["lon"].round(3)
        data["lat"] = data["lat"].round(3)
        data = data.groupby(["lon", "lat"]).count().reset_index()
        data = data[["lon", "lat", "nom_comu_c"]]
        data.columns = ["lon", "lat", "n"]
    elif info[0] == "traffic":
        data = data_raw[["idtramo", "des_tramo", "lectura", "geo_shape"]]
        data.columns = ["id", "name", "cars_per_hour", "geo_shape"]
    elif info[0] == "weather-pollution":
        data = data_raw[["estacion", "fecha", "temperatura", "humidad_relativa", "precipitacion", 
                   "velocidad_del_viento", "no", "no2", "o3", "co", "so2", "pm2_5", "pm10"]]
        data.columns = ["station", "date", "temperature", "humidity", "rainfall", "wind_speed",
                 "no", "no2", "o3", "co", "so2", "pm2_5", "pm10"]
        data["date"] = pd.to_datetime(data["date"])
        data = data[data["date"] >= datetime.strptime("2010-01-01", "%Y-%m-%d")]
        data = data[data["date"] < datetime.strptime("2021-01-01", "%Y-%m-%d")]
    elif info[0] == "stations":
        trees = get_data("trees")
        traffic = get_data("traffic")
        weather_pollution = get_data("weather-pollution")
        data = data_raw[["nombre"]]
        data["lon"]  = data_raw["geo_point_2d"].apply(lambda x: dict(x)["lon"])
        data["lat"]  = data_raw["geo_point_2d"].apply(lambda x: dict(x)["lat"])
        data.columns = ["name", "lon", "lat"]
        tree_dens = []
        cars_day = []
        co = []
        so2 = []
        pm = []
        for name in data["name"].unique():
            dens = calculate_tree_density(data, trees, name)
            cars = calculate_traffic(data, traffic, name)
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
            station_data = weather_pollution[weather_pollution["station"] == names[name]]
            tree_dens.append(dens)
            cars_day.append(cars)
            co.append(station_data["co"].mean())
            so2.append(station_data["so2"].mean())
            pm.append(station_data["pm2_5"].mean())
        data["cars_per_day"] = cars_day
        data["trees"] = tree_dens
        data["co"] = co
        data["so2"] = so2
        data["pm"] = pm
    # Actualizar datos y metadatos
    update_data(data, info[3])
    update_metadata(info, api_last_update)
    # Devolver datos
    return data

def get_data(name):
    status, info = exists(name)
    # Comprobar si existe
    if not status:
        raise Exception("The database does not exist")
    api_last_update = last_update(info)
    local_last_update = info[2]
    local_last_update = datetime.strptime(local_last_update, "%Y-%m-%d")

    # Comprobar si está actualizado
    if local_last_update == api_last_update: 
        # Entonces -> Cargar y devolver
        data = load_data(info)
    else:
        print(f"Updating {name} database...")
        # Sino -> Descargar, preprocesar, actualizar y devolver
        data = download_data(info, api_last_update)
    return data