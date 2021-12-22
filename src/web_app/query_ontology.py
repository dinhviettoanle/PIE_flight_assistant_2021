import owlready2 as owl
import pyowm
import numpy as np
import pandas as pd
from csv import reader
from .geo_utils import *

filename_onto_individuals = "./ontology/final-archi-individuals.owl"

OWM_APIKEY = 'a39692b70ec17cf580fbd700f2e4416e'
owm = pyowm.OWM(OWM_APIKEY)
mgr = owm.weather_manager()

def fprint(*args, **kwargs):
    print(args, flush=True, **kwargs)


def init_ontology_individuals():
    """ Initializes the ontology instance from the file
    """
    fprint("Loading ontology...", end=" ")
    onto_individuals = owl.get_ontology(filename_onto_individuals).load()
    fprint("Ontology loaded !")
    return onto_individuals


df_all_airports = None
df_all_runways = None
df_all_frequencies = None
df_all_navaids = None
df_all_waypoints = None
df_all_checklists = None



def init_dataframes_individuals():
    """ Initializes dataframe objects containing Airport, Runway, Frequency, Navaid, Waypoint
    from ontology
    """
    global df_all_airports, df_all_runways, df_all_frequencies, df_all_navaids, df_all_waypoints, df_all_checklists
    fprint("Loading individuals", end=" ")
    df_all_airports = init_df_all_airports()
    df_all_runways = init_df_all_runways()
    df_all_frequencies = init_df_all_frequencies()
    df_all_navaids = init_df_all_navaids()
    df_all_waypoints = init_df_all_waypoints()
    df_all_checklists = init_df_all_checklists()
    fprint("Individuals loaded !")
    return



def init_df_all_airports():
    """ Initializes the airport dataframe from the Airport ontology's object
    """
    all_airports = list(owl.default_world.sparql(
        f"""
            PREFIX pie:<http://www.semanticweb.org/clement/ontologies/2020/1/final-archi#>
            SELECT ?name ?iata ?icao ?latitude ?longitude ?altitude ?country
            WHERE {{
                ?Airport pie:AirportName ?name .
                ?Airport pie:AirportIATA ?iata .
                ?Airport pie:AirportICAOCode ?icao .
                ?Airport pie:AirportGPSLatitude ?latitude .
                ?Airport pie:AirportGPSLongitude ?longitude .
                ?Airport pie:AirportAltitude ?altitude .
                ?Airport pie:AirportCountry ?country .
            }}
        """))
    fields = ['name', 'iata', 'icao', 'latitude', 'longitude', 'altitude', 'country']
    dict_all_airports = [dict(zip(fields, airport_tuple)) for airport_tuple in all_airports]
    return pd.DataFrame(dict_all_airports)


def init_df_all_runways():
    """ Initializes the runway dataframe from the Runway ontology's object
    """
    all_runways = list(owl.default_world.sparql(
        f"""
            PREFIX pie:<http://www.semanticweb.org/clement/ontologies/2020/1/final-archi#>
            SELECT ?icao ?couple ?ident ?altitude ?beg_latitude ?beg_longitude ?end_latitude ?end_longitude
                ?length ?lights ?orientation ?surface ?threshold ?width
            WHERE {{
                ?Airport pie:AirportICAOCode ?icao .
                ?Airport pie:HasRunway ?Runway .
                ?Runway pie:RunwayAltitude ?altitude .
                ?Runway pie:RunwayCouple ?couple .
                ?Runway pie:RunwayBeginGPSLatitude ?beg_latitude .
                ?Runway pie:RunwayBeginGPSLongitude ?beg_longitude .
                ?Runway pie:RunwayEndGPSLatitude ?end_latitude .
                ?Runway pie:RunwayEndGPSLongitude ?end_longitude .
                ?Runway pie:RunwayIdentifier ?ident .
                ?Runway pie:RunwayLength ?length .
                ?Runway pie:RunwayLights ?lights .
                ?Runway pie:RunwayIdentifier ?ident .
                ?Runway pie:RunwayOrientation ?orientation .
                ?Runway pie:RunwaySurface ?surface .
                ?Runway pie:RunwayThresholdLength ?threshold .
                ?Runway pie:RunwayWidth ?width .
            }}
        """))
    fields = ['airport', 'couple', 'ident', 'altitude', 'beg_latitude', 'beg_longitude', 'end_latitude', 'end_longitude', 
            'length', 'lights', 'orientation', 'surface', 'threshold', 'width']
    dict_all_runways = [dict(zip(fields, runway_tuple)) for runway_tuple in all_runways]
    return pd.DataFrame(dict_all_runways)


def init_df_all_frequencies():
    """ Initializes the frequency dataframe from the Frequency ontology's object
    """
    all_frequencies = list(owl.default_world.sparql(
        f"""
            PREFIX pie:<http://www.semanticweb.org/clement/ontologies/2020/1/final-archi#>
            SELECT ?frq_type ?desc ?frq_mhz ?icao
            WHERE {{
                ?Airport pie:AirportICAOCode ?icao .
                ?Airport pie:HasFrequency ?Frequency .
                ?Frequency pie:FrequencyDescription ?desc .
                ?Frequency pie:FrequencyMHz ?frq_mhz .
                ?Frequency pie:FrequencyType ?frq_type .
            }}
        """))
    fields = ['frq_type', 'desc', 'frq_mhz', 'icao']
    dict_all_frequencies = [dict(zip(fields, frq_tuple)) for frq_tuple in all_frequencies]
    return pd.DataFrame(dict_all_frequencies)


def init_df_all_navaids():
    """ Initializes the navaid dataframe from the Navaid ontology's object
    """
    all_navaids = list(owl.default_world.sparql(
        f"""
            PREFIX pie:<http://www.semanticweb.org/clement/ontologies/2020/1/final-archi#>
            SELECT ?ident ?name ?nav_type ?frequency ?latitude ?longitude ?altitude
            WHERE {{
                ?Navaid pie:NavaidIdentifier ?ident .
                ?Navaid pie:NavaidName ?name .
                ?Navaid pie:NavaidType ?nav_type .
                ?Navaid pie:NavaidFrequencyKHz ?frequency .
                ?Navaid pie:NavaidGPSLatitude ?latitude .
                ?Navaid pie:NavaidGPSLongitude ?longitude .
                ?Navaid pie:NavaidAltitude ?altitude .
            }}
        """))
    fields = ['ident', 'name', 'nav_type', 'frequency', 'latitude', 'longitude', 'altitude']
    dict_all_navaids = [dict(zip(fields, navaid_tuple)) for navaid_tuple in all_navaids]
    return pd.DataFrame(dict_all_navaids)


def init_df_all_waypoints():
    """ Initializes the waypoint dataframe from the Waypoint ontology's object
    """
    all_waypoints = list(owl.default_world.sparql(
        f"""
            PREFIX pie:<http://www.semanticweb.org/clement/ontologies/2020/1/final-archi#>
            SELECT ?ident ?country ?latitude ?longitude
            WHERE {{
                ?Waypoint pie:WaypointIdentifier ?ident .
                ?Waypoint pie:WaypointCountryCode ?country .
                ?Waypoint pie:WaypointGPSLatitude ?latitude .
                ?Waypoint pie:WaypointGPSLongitude ?longitude .
            }}
        """))
    fields = ['ident', 'country', 'latitude', 'longitude']
    dict_all_waypoints = [dict(zip(fields, waypoint_tuple)) for waypoint_tuple in all_waypoints]
    return pd.DataFrame(dict_all_waypoints)


def init_df_all_checklists():
    """ Initializes the checklist dataframe from the Checklist ontology's object
    """
    all_checklists = list(owl.default_world.sparql(
        f"""
            PREFIX pie:<http://www.semanticweb.org/clement/ontologies/2020/1/final-archi#>
            SELECT ?type ?model ?content
            WHERE {{
                ?Waypoint pie:ChecklistContent ?content .
                ?Waypoint pie:ChecklistModel ?model .
                ?Waypoint pie:ChecklistType ?type .
            }}
        """))
    fields = ['type', 'model', 'content']
    dict_all_checklists = [dict(zip(fields, checklist_tuple)) for checklist_tuple in all_checklists]
    return pd.DataFrame(dict_all_checklists)




# ======================================================================================
# ================ MAP QUERIES =========================================================
# ======================================================================================
# Queries to update the map on the GUI

def query_map_near_airports(s, n, w, e):
    df_near_airports = df_all_airports.loc[
        df_all_airports['longitude'].between(w, e) & \
        df_all_airports['latitude'].between(s, n)
    ]
    return df_near_airports.to_dict('records')


def query_map_near_runways(s, n, w, e):
    df_near_runways = df_all_runways.loc[
        df_all_runways['beg_longitude'].between(w, e) & \
        df_all_runways['beg_latitude'].between(s, n)
    ]
    return df_near_runways.to_dict('records')


def query_map_near_frequencies(current_icao):
    df_associated_frequencies = df_all_frequencies.loc[
        df_all_frequencies['icao'] == current_icao
    ]
    return df_associated_frequencies.to_dict('records')


def query_map_near_navaids(s, n, w, e):
    df_near_navaids = df_all_navaids.loc[
        df_all_navaids['longitude'].between(w, e) & \
        df_all_navaids['latitude'].between(s, n)
    ]
    return df_near_navaids.to_dict('records')


def query_map_near_waypoints(s, n, w, e):
    df_near_waypoints = df_all_waypoints.loc[
        df_all_waypoints['longitude'].between(w, e) & \
        df_all_waypoints['latitude'].between(s, n)
    ]
    return df_near_waypoints.to_dict('records')

# ======================================================================================
# ================ USER QUERIES ========================================================
# ======================================================================================

def query_nearest_airport(lat, lng):
    df=  pd.DataFrame({
        'name': df_all_airports['name'],
        'ICAO': df_all_airports['icao'],
        'lat': df_all_airports['latitude'],
        'lng': df_all_airports['longitude'],
    })

    df['distance'] = df.apply(lambda x: coord_to_dist(x["lat"], x["lng"], lat, lng), axis=1)
    return df.iloc[df['distance'].idxmin()].to_dict()





def query_runways_at_arrival(icao_arrival):
    response = list(owl.default_world.sparql(
        f"""
            PREFIX pie:<http://www.semanticweb.org/clement/ontologies/2020/1/final-archi#>
            SELECT ?rw_id
            WHERE {{
                ?Airport pie:AirportICAOCode ?airport_icao .
                ?Airport pie:HasRunway ?Runway .
                ?Runway pie:RunwayIdentifier ?rw_id .
                FILTER regex(?airport_icao, "{icao_arrival}", "i")
            }}
        """))

    if len(response) == 0:
        return {"status": False}

    list_runways = [i[0] for i in response]
    return {"status": True, "icao": icao_arrival, "list_runways": list_runways}



def query_temperature_at_airport(icao):
    row = df_all_airports.loc[df_all_airports['icao'] == icao]
    airport_name = row['name'].values[0]
    
    if len(row) == 0:
        return {"status": False}
    
    coord = (float(row['latitude']), float(row['longitude']))
    current_weather = mgr.weather_at_coords(*coord).weather
    temperature = current_weather.temperature('celsius')['temp']
    return {
        "status": True, 
        "temperature": temperature, 
        "airport_name" : airport_name
    }



def query_wind_at_airport(icao):
    row = df_all_airports.loc[df_all_airports['icao'] == icao]
    airport_name = row['name'].values[0]
    
    if len(row) == 0:
        return {"status": False}
    
    coord = (float(row['latitude']), float(row['longitude']))
    current_weather = mgr.weather_at_coords(*coord).weather
    wind_speed = current_weather.wind().get('speed')
    wind_orientation = current_weather.wind().get('deg')
    return {
        "status": True, 
        "wind_speed": wind_speed, 
        "wind_orientation": wind_orientation,
        "airport_name": airport_name
    }


# (Item, Response, ID) -- ID used for DOM, for example if there are many "ON" responses
def get_checklist(type_checklist, model):
    model = 'a320' #### TO DELETE in the future

    row = df_all_checklists.loc[(df_all_checklists['type'] == type_checklist) & (df_all_checklists['model'] == model)]
    checklist_file = row['content'].iloc[0]

    with open(checklist_file, 'r') as read_obj:
        csv_reader = reader(read_obj)
        list_of_rows = list(csv_reader)

    checklist = [(item, response, i+1) for i, (item, response) in enumerate(list_of_rows)]
    return {"status": True, "checklist": checklist}
