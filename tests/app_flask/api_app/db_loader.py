import requests
import pandas as pd
import io
from tqdm.autonotebook import tqdm
import logging as lg

from .models import db, Airport, Runway

class AirportLoader:

    def __init__(self, source='fr24'):
        if source == 'fr24':
            self.data = self.download_fr24()
        elif source == 'ourairports':
            self.data = self.download_ourairports()

    def get_airport_data(self):
        return self.data
    
    def download_fr24(self):
        s = requests.session()
        c = s.get(
            'https://www.flightradar24.com/_json/airports.php', 
            headers={"user-agent": "Mozilla/5.0"}
            )
        df_airportsfr24 = (pd.DataFrame.from_records(c.json()['rows'])
                        .assign(name=lambda df: df.name.str.strip())
                        .rename(columns={
                            'lat' : 'latitude',
                            'lon' : 'longitude',
                            'alt' : 'altitude',
                        })
                    )
        n_airports = len(df_airportsfr24)
        df_airportsfr24['desc'] = [None] * n_airports
        df_airportsfr24['municipality'] = [None] * n_airports
            
        # Erreurs dans la base de donnees
        df_airportsfr24.at[df_airportsfr24.loc[df_airportsfr24['name'] == "Baicheng Chang'an Airport"]\
            .index[0], 'icao'] = "ZYBA"
        
        return df_airportsfr24

    
    def download_ourairports(self):
        s = requests.session()

        # Load countries
        f = s.get("https://ourairports.com/data/countries.csv")
        buffer = io.BytesIO(f.content)
        buffer.seek(0)
        df_countries = pd.read_csv(buffer)
        df_countries = df_countries.rename(columns={'code' : 'iso_country', 'name' : 'country'})

        # Load airports
        f = s.get("https://ourairports.com/data/airports.csv", stream=True)
        total = int(f.headers["Content-Length"])
        buffer = io.BytesIO()
        for chunk in tqdm(
            f.iter_content(1024),
            total=total // 1024 + 1 if total % 1024 > 0 else 0,
            desc="Requesting airport@ourairports",
        ):
            buffer.write(chunk)

        buffer.seek(0)
        df_airports = pd.read_csv(buffer)
        df_airports = (df_airports.rename(columns={
                            'latitude_deg': 'latitude',
                            'longitude_deg': 'longitude',
                            'elevation_ft': 'altitude',
                            'iata_code': 'iata',
                            'ident': 'icao',
                            'type' : 'desc',
                    })
                    .merge(df_countries[['iso_country', 'country']])
                    )
        df_airports = df_airports[['name', 'iata', 'icao', 'latitude', 'longitude', 'country', 'altitude', 'desc', 'municipality']]

        return df_airports



class RunwayLoader:

    def __init__(self):
        self.data = self.download_ourairports()

    def get_runway_data(self):
        return self.data
    
    def download_ourairports(self):
        
        df_airportsfr24 = AirportLoader().download_fr24().drop(columns=['desc', 'municipality'])
        s = requests.session()

        f = s.get("https://ourairports.com/data/runways.csv", stream=True)
        total = int(f.headers["Content-Length"])
        buffer = io.BytesIO()
        for chunk in tqdm(
            f.iter_content(1024),
            total=total // 1024 + 1 if total % 1024 > 0 else 0,
            desc="Requesting runway@ourairports",
        ):
            buffer.write(chunk)

        buffer.seek(0)
        df_runways = pd.read_csv(buffer)

        df_all = (df_airportsfr24
            .merge(df_runways, left_on='icao', right_on='airport_ident', how='left')
            .drop(columns=['id', 'airport_ident', 'airport_ref', 'le_displaced_threshold_ft', 'he_displaced_threshold_ft'])
            .dropna(axis=0)
            .reset_index()
            )

        return df_all



def import_airports(db):
    airport_data = AirportLoader().get_airport_data()
    pbar = tqdm(total = len(airport_data), desc="Creating entries")
    list_airports = []
    for i, airport in airport_data.iterrows():
        new_airport = Airport(
            name = airport['name'],
            iata = airport['iata'],
            icao = airport['icao'],
            latitude = airport['latitude'],
            longitude = airport['longitude'],
            altitude = airport['altitude'],
            country = airport['country'],
            desc = airport['desc'],
            municipality = airport['municipality'],
        )
        db.session.add(new_airport)
        db.session.commit()
        pbar.update(1)
    pbar.close()

    print("Done !")


def import_runways(db):
    runway_data = RunwayLoader().get_runway_data()
    pbar = tqdm(total = len(runway_data), desc="Creating entries")
    list_runways = []
    for i, runway in runway_data.iterrows():
        # this_airport = Airport.query.filter(Airport.icao == runway['icao']).first()
        # if this_airport == None:
        #     print(runway['icao'])
        #     print(runway)
        #     raise Exception("Error")
        new_runway = Runway(
            id = i,
            airport = runway['icao'],
            length = runway['length_ft'],
            width = runway['width_ft'],
            surface = runway['surface'],
            le_ident = runway['le_ident'],
            le_heading = runway['le_heading_degT'],
            le_latitude = runway['le_latitude_deg'],
            le_longitude = runway['le_longitude_deg'],
            le_altitude = runway['le_elevation_ft'],
            he_ident = runway['he_ident'],
            he_heading = runway['he_heading_degT'],
            he_latitude = runway['he_latitude_deg'],
            he_longitude = runway['he_longitude_deg'],
            he_altitude = runway['he_elevation_ft'],
        )
        db.session.add(new_runway)
        db.session.commit()
        pbar.update(1)
    pbar.close()

    print("Done !")




def init_db():
    db.drop_all()
    db.create_all()
    import_airports(db)
    import_runways(db)
    lg.warning('Database initialized!')

