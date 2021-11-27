import owlready2 as owl
import numpy as np
import pandas as pd

filename_onto_individuals = "./ontology/final-archi-individuals.owl"


def fprint(*args, **kwargs):
    print(args, flush=True, **kwargs)


def init_ontology_individuals():
    fprint("Loading ontology...", end=" ")
    onto_individuals = owl.get_ontology(filename_onto_individuals).load()
    fprint("Ontology loaded !")
    return onto_individuals


df_all_airports = None
df_all_runways = None
df_all_frequencies = None
df_all_navaids = None



def init_dataframes_individuals():
    global df_all_airports, df_all_runways, df_all_frequencies, df_all_navaids
    fprint("Loading individuals", end=" ")
    df_all_airports = init_df_all_airports()
    df_all_runways = init_df_all_runways()
    df_all_frequencies = init_df_all_frequencies()
    df_all_navaids = init_df_all_navaids()
    fprint("Individuals loaded !")
    return



def init_df_all_airports():
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



# ======================================================================================
# ================ MAP QUERIES =========================================================
# ======================================================================================


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
    return df_all_navaids.to_dict('records')


# ======================================================================================
# ================ USER QUERIES ========================================================
# ======================================================================================

def query_nearest_airport(lat, lng):
    response = list(owl.default_world.sparql(
        f"""
        PREFIX pie:<http://www.semanticweb.org/clement/ontologies/2020/1/final-archi#>
        SELECT ?Name ?icao ?lat ?long
        WHERE {{
            ?Airport pie:AirportICAOCode ?icao .
            ?Airport pie:AirportName ?Name .
            ?Airport pie:AirportGPSLongitude ?long .
            ?Airport pie:AirportGPSLatitude ?lat .
            }}
        """))

    l = np.array(response)

    df=  pd.DataFrame({
        'name': l[:, 0],
        'ICAO': l[:, 1],
        'lat': l[:, 2],
        'lng': l[:, 3],
    })

    df['lat'] = pd.to_numeric(df['lat'], downcast="float")
    df['lng'] = pd.to_numeric(df['lng'], downcast="float")

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



# ======================================================================================
# ================ UTILS ===============================================================
# ======================================================================================
def coord_to_dist(cur_lat, cur_long, dest_lat, dest_long):
    cur_lat = cur_lat*np.pi/180
    cur_long = cur_long*np.pi/180
    dest_lat = dest_lat*np.pi/180
    dest_long = dest_long*np.pi/180
    return 60*180/np.pi*np.arccos(np.sin(cur_lat)*np.sin(dest_lat)+np.cos(cur_lat)*np.cos(dest_lat)*np.cos(dest_long-cur_long))