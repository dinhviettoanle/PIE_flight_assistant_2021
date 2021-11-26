"""
Individual loader in the ontology

"""
import owlready2 as owl
import pandas as pd
from tqdm.autonotebook import tqdm
from data_loader import AirportLoader, RunwayLoader, NavaidLoader, FrequencyLoader, WaypointLoader

filename_onto = "./ontology/final-archi.owl"
filename_onto_individuals = "./ontology/final-archi-individuals.owl"
onto = owl.get_ontology(filename_onto).load()

# ===================================================================================
# ================ AIRPORTS =========================================================
# ===================================================================================

def create_airport_individuals():
    """ Creates Airport individuals

    Returns
    -------
    dict
        Dictionary conataining Airport individuals
        Keys are ICAO identifiers
    """
    airport_data = AirportLoader().get_airport_data()
    dict_airports = {}
    pbar = tqdm(total=len(airport_data), desc="Airports")
    for i, row in airport_data.iterrows():
        new_airport = onto.Airport(row['icao'])
        new_airport.AirportARFFIndex.append("NA")
        new_airport.AirportAltitude.append(row['altitude'])
        new_airport.AirportCTRActiveHours.append("NA")
        new_airport.AirportCountry.append(row['country'])
        new_airport.AirportEstimatedDepartureTime.append("NA")
        new_airport.AirportEstimatedTimeOfArrival.append("NA")
        new_airport.AirportFuel.append("NA")
        new_airport.AirportGPSLatitude.append(row['latitude'])
        new_airport.AirportGPSLongitude.append(row['longitude'])
        new_airport.AirportHandling.append("NA")
        new_airport.AirportIATA.append(row['iata'])
        new_airport.AirportICAOCode.append(row['icao'])
        new_airport.AirportName.append(row['name'])
        new_airport.AirportOpeningHours.append("NA")
        new_airport.AirportParkingSpot.append("NA")
        new_airport.AirportWidthTaxiway.append(-1)
        dict_airports[row['icao']] = new_airport
        pbar.update(1)
    pbar.close()

    return dict_airports

# ===================================================================================
# ================ RUNWAYS ==========================================================
# ===================================================================================

def create_runway_individuals(dict_airports):
    """ Creates Runway individuals in the ontology

    Parameters
    ----------
    dict_airports : dict
        Dictionary conataining Airport individuals
    """
    runway_data = RunwayLoader().get_runway_data()
    pbar = tqdm(total=len(runway_data), desc="Runways")
    for i, row in runway_data.iterrows():
        this_airport = row['icao']
        # Lowest orientation
        ## Individual
        new_runway_low = onto.Runway(f"{this_airport}-{row['le_ident']}")
        new_runway_low.RunwayAltitude.append(row['le_elevation_ft'])
        new_runway_low.RunwayCouple.append(f"{row['le_ident']}/{row['he_ident']}")
        new_runway_low.RunwayBeginGPSLatitude.append(row['le_latitude_deg'])
        new_runway_low.RunwayBeginGPSLongitude.append(row['le_longitude_deg'])
        new_runway_low.RunwayEndGPSLongitude.append(row['he_longitude_deg'])
        new_runway_low.RunwayEndGPSLatitude.append(row['he_latitude_deg'])
        new_runway_low.RunwayIdentifier.append(row['le_ident'])
        new_runway_low.RunwayLights.append(row['lighted'])
        new_runway_low.RunwayLength.append(row['length_ft'])
        new_runway_low.RunwayOrientation.append(row['le_heading_degT'])
        new_runway_low.RunwayPCN.append("NA")
        new_runway_low.RunwaySurface.append(row['surface'])
        new_runway_low.RunwayThresholdLength.append(row['le_displaced_threshold_ft'])
        new_runway_low.RunwayWidth.append(row['width_ft'])
        ## ObjectProperty
        new_runway_low.BelongsToAirport.append(dict_airports[this_airport])
        dict_airports[this_airport].HasRunway.append(new_runway_low)
        
        # Highest orientation
        new_runway_high = onto.Runway(f"{this_airport}-{row['he_ident']}")
        new_runway_high.RunwayAltitude.append(row['he_elevation_ft'])
        new_runway_high.RunwayCouple.append(f"{row['le_ident']}/{row['he_ident']}")
        new_runway_high.RunwayBeginGPSLatitude.append(row['he_latitude_deg'])
        new_runway_high.RunwayBeginGPSLongitude.append(row['he_longitude_deg'])
        new_runway_high.RunwayEndGPSLatitude.append(row['le_latitude_deg'])
        new_runway_high.RunwayEndGPSLongitude.append(row['le_longitude_deg'])
        new_runway_high.RunwayIdentifier.append(row['he_ident'])
        new_runway_high.RunwayLights.append(row['lighted'])
        new_runway_high.RunwayLength.append(row['length_ft'])
        new_runway_high.RunwayOrientation.append(row['he_heading_degT'])
        new_runway_high.RunwayPCN.append("NA")
        new_runway_high.RunwaySurface.append(row['surface'])
        new_runway_high.RunwayThresholdLength.append(row['he_displaced_threshold_ft'])
        new_runway_high.RunwayWidth.append(row['width_ft'])
        ## ObjectProperty
        new_runway_high.BelongsToAirport.append(dict_airports[this_airport])
        dict_airports[this_airport].HasRunway.append(new_runway_high)
        
        pbar.update(1)
    pbar.close()

# ===================================================================================
# ================ FREQUENCIES ======================================================
# ===================================================================================

def create_frequency_individuals(dict_airports):
    """ Creates Frequency individuals in the ontology

    Parameters
    ----------
    dict_airports : dict
        Dictionary conataining Airport individuals
    """
    frequency_data = FrequencyLoader().get_frequency_data()
    pbar = tqdm(total=len(frequency_data), desc="Frequencies")
    for i, row in frequency_data.iterrows():
        ## Individual
        this_airport = row['icao']
        new_frequency = onto.Frequency(f"Frequency_{i}")
        new_frequency.FrequencyDescription.append(row['description'])
        new_frequency.FrequencyMHz.append(row['frequency_mhz'])
        new_frequency.FrequencyType.append(row['type'])
        ## ObjectProperty
        new_frequency.BelongsToAirport.append(dict_airports[this_airport])
        dict_airports[this_airport].HasFrequency.append(new_frequency)

        pbar.update(1)
    pbar.close()


# ===================================================================================
# ================ NAVAIDS ==========================================================
# ===================================================================================

def create_navaid_individuals():
    """ Creates Navaid individuals in the ontology
    """
    navaid_data = NavaidLoader().get_navaid_data()
    pbar = tqdm(total=len(navaid_data), desc="Navaids")
    for i, row in navaid_data.iterrows():
        new_navaid = onto.Navaid(f"Navaid_{i}")
        new_navaid.NavaidAltitude.append(row['elevation_ft'])
        new_navaid.NavaidFrequencyKHz.append(row['frequency_khz'])
        new_navaid.NavaidGPSLatitude.append(row['latitude_deg'])
        new_navaid.NavaidGPSLongitude.append(row['longitude_deg'])
        new_navaid.NavaidIdentifier.append(row['ident'])
        new_navaid.NavaidName.append(row['navaid_name'])
        new_navaid.NavaidPower.append(row['power'])
        new_navaid.NavaidType.append(row['type'])
        new_navaid.NavaidUsage.append(row['usageType'])

        pbar.update(1)
    pbar.close()


# ===================================================================================
# ================ WAYPOINTS ========================================================
# ===================================================================================

def create_waypoint_individuals():
    PATH = "../data/waypoints.csv"
    waypoint_data = WaypointLoader(PATH=PATH).get_waypoint_data()
    pbar = tqdm(total=len(waypoint_data), desc="Waypoints")
    for i, row in waypoint_data.iterrows():
        new_waypoint = onto.Waypoint(f"Waypoint_{i}")
        new_waypoint.WaypointCountryCode.append(row['country_code'])
        new_waypoint.WaypointGPSLatitude.append(row['latitude'])
        new_waypoint.WaypointGPSLongitude.append(row['longitude'])
        new_waypoint.WaypointIdentifier.append(row['ident'])
        new_waypoint.WaypointPlannedAltitude.append(-1)

        pbar.update(1)
    pbar.close()





def main():
    dict_airports = create_airport_individuals()
    create_runway_individuals(dict_airports)
    create_frequency_individuals(dict_airports)
    create_navaid_individuals()
    create_waypoint_individuals()
    onto.save(file=filename_onto_individuals, format="rdfxml")
    print("Done !")
    return

if __name__ == '__main__':
    main()