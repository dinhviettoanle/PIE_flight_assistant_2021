var dict_airports = {}

class Airport {
    constructor(airport) {
        this.name = airport.name;
        this.iata = airport.iata;
        this.icao = airport.icao;
        this.latitude = airport.latitude;
        this.longitude = airport.longitude;
        this.altitude = airport.altitude;
        this.country = airport.country;
        this.desc = airport.desc;


        var airport_icon = L.icon({
            iconUrl: airport_url,
            iconSize:     [32, 32],
            iconAnchor:   [16, 32],
            popupAnchor:  [0, -40]
        });

        this.marker = new L.marker([this.latitude, this.longitude], {icon : airport_icon});
        this.marker.bindPopup(`${this.name} - ${this.icao} <br> 
                                Altitude : ${this.altitude}`);
    }

    draw_map(map) {
        this.marker.addTo(map);
    }

    free_map(map) {
        map.removeLayer(this.marker);
    }

    is_outside_map(minLong, maxLong, minLat, maxLat, center) {
        if (USE_RADAR) {
            return calcCrow(center[0], center[1], this.latitude, this.longitude) > radius;
        }
        else {
            const margin = 0;
            return (Math.abs(this.longitude - minLong) < margin) || 
                (Math.abs(this.longitude - maxLong) < margin) ||
                (Math.abs(this.latitude - minLat) < margin) ||
                (Math.abs(this.latitude - maxLat) < margin);
        }
    }
}

function check_visible_airports(icao_list) {
    for (const [icao, airport] of Object.entries(dict_airports)) {
        if (airport.is_outside_map(minLong, maxLong, minLat, maxLat, center) || !icao_list.includes(icao)) {
            airport.free_map(mymap);
            delete dict_airports[icao];
        }
    }
}

function update_airports(list_airports) {
    var icao_list = list_airports.map(({icao}) => icao);
    check_visible_airports(icao_list);

    list_airports.forEach(a => {
        if (!(a.icao in dict_airports)) {
            let airport = new Airport(a);
            if (airport.is_outside_map(minLong, maxLong, minLat, maxLat, center)) {
                delete dict_airports[a.icao];
            }
            else {
                dict_airports[a.icao] = airport;
                airport.draw_map(mymap);
            }
        }
    });
}