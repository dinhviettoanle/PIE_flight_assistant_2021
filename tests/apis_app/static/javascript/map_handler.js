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



class Location {

    constructor(entity) {
        this.longitude = entity.longitude;
        this.latitude = entity.latitude;
        this.marker = null;
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



init_map();

if (USE_RADAR) { init_radar(); }
else { init_box(); }