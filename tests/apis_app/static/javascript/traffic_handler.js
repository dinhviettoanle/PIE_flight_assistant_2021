var dict_airplanes = {};

class Airplane extends Location {
    constructor(flight) {
        super(flight);

        this.icao24 = flight.icao24;
        this.callsign = flight.callsign;
        this.heading = flight.heading;
        this.altitude = flight.altitude;

        var img = new Image();
        img.src = arrow_url;
        var options = {
            label: this.icao24,
            labelFlag: true,
            labelColor: 'black',
            img: img
        };

        this.marker = L.angleMarker([this.latitude, this.longitude], options);
        this.marker.setHeading(this.heading / 180 * Math.PI);
        this.marker.bindPopup(`${this.icao24} - ${this.callsign} <br> \
                                (${this.latitude}, ${this.longitude}) <br>  \
                                Heading : ${this.heading} <br>\
                                Altitude : ${this.altitude}`);
    }

    update_position(flight) {
        this.marker.setLatLng([flight.latitude, flight.longitude]).update();
        this.latitude = flight.latitude;
        this.longitude = flight.longitude;
        this.heading = flight.heading;
        this.altitude = flight.altitude;

        this.marker.setHeading(flight.heading / 180 * Math.PI);
        this.marker.bindPopup(`${this.icao24} - ${this.callsign} <br> \
            (${this.latitude}, ${this.longitude}) <br>  \
            Heading : ${this.heading} <br>\
            Altitude : ${this.altitude}`);
    }
}



function check_visible_planes(icao_list) {
    for (const [icao24, airplane] of Object.entries(dict_airplanes)) {
        if (airplane.is_outside_map(minLong, maxLong, minLat, maxLat, center) || !icao_list.includes(icao24)) {
            airplane.free_map(mymap);
            delete dict_airplanes[icao24];
        }
    }
}


function update_traffic(list_flights) {
    var icao_list = list_flights.map(({icao24}) => icao24);
    check_visible_planes(icao_list);
    list_flights.forEach(f => {
        if (f.icao24 in dict_airplanes) {
            dict_airplanes[f.icao24].update_position(f);
        }
        else {
            let airplane = new Airplane(f);
            if (airplane.is_outside_map(minLong, maxLong, minLat, maxLat, center)) {
                airplane.free_map(mymap);
                delete dict_airplanes[f.icao24];
            }
            else {
                dict_airplanes[f.icao24] = airplane;
                airplane.draw_map(mymap);
            }
        }
    });
}

