from math import radians, cos, sin, asin, sqrt, pi

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

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r

def calculate_tree_density(stations, trees, name, threshold = 1):
    station = stations[stations["name"] == name]
    sta_lon = station["lon"]
    sta_lat = station["lat"]
    n_trees = 0
    for tree in trees.iterrows():
        tree = tree[1]
        tree_lon = tree["lon"]
        tree_lat = tree["lat"]
        if haversine(sta_lon, sta_lat, tree_lon, tree_lat) <= threshold:
            n_trees += tree["n"]
    area = pi * threshold**2
    density = n_trees/area
    return density

def calculate_traffic(stations, traffic, name, threshold = 0.5):
    station = stations[stations["name"] == name].iloc[0]
    sta_lon = station["lon"]
    sta_lat = station["lat"]
    n_cars = []
    for street in traffic.iterrows():
        street = street[1]
        coords_dict = dict(street["geo_shape"])["geometry"]["coordinates"]
        lon, lat = coords_dict[0]
        lon2, lat2 = coords_dict[1]
        if haversine(sta_lon, sta_lat, lon, lat) <= threshold or haversine(sta_lon, sta_lat, lon2, lat2) <= threshold:
            n_cars.append(street["cars_per_hour"])
    cars_day = max(n_cars, default = 0)*24
    return cars_day