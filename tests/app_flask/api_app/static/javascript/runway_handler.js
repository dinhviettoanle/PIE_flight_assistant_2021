var dict_runways = {};


class Runway extends Location{
    constructor(runway) {
        super(runway);

        this.airport = runway.airport;
        this.length = runway.length;
        this.width = runway.width;
        this.surface = runway.surface;
        this.le_ident = runway.le_ident;
        this.le_heading = runway.le_heading;
        this.le_latitude = runway.le_latitude;
        this.le_longitude = runway.le_longitude;
        this.he_ident = runway.he_ident;
        this.he_heading = runway.he_heading;
        this.he_latitude = runway.he_latitude;
        this.he_longitude = runway.he_longitude;
        
        var latlngs = [
            [this.le_latitude, this.le_longitude],
            [this.he_latitude, this.he_longitude],
        ];
        
        this.line = new L.polyline(latlngs, 
            {color: 'red',
            lineCap : 'square',
            weight : 0});
        
        this.line.bindTooltip(`${this.le_ident}/${this.he_ident} - ${this.airport} <br>
            Dim : ${this.length} x ${this.width} <br>
            Surf : ${this.surface}`, 
            {className : "runwayToolTip", sticky : true});
        

    }

    draw_map(map) {
        this.line.addTo(map);
    }

    free_map(map) {
        map.removeLayer(this.line);
    }
    
}

function set_middle_latlgn(runway_dict) {
    runway_dict['latitude'] = (runway_dict.le_latitude + runway_dict.he_latitude)/2;
    runway_dict['longitude'] = (runway_dict.le_longitude + runway_dict.he_longitude)/2;
    return runway_dict;
}

function check_visible_runway(key_list) {
    for (const [key, runway] of Object.entries(dict_runways)) {
        if (runway.is_outside_map(minLong, maxLong, minLat, maxLat, center) || !key_list.includes(key)) {
            runway.free_map(mymap);
            delete dict_runways[key];
        }
    }
}


function update_runways(list_runways) {
    var key_list = list_runways.map(({airport, le_ident}) => airport + "-" + le_ident);
    check_visible_runway(key_list);
    
    list_runways.forEach(r => {
        var key = r.airport + "-" + r.le_ident;
        if (!(key in dict_runways)) {
            r = set_middle_latlgn(r);
            let runway = new Runway(r);
            if (runway.is_outside_map(minLong, maxLong, minLat, maxLat, center)) {
                delete dict_runways[key];
            }
            else {
                dict_runways[key] = runway;
                runway.draw_map(mymap);
            }
        }
    });
}

function setWeightsPolylines(weight) {
    for (const [key, runway] of Object.entries(dict_runways)) {
        runway.line.setStyle({weight : weight});
    }
}

mymap.on('zoomend', function () {
    currentZoom = mymap.getZoom();
    if (currentZoom < 10) {
        setWeightsPolylines(0);
    }
    else if (10 <= currentZoom && currentZoom <= 16) {
        setWeightsPolylines(3*currentZoom - 29);
    }
    else {
        setWeightsPolylines(20);
    }
});