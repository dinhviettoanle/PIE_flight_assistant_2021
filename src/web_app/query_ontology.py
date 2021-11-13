import owlready2 as owl

filename_onto_individuals = "./ontology/final-archi-individuals.owl"


def fprint(*args, **kwargs):
    print(args, flush=True)


def init_ontology_individuals():
    fprint("Loading ontology...")
    onto_individuals = owl.get_ontology(filename_onto_individuals).load()
    fprint("Ontology loaded !")
    return onto_individuals


def query_map_near_airports(s, n, w, e):
    near_airports = list(owl.default_world.sparql(
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
                FILTER (?longitude > {w} && ?longitude < {e} 
                    &&  ?latitude > {s} && ?latitude < {n})
                
            }}
        """))
    fields = ['name', 'iata', 'icao', 'latitude', 'longitude', 'altitude', 'country']
    return [dict(zip(fields, airport_tuple)) for airport_tuple in near_airports]


def query_map_near_runways(s, n, w, e):
    near_runways = list(owl.default_world.sparql(
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
                FILTER (?beg_longitude > {w} && ?beg_longitude < {e} 
                    &&  ?beg_latitude > {s} && ?beg_latitude < {n})
                
            }}
        """))
    fields = ['airport', 'couple', 'ident', 'altitude', 'beg_latitude', 'beg_longitude', 'end_latitude', 'end_longitude', 
            'length', 'lights', 'orientation', 'surface', 'threshold', 'width']
    return [dict(zip(fields, runway_tuple)) for runway_tuple in near_runways]


def query_map_near_frequencies(current_icao):
    associated_frequencies = list(owl.default_world.sparql(
        f"""
            PREFIX pie:<http://www.semanticweb.org/clement/ontologies/2020/1/final-archi#>
            SELECT ?frq_type ?desc ?frq_mhz 
            WHERE {{
                ?Airport pie:AirportICAOCode ?ICAO .
                ?Airport pie:HasFrequency ?Frequency .
                ?Frequency pie:FrequencyDescription ?desc .
                ?Frequency pie:FrequencyMHz ?frq_mhz .
                ?Frequency pie:FrequencyType ?frq_type .
                FILTER regex(?ICAO, "{current_icao}", "i")
                
            }}
        """))
    fields = ['frq_type', 'desc', 'frq_mhz']
    return [dict(zip(fields, frq_tuple)) for frq_tuple in associated_frequencies]


def query_map_near_navaids(s, n, w, e):
    near_navaids = list(owl.default_world.sparql(
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
                FILTER (?longitude > {w} && ?longitude < {e} 
                    &&  ?latitude > {s} && ?latitude < {n})
                
            }}
        """))
    fields = ['ident', 'name', 'nav_type', 'frequency', 'latitude', 'longitude', 'altitude']
    return [dict(zip(fields, navaid_tuple)) for navaid_tuple in near_navaids]