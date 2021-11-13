var dict_navaids = {}

class Navaid extends Location{
    constructor(navaid) {
        super(navaid);
        
        this.ident = navaid.ident;
        this.name = navaid.name;
        this.nav_type = navaid.nav_type;
        this.frequency = navaid.frequency;
        this.altitude = navaid.altitude;

        this.nav_url = (this.nav_type.includes('NDB')) ? ndb_url : vor_url;
        
        var currentZoom = mymap.getZoom();
        var size = 0
        if (currentZoom <= 5) { size = 0; }
        else if (5 < currentZoom && currentZoom <= 14) { size = 2.9*currentZoom - 14.2; }
        else { size = 25; }
        var navaid_icon = L.icon({
            iconUrl: this.nav_url,
            iconSize:     [size, size],
            iconAnchor:   [size/2, size/2],
        });


        this.marker = new L.marker([this.latitude, this.longitude], {icon : navaid_icon});
        this.marker.bindTooltip(`${this.ident} - ${this.name} <br>
                                    Type : ${this.nav_type} <br>
                                    Altitude : ${this.altitude} <br>
                                    Frq : ${this.frequency} KHz`, 
                                {className: "navaidToolTip"});
    }
}

function check_visible_navaids(key_list) {
    for (const [key, navaid] of Object.entries(dict_navaids)) {
        if (navaid.is_outside_map(minLong, maxLong, minLat, maxLat, center) || !key_list.includes(key)) {
            navaid.free_map(mymap);
            delete dict_navaids[key];
        }
    }
}

function update_navaids(list_navaids) {
    var key_list = list_navaids.map(({ident, nav_type}) => ident + "-" + nav_type);
    check_visible_navaids(key_list);
    
    list_navaids.forEach(n => {
        var key = n.ident + "-" + n.nav_type;
        if (!(key in dict_navaids)) {
            let navaid = new Navaid(n);
            if (navaid.is_outside_map(minLong, maxLong, minLat, maxLat, center)) {
                delete dict_navaids[key];
            }
            else {
                dict_navaids[key] = navaid;
                navaid.draw_map(mymap);
            }
        }
    });
}


function setZoomNavIcons(size) {
    for (const [key, navaid] of Object.entries(dict_navaids)) {
        var LeafIcon = L.icon({
            iconUrl: navaid.nav_url,
            iconSize:     [size, size],
            iconAnchor:   [size/2, size/2],
        });
        navaid.marker.setIcon(LeafIcon);
    }
}


mymap.on('zoomend', function() {
    var currentZoom = mymap.getZoom();
    if (currentZoom <= 5) {
        setZoomNavIcons(0);
    }
    else if (5 < currentZoom && currentZoom <= 14) {
        setZoomNavIcons(2.9*currentZoom - 14.2);
    }
    else {
        setZoomNavIcons(25);

    }

});