"""
Data downloaders used to import individuals in the ontology
"""
import requests
import pandas as pd
import io
from tqdm.autonotebook import tqdm
import logging as lg

from bs4 import BeautifulSoup
import re

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
    
    def __init__(self, PATH=False):
        if not(PATH):
            self.data = self.download_waypoints()
            print(len(self.data), "waypoints parsed")
        else:
            self.data = pd.read_csv(PATH, na_filter=False)
    

    def get_waypoint_data(self):
        return self.data

    def export_waypoint_data(self):
        self.data.sort_values(by=['country_code', 'ident'], inplace=True)
        self.data.to_csv("../data/waypoints.csv", index=False)

    def download_waypoints(self):
        df_waypoints = pd.DataFrame({
            'ident' : [],
            'latitude' : [],
            'longitude' : [],
            'country_code' : [],
            'country_name' : []
        })

        df_down_all = self.download_opennav()
        df_down_us = self.download_faa()
        df_waypoints = pd.concat([df_waypoints, df_down_all, df_down_us])
        return df_waypoints


    def download_opennav(self):
        df_countries = pd.read_csv("../data/countries.csv")[['code', 'name']]

        list_waypoints = []

        pbar = tqdm(total=len(df_countries)-1, desc="Requesting waypoint@opennav")
        for i, row in df_countries.iterrows():
            if row['name'] == 'Namibia': row['code'] = "NA"
            if row['code'] == "US": continue
            self.get_waypoints_country(row, list_waypoints)
            pbar.update(1)
        pbar.close()
        df_down = pd.DataFrame(list_waypoints)

        return df_down
    

    def download_faa(self):
        list_us_wp = []
        tot_us_waypoints = 65875
        pbar = tqdm(total=tot_us_waypoints, desc="Requesting waypoint@faa")
        for start_id in range(0, tot_us_waypoints, 1000):
            self.get_us_part_waypoints(start_id, list_us_wp)
            pbar.update(1000)
        pbar.close()
        df_down = pd.DataFrame(list_us_wp)

        return df_down


    @staticmethod
    def get_waypoints_country(row, list_waypoints, country_code=None, country=None):
        if country_code is None and country is None:
            country_code, country = row['code'], row['name']
        page = requests.get(f"https://opennav.com/waypoint/{country_code}")
        if len(page.history) > 0: 
            return

        soup = BeautifulSoup(page.content, "html.parser")
        for i, tr in enumerate(soup.find_all("tr")[2:]):
            content_tr = tr.find_all("td", class_=lambda x: x != 'layout_col50')
            waypoint_ident = content_tr[0].find("a").text
            
            if re.match(r"""\d+\s\d+.\d+[NSEW]""", content_tr[1].text):
                # Case Brazil
                waypoint_latitude = content_tr[1].text
                waypoint_longitude = content_tr[2].text
            else:
                # Other cases
                waypoint_latitude = content_tr[1].text.replace(' ', '')
                waypoint_longitude = content_tr[2].text.replace(' ', '')

            try:
                list_waypoints.append({
                    'ident' : waypoint_ident,
                    'latitude' : convert_coordinate_str(waypoint_latitude),
                    'longitude' : convert_coordinate_str(waypoint_longitude),
                    'country_code' : country_code,
                    'country_name' : country,
                })
            except Exception as e:
                print(e, country_code, waypoint_ident, waypoint_latitude, waypoint_longitude, flush=True)





    @staticmethod
    def get_us_part_waypoints(start_id, list_us_wp):
        url = f"https://nfdc.faa.gov/nfdcApps/controllers/PublicDataController/getLidData?dataType=LIDFIXESWAYPOINTS&start={start_id}&length=1000&sortcolumn=fix_identifier&sortdir=asc"
        r = requests.get(url)
        json_waypoints = r.json()['data']
        for i, wp_data in enumerate(json_waypoints):
            latitude, longitude = get_coordinates_from_desc(wp_data['description'])
            list_us_wp.append({
                'ident' : wp_data['fix_identifier'],
                'latitude' : latitude,
                'longitude' : longitude,
                'country_code' : "US",
                'country_name' : "United States",
            })



def get_coordinates_from_desc(desc):
    # For US Waypoints
    direction = {'N':1, 'S':-1, 'E': 1, 'W':-1}
    lng_str = re.match(r".*\s(\d+-\d+-\d+\.\d+(W|E))", desc).group(1)
    lat_str = re.match(r".*(\d{2,2}-\d+-\d+\.\d+(N|S)).*", desc).group(1)
    lat = convert_coordinate_str(lat_str)
    lng = convert_coordinate_str(lng_str)
    return lat, lng




def convert_coordinate_str(old):
    direction = {'N':1, 'S':-1, 'E': 1, 'W':-1}
    
    if re.match(r"""\s*\d+(:*)°\d+'\d+.\d*"\s*[NSEW]""", old):
        new = old.replace(u'°',' ').replace('\'',' ').replace('"',' ').replace(':', ' ')
        new = new.split()
        new_dir = new.pop()
        new.extend([0,0,0])

    elif re.match(r"""\d+[NSEW]""", old):
        new_dir = old[-1]
        new = old[:-1]
        new = str(int(new))
        new = [new[i:i+2] for i in range(0, len(new), 2)]

    elif re.match(r"""\d+-\d+-\d+.\d+[NSEW]""", old):
        new_dir = old[-1]
        new = old[:-1].split("-")
    
    elif re.match(r"""\d+\s\d+.\d+[NSEW]""", old):
        new_dir = old[-1]
        new = old[:-1].replace('.', ' ')
        new = new.split()
    
    elif re.match(r"""\d+°-\d'\d-.\d+(.\d+)*"[NSEW]""", old):
        new_dir = old[-1]
        new = old[:-1].replace("'",'').replace('°-', ' ').replace('-.', ' ').replace('"', '')
        new = new.split()
    
    elif re.match(r"""\d+°\d+'\d+..\d+"[NSEW]""", old):
        new_dir = old[-1]
        new = old[:-1].replace('°', ' ').replace("'", '').replace('..',' ').replace('"', '')
        new = new.split()
    else:
        assert False
    
    return (float(new[0])+float(new[1])/60.0+float(new[2])/3600.0) * direction[new_dir]




def test_convert_latlng():
    lat, lon = """45°20'52.00" N, 002°29'59.00"E""".split(',')
    convert_coordinate_str(lat), convert_coordinate_str(lon)

    lat, lon = "47-22-59.27N", "015-00-23.87E"
    convert_coordinate_str(lat), convert_coordinate_str(lon)

    lat, lon = "253226N", "0545455E"
    convert_coordinate_str(lat), convert_coordinate_str(lon)

    lat, lon = "13 51.48S", "041 24.44W"
    convert_coordinate_str(lat), convert_coordinate_str(lon)

    lat, lon = "22 18.55S", "042 25.51W"
    convert_coordinate_str(lat), convert_coordinate_str(lon)

    lat, lon = """40°50'17.52"N""", """28:°47'17.13"E"""
    convert_coordinate_str(lat), convert_coordinate_str(lon)

    lat, lon = """25°-4'8-.22.91"N""", """121°-4'9-.02.84"E"""
    # ==> 25°48'22.91" N, 121° 49'02.84" E
    convert_coordinate_str(lat), convert_coordinate_str(lon)

    lat, lon = """24°-4'3-.48"N""", """120°-3'0-.30"E"""
    convert_coordinate_str(lat), convert_coordinate_str(lon)

    lat, lon = """25°2'1..9"N""", """121°2'6..3"E"""
    # ==> 25°21'9"N, 121°26'3" E
    convert_coordinate_str(lat), convert_coordinate_str(lon)



if __name__ == '__main__':
    wpl = WaypointLoader()


