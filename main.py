"""
Module for displaying the nearest 10 filming locations on the interactive map
"""
import json
import os.path
import sys
from math import sin, cos, pi, sqrt, atan2
from typing import List, Tuple, Optional, Dict
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from folium import Map, FeatureGroup, Marker, Icon


def read_dataset(path: str, year: int) -> List[Tuple[str, str]]:
    """
    Returns dataset as list of tuples (film name, filming location)
    For example:
    """
    with open(path, 'r') as file:
        dataset = []
        lines = file.read().split('\n')
        for line in lines[lines.index("LOCATIONS LIST") + 2:-2]:
            last_tab_index = line.rindex('\t')
            if line[last_tab_index + 1] == '(':
                line = line[:last_tab_index]
            location = line[line.rindex('\t') + 1:]
            name = line[:line.index('\t')]
            line = line[:line.index('\t')]
            if line[-1] == '}':
                line = line[:line.index('{') - 1]
            film_year = line[line.rindex(' '):][2:-1]
            if int(film_year) == year:
                dataset.append((name, location))
        return dataset


def get_coordinates(location: str, geocode) -> Optional[Tuple[float, float]]:
    """
    Returns (lat, lng) by location string
    """
    location = geocode(location)
    if location is None:
        return None
    return location.latitude, location.longitude


def load_geocache() -> Dict[str, Tuple[float, float]]:
    """
    Loads geocache from file
    """
    if os.path.exists("geocache"):
        with open('geocache', 'r', encoding='utf-8') as file:
            return {k: None if v is None else tuple(v) for k, v in json.loads(file.read()).items()}
    else:
        return {}


def save_geocache(cache: Dict[str, Tuple[float, float]]):
    """
    Saves geocache to file
    """
    with open('geocache', 'w', encoding='utf-8') as file:
        file.write(json.dumps(cache))


def create_progress(progress_name: str, total: int) -> Tuple[str, int, int]:
    return progress_name, 0, total


def display_progress(progress: Tuple[str, int, int]):
    sys.stdout.write(f"\r{progress[0]}: {progress[1] / progress[2] * 100:.2f}% ({progress[1]} out of {progress[2]})")
    sys.stdout.flush()


def get_films_with_coordinates(dataset: List[Tuple[str, str]]) ->\
        List[Tuple[str, Tuple[float, float]]]:
    """
    Returns films with coordinates from films with location strings
    """
    geolocator = Nominatim(user_agent="UCU_Lab_Geofilm")
    geocode = RateLimiter(geolocator.geocode)

    filming_locations = []
    cache = load_geocache()
    progress = create_progress("Fetching locations", len(dataset))
    for entry in dataset:
        if entry[1] not in cache:
            cache[entry[1]] = get_coordinates(entry[1], geocode)
        if (coordinates := cache[entry[1]]) is not None:
            filming_locations.append((entry[0], coordinates))
        progress = (progress[0], progress[1] + 1, progress[2])
        display_progress(progress)

    save_geocache(cache)
    return filming_locations


def distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Computes distance between two points
    >>> distance((54, 21), (53, 19))
    172797.4514739205
    """
    r = 6371e3
    phi1 = point1[0] * pi / 180
    phi2 = point2[0] * pi / 180
    delta_phi = (point2[0] - point1[0]) * pi / 180
    delta_lambda = (point2[1] - point1[1]) * pi / 180
    a = sin(delta_phi / 2) * sin(delta_phi / 2) + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) * sin(delta_lambda / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c


def get_nearest_locations(dataset: List[Tuple[str, Tuple[float, float]]],
                          location: Tuple[float, float]) -> List[Tuple[str, Tuple[float, float]]]:
    """
    Returns top 10 nearest locations
    """
    return sorted(dataset, key=lambda x: distance(x[1], location))[-10:]


def get_map(dataset: List[Tuple[str, Tuple[float, float]]], location: Tuple[float, float]) -> Map:
    """
    Creates map with given list of points in dataset
    """
    html_map = Map(location=location, zoom_start=10)
    fg = FeatureGroup(name="Filming locations")

    for entry in dataset:
        fg.add_child(Marker(location=entry[1], popup=entry[-0], icon=Icon()))

    html_map.add_child(fg)
    return html_map


def create_map(path_to_dataset: str, location: Tuple[float, float], year: int):
    dataset = get_films_with_coordinates(read_dataset(path_to_dataset, year))
    nearest_locations = get_nearest_locations(dataset, location)
    html_map = get_map(nearest_locations, location)
    html_map.save('map.html')


create_map("locations_small.list", (54, 21), 2014)
