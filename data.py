import json
import requests
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
        data = data_raw[["nom_comu_c", "tipo_situacion"]]
        data["lon"]  = data_raw["geo_point_2d"].apply(lambda x: dict(x)["lon"])
        data["lat"]  = data_raw["geo_point_2d"].apply(lambda x: dict(x)["lat"])
        data.columns = ["name", "location", "lon", "lat"]
    elif info[0] == "traffic":
        data = data_raw[["idtramo", "des_tramo", "lectura", "geo_shape"]]
        data.columns = ["id", "name", "cars_per_hour", "geo_shape"]
    elif info[0] == "weather-pollution":
        data = data_raw[["estacion", "fecha", "temperatura", "humidad_relativa", "precipitacion", 
                   "velocidad_del_viento", "no", "no2", "nox", "o3", "co", "so2", "pm1", "pm2_5", "pm10"]]
        data.columns = ["station", "date", "temperature", "humidity", "rainfall", "wind_speed",
                 "no", "no2", "nox", "o3", "co", "so2", "pm1", "pm2_5", "pm10"]
    elif info[0] == "stations":
        data = data_raw[["nombre"]]
        data["lon"]  = data_raw["geo_point_2d"].apply(lambda x: dict(x)["lon"])
        data["lat"]  = data_raw["geo_point_2d"].apply(lambda x: dict(x)["lat"])
        data.columns = ["name", "lon", "lat"]
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