const USE_RADAR = true;

var box = [42.59972466458162, 44.59972466458162, -0.5507202427834272, 3.4492797572165728];
var minLat = box[0];
var maxLat = box[1];
var minLong = box[2];
var maxLong = box[3];

var center = [43.59972466458162, 1.4492797572165728];
var radius = 100;

var bounds = null;
var rect = null;
var circle = null;

var dict_airplanes = {};

function calcCrow(lat1, lon1, lat2, lon2) {
      var R = 6371; // km
      var dLat = toRad(lat2-lat1);
      var dLon = toRad(lon2-lon1);
      var lat1 = toRad(lat1);
      var lat2 = toRad(lat2);

      var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.sin(dLon/2) * Math.sin(dLon/2) * Math.cos(lat1) * Math.cos(lat2); 
      var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
      var d = R * c;
      return d;
    }

// Converts numeric degrees to radians
function toRad(Value) {
    return Value * Math.PI / 180;
}

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

        // With circle
        center = [ e.latlng.lat, e.latlng.lng];
        
        if (USE_RADAR) { update_radar(); }
        else { update_box(); }

    });

}



function init_box() {
    bounds = [[minLat, minLong], [maxLat, maxLong]];
    rect = L.rectangle(bounds, {color: "#ff7800", weight: 1});
    rect.addTo(mymap);
    mymap.fitBounds(bounds);
}

function init_radar() {
    circle = L.circle(center, {radius: radius * 1000, color: "#ff7800", weight : 1});
    circle.addTo(mymap);
    mymap.fitBounds(circle.getBounds());
}


function update_box() {
    mymap.removeLayer(rect);
    bounds = [[minLat, minLong], [maxLat, maxLong]];
    rect = L.rectangle(bounds, {color: "#ff7800", weight: 1});
    rect.addTo(mymap);
    mymap.fitBounds(bounds);
}


function update_radar() {
    mymap.removeLayer(circle);
    circle = L.circle(center, {radius: radius * 1000, color: "#ff7800", weight : 1});
    circle.addTo(mymap);
    mymap.fitBounds(circle.getBounds());
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


init_map();

if (USE_RADAR) { init_radar(); }
else { init_box(); }