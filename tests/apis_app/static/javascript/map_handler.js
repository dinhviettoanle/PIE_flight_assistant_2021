var box = [42.59972466458162, 44.59972466458162, -0.5507202427834272, 3.4492797572165728];

var minLat = box[0];
var maxLat = box[1];
var minLong = box[2];
var maxLong = box[3];

var mymap = null;
var bounds = null;
var rect = null;

var dict_airplanes = {};

class Airplane {
    constructor(flight) {
        this.icao24 = flight.icao24;
        this.callsign = flight.callsign;
        this.latitude = flight.latitude;
        this.longitude = flight.longitude;
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

    draw_map(map) {
        this.marker.addTo(map);
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

    free_map(map) {
        map.removeLayer(this.marker);
    }

    is_outside_map(minLong, maxLong, minLat, maxLat) {
        const margin = 0.1;
        return (Math.abs(this.longitude - minLong) < margin) || 
               (Math.abs(this.longitude - maxLong) < margin) ||
               (Math.abs(this.latitude - minLat) < margin) ||
               (Math.abs(this.latitude - maxLat) < margin)
    }
}

function init_map() {
    mymap = L.map('mapid').setView([maxLat, minLong], 13);
    // Set tiles
    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
        id: 'mapbox/outdoors-v11',
        tileSize: 512,
        zoomOffset: -1,
        opacity: 0.5,
        accessToken: 'pk.eyJ1IjoibGVkdnQiLCJhIjoiY2t1amlzMm5iMTM4bDMybXlnMXlzZWVwbyJ9.ecGiBs-_E5oKq7ccKprCYg'
    }).addTo(mymap);

    // Set interaction
    mymap.on('click', function(e) {
        console.log("Lat, Lon : " + e.latlng.lat + ", " + e.latlng.lng);
        socket.emit('change_focus', {
            latitude : e.latlng.lat,
            longitude : e.latlng.lng,
        });

        maxLong = e.latlng.lng + 2;
        minLong = e.latlng.lng - 2;
        minLat = e.latlng.lat - 1;
        maxLat = e.latlng.lat + 1;

        mymap.setView([maxLat, minLong], 50);
        update_bounds();
    });

}



function init_bounds() {
    bounds = [[minLat, minLong], [maxLat, maxLong]];
    rect = L.rectangle(bounds, {color: "#ff7800", weight: 1});
    rect.addTo(mymap);
    mymap.fitBounds(bounds);
}


function update_bounds() {
    mymap.removeLayer(rect)
    bounds = [[minLat, minLong], [maxLat, maxLong]];
    rect = L.rectangle(bounds, {color: "#ff7800", weight: 1});
    rect.addTo(mymap);
    mymap.fitBounds(bounds);
}


function check_visible_planes(icao_list) {
    for (const [icao24, airplane] of Object.entries(dict_airplanes)) {
        if (airplane.is_outside_map(minLong, maxLong, minLat, maxLat) || !icao_list.includes(icao24)) {
            airplane.free_map(mymap);
            delete dict_airplanes[icao24];
        }
    }
}


function update_map(list_flights) {
    var icao_list = list_flights.map(({icao24}) => icao24);
    check_visible_planes(icao_list);
    list_flights.forEach(f => {
        if (f.icao24 in dict_airplanes) {
            dict_airplanes[f.icao24].update_position(f);
        }
        else {
            let airplane = new Airplane(f);
            if (airplane.is_outside_map(minLong, maxLong, minLat, maxLat)) {
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


init_map();
init_bounds();