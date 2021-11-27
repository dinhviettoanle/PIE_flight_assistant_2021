var dict_waypoints = {}

class Waypoint extends Location{
    constructor(waypoint) {
        super(waypoint);
        
        this.ident = waypoint.ident;
        this.country = waypoint.country;
        this.latitude = waypoint.latitude;
        this.longitude = waypoint.longitude;
        
        var currentZoom = mymap.getZoom();
        var size = 0
        if (currentZoom <= 6) { size = 0; }
        else if (6 < currentZoom && currentZoom <= 15) { size = 2.1*currentZoom - 12.2; }
        else { size = 20; }
        var waypoint_icon = L.icon({
            iconUrl:      waypoint_url,
            iconSize:     [size, size],
            iconAnchor:   [size/2, size/2],
        });


        this.marker = new L.marker([this.latitude, this.longitude], {icon : waypoint_icon});
        this.marker.bindTooltip(`${this.ident} (${this.country})`,
                                {className: "waypointToolTip"});
    }
}

function check_visible_waypoints(key_list) {
    for (const [key, waypoint] of Object.entries(dict_waypoints)) {
        if (waypoint.is_outside_map(minLong, maxLong, minLat, maxLat, center) || !key_list.includes(key)) {
            waypoint.free_map(mymap);
            delete dict_waypoints[key];
        }
    }
}

function update_waypoints(list_waypoints) {
    var key_list = list_waypoints.map(({ident, country}) => ident + "-" + country);
    check_visible_waypoints(key_list);
    
    list_waypoints.forEach(n => {
        var key = n.ident + "-" + n.country;
        if (!(key in dict_waypoints)) {
            let waypoint = new Waypoint(n);
            if (waypoint.is_outside_map(minLong, maxLong, minLat, maxLat, center)) {
                delete dict_waypoints[key];
            }
            else {
                dict_waypoints[key] = waypoint;
                waypoint.draw_map(mymap);
            }
        }
    });
}


function setZoomWaypointIcons(size) {
    for (const [key, waypoint] of Object.entries(dict_waypoints)) {
        var LeafIcon = L.icon({
            iconUrl:      waypoint_url,
            iconSize:     [size, size],
            iconAnchor:   [size/2, size/2],
        });
        waypoint.marker.setIcon(LeafIcon);
    }
}


mymap.on('zoomend', function() {
    var currentZoom = mymap.getZoom();
    if (currentZoom <= 6) {
        setZoomWaypointIcons(0);
    }
    else if (6 < currentZoom && currentZoom <= 15) {
        setZoomWaypointIcons(2.1*currentZoom - 12.2);
    }
    else {
        setZoomWaypointIcons(20);

    }

});