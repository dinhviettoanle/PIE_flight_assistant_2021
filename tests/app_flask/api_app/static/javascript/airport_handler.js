var dict_airports = {}

class Airport extends Location{
    constructor(airport) {
        super(airport);
        
        this.name = airport.name;
        this.iata = airport.iata;
        this.icao = airport.icao;
        this.altitude = airport.altitude;
        this.country = airport.country;
        this.desc = airport.desc;
        this.list_frequencies = airport.list_frequencies;


        var airport_icon = L.icon({
            iconUrl: airport_url,
            iconSize:     [32, 32],
            iconAnchor:   [16, 32],
            popupAnchor:  [0, -40]
        });

        var list_frequencies_str = '';
        this.list_frequencies.forEach(f => {
            list_frequencies_str = list_frequencies_str + `<b>${f.desc}</b> : ${f.frq_mhz} MHz<br>`;
        });

        this.marker = new L.marker([this.latitude, this.longitude], {icon : airport_icon});
        this.marker.bindTooltip(`${this.name} - ${this.icao} <br> 
                                Altitude : ${this.altitude} <br>
                                ----- <br>
                                ${list_frequencies_str}`, 
                                {className: "airportToolTip"});
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