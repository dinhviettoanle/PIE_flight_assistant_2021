var dict_runways = {};


class Runway extends Location{
    constructor(runway) {
        super(runway);

        this.airport = runway.airport;
        this.length = runway.length;
        this.width = runway.width;
        this.surface = runway.surface;
        this.couple = runway.couple;
        this.beg_latitude = runway.beg_latitude;
        this.beg_longitude = runway.beg_longitude;
        this.end_latitude = runway.end_latitude;
        this.end_longitude = runway.end_longitude;
        
        var latlngs = [
            [this.beg_latitude, this.beg_longitude],
            [this.end_latitude, this.end_longitude],
        ];
        
        this.line = new L.polyline(latlngs, 
            {color: 'black',
            lineCap : 'square',
            weight : 0,
            opacity : 0.3});
        
        this.line.bindTooltip(`${this.couple} - ${this.airport} <br>
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
    runway_dict['latitude'] = (runway_dict.beg_latitude + runway_dict.end_latitude)/2;
    runway_dict['longitude'] = (runway_dict.beg_longitude + runway_dict.end_longitude)/2;
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
    var key_list = list_runways.map(({airport, couple}) => airport + "-" + couple);
    check_visible_runway(key_list);
    
    list_runways.forEach(r => {
        var key = r.airport + "-" + r.couple;
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