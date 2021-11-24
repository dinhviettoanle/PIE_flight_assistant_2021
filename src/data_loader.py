"""
Data downloaders used to import individuals in the ontology
"""
import requests
import pandas as pd
import io
from tqdm.autonotebook import tqdm
import logging as lg

import multiprocessing
from joblib import Parallel, delayed
from bs4 import BeautifulSoup

class AirportLoader:
    """
    Airport data downloader from FlightRadar24 or ourairports
    """

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


# =========================================================================================


class RunwayLoader:
    """
    Runway data downloader from ourairports
    """
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
            .drop(columns=['id', 'airport_ident', 'airport_ref'])
            .fillna({'le_displaced_threshold_ft' : 0,'he_displaced_threshold_ft' : 0})
            .dropna(axis=0)
            .reset_index()
            )

        return df_all


# =========================================================================================


class NavaidLoader:
    """
    Navaid data downloader from ourairports
    """
    def __init__(self):
        self.data = self.download_navaids()

    def get_navaid_data(self):
        return self.data
    
    def download_navaids(self):
        df_airportsfr24 = AirportLoader().download_fr24().drop(columns=['desc', 'municipality'])
        s = requests.session()

        # Load countries
        f = s.get("https://ourairports.com/data/countries.csv")
        buffer = io.BytesIO(f.content)
        buffer.seek(0)
        df_countries = pd.read_csv(buffer)
        df_countries = df_countries.rename(columns={'code' : 'iso_country', 'name' : 'country'})

        # Load navaids
        f = s.get("https://ourairports.com/data/navaids.csv", stream=True)
        total = int(f.headers["Content-Length"])
        buffer = io.BytesIO()
        for chunk in tqdm(
            f.iter_content(1024),
            total=total // 1024 + 1 if total % 1024 > 0 else 0,
            desc="Requesting navaid@ourairports",
        ):
            buffer.write(chunk)

        buffer.seek(0)
        df_navaids = pd.read_csv(buffer)

        df_all = (df_navaids
            .merge(df_countries[['iso_country', 'country']])
            .merge(df_airportsfr24[['name', 'icao']], left_on='associated_airport', right_on='icao', how='left')
            .drop(columns=['id', 'filename', 'iso_country', 'associated_airport',
                            'dme_frequency_khz', 'dme_channel', 'dme_latitude_deg', 'dme_longitude_deg', 'dme_elevation_ft',
                            'slaved_variation_deg', 'magnetic_variation_deg'])
            .rename(columns={'name_x' : 'navaid_name', 'name_y' : 'airport_name', 'icao' : 'airport_icao'})
            .reset_index()
                )
        df_all['ident'].fillna('NA', inplace=True)
        df_all['power'].fillna('NA', inplace=True)
        df_all['usageType'].fillna('NA', inplace=True)
        df_all['elevation_ft'].fillna(0, inplace=True)
        df_all = df_all.where(pd.notnull(df_all), None)


        return df_all


# =========================================================================================


class FrequencyLoader:
    """
    Frequency data downloader from ourairports
    """
    def __init__(self):
        self.data = self.download_frequencies()

    def get_frequency_data(self):
        return self.data
    
    def download_frequencies(self):
        df_airportsfr24 = AirportLoader().download_fr24().drop(columns=['desc', 'municipality'])        
        s = requests.session()

        f = s.get("https://ourairports.com/data/airport-frequencies.csv", stream=True)
        total = int(f.headers["Content-Length"])
        buffer = io.BytesIO()
        for chunk in tqdm(
            f.iter_content(1024),
            total=total // 1024 + 1 if total % 1024 > 0 else 0,
            desc="Requesting frequency@ourairports",
        ):
            buffer.write(chunk)

        buffer.seek(0)
        df_frequencies = pd.read_csv(buffer)


        df_all = (df_airportsfr24
            .merge(df_frequencies, left_on='icao', right_on='airport_ident', how='left')
            .drop(columns=['id', 'airport_ident', 'airport_ref'])
            .dropna(axis=0)
            .reset_index()
         )

        return df_all

# =========================================================================================

class WaypointLoader:
    
    def __init__(self):
        try:
            self.data = pd.read_csv('../data/waypoints.csv')
            print("Loading ../data/waypoints.csv")
        except FileNotFoundError:
            print("../data/waypoints.csv not found")
            self.data = pd.DataFrame({'ident': [], 'latitude': [], 'longitude': []})
    

    def get_waypoint_data(self):
        return self.data


    def add_waypoints(self, min_i, max_i):
        """Adds waypoints to an already (full or not) self.data

        Parameters
        ----------
        min_i : int
            Minimum index of the plan on the website
        max_i : int
            Maximum index of the plan on the website

        Returns
        -------
        pd.DataFrame
            DataFrame containing already existing waypoints and new parsed waypoints
        """
        num_cores = multiprocessing.cpu_count()

        url_list = tqdm([f"https://flightplandatabase.com/plan/{i}" for i in range(min_i, max_i)])

        # Run web scraping in parallel
        processed_list = Parallel(n_jobs=num_cores)(delayed(self.parse_page)(url) for url in url_list)

        # Remove None and []
        list_list_waypoints = [item for item in processed_list if item not in (None, [])]
        # Flatten the list of list
        list_waypoints_flatten = [item for sublist in list_list_waypoints for item in sublist]
        # Remove duplicate dicts
        list_waypoints = [dict(t) for t in {tuple(d.items()) for d in list_waypoints_flatten}]
        df_waypoints = pd.DataFrame(list_waypoints)

        print(f"{len(df_waypoints)} waypoints found between {min_i} and {max_i}")

        self.data = pd.concat([self.data, df_waypoints]).drop_duplicates().reset_index(drop=True)
        print(f"Current number of waypoints: {len(self.data)}")

        return self.data



    def export_waypoints(self):
        """ Export self.data to a csv file
        """
        print("Export to ../data/waypoints.csv")
        self.data.to_csv("../data/waypoints.csv", index=False)
    


    @staticmethod
    def parse_page(url, list_waypoints=None):
        page = requests.get(url)
        if page.status_code != 200: 
            return

        soup = BeautifulSoup(page.content, "html.parser")
        plan_route_table = soup.find("table", {"class": "plan-route-table"})

        list_new_waypoints = []
        for tr in plan_route_table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) == 0: continue
            _, ident, type_wpt, via, alt, position, dist, name = [item.text for item in tds]
            if type_wpt == "FIX":
                lat, lng = position.replace(' ', '').split('/')
                new_waypoint = {
                    'ident': ident,
                    'latitude': float(lat),
                    'longitude': float(lng)
                }
                # Parallel
                list_new_waypoints.append(new_waypoint)
                
                # Sequential
                if list_waypoints is not None:
                    if new_waypoint not in list_waypoints:
                        list_waypoints.append(new_waypoint)
                        list_new_waypoints.append(new_waypoint)
                    else:
                        print(new_waypoint['ident'], end=' ', flush=True)
        # Parallel
        return list_new_waypoints





if __name__ == '__main__':
    # min_i, max_i = 499, 800 # 4_778_086
    min_i, max_i = 250000, 300000 # 4_778_086
    wpl = WaypointLoader()
    wpl.add_waypoints(min_i, max_i)
    wpl.export_waypoints()