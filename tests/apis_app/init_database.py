import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','flight_assistant_app.settings')

import django
django.setup()

# Rappel : 
# Pour afficher une table dans le shell :
# from app.models import Airport
# Airport.objects.all()
#
# Pour supprimer :
# Airport.objects.all().delete()


import requests
import pandas as pd
import io
from tqdm.autonotebook import tqdm

from app.models import Airport


class AirportLoader:

    def __init__(self, source='ourairports'):
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
            desc="Requesting @ourairports",
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



def import_data(airport_data):
    return

def main():
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
            country = airport['country'],
            desc = airport['desc'],
            municipality = airport['municipality'],
        )
        list_airports.append(new_airport)
        pbar.update(1)
    pbar.close()

    Airport.objects.bulk_create(list_airports)

    print("Done !")


if __name__ == '__main__':
    main()