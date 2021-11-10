import owlready2 as owl
import pandas as pd
from tqdm.autonotebook import tqdm
from api_app.db_loader import AirportLoader, RunwayLoader, NavaidLoader, FrequencyLoader

filename_onto = "../ontology/final-archi.owl"
filename_onto_individuals = "../ontology/final-archi-individuals.owl"
onto = owl.get_ontology(filename_onto).load()

# ===================================================================================
# ================ AIRPORTS =========================================================
# ===================================================================================

def create_airport(row):
    return

def create_airport_entities():
    airport_data = AirportLoader().get_airport_data()
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
        pbar.update(1)
    pbar.close()




def main():
    create_airport_entities()
    onto.save(file=filename_onto_individuals, format="rdfxml")
    return

if __name__ == '__main__':
    main()