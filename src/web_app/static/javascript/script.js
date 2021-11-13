
var socket = null;
var mymap = null;
var isInitialized = false;

$(document).ready(function(){
    //connect to the socket server.
    var namespace = '/test'
    // socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
    socket = io();

    console.log("Ready !");
    
    //receive details from server
    socket.on('airspace', function(msg) {
        // console.log(msg.list_airports);

        if (!isInitialized) {
            init_graphics(msg.center, msg.radius);
            isInitialized = true;
        }

        var list_flights_string = '';
        msg.list_flights.forEach(f => {
            list_flights_string = list_flights_string + `${f.icao24} - ${f.callsign}<br>`;
        });

        var list_airport_string = '';
        msg.list_airports.forEach(a => {
            list_airport_string = list_airport_string + `${a.icao} (${a.iata}) - ${a.name}<br>`;
        });

        var list_runway_string = '';
        msg.list_runways.forEach(r => {
            list_runway_string = list_runway_string + `${r.le_ident}/${r.he_ident} (${r.airport})<br>`;
        });

        var list_navaid_string = '';
        msg.list_navaids.forEach(r => {
            list_navaid_string = list_navaid_string + `(${r.nav_type}) ${r.ident} ${r.name}<br>`;
        });


        $('#DOM-lastUpdate').html(msg.time_update_str);
        $('#DOM-numberFlights').html(msg.number_flights);
        $('#DOM-listFlights').html(list_flights_string);
        $('#DOM-listAirports').html(list_airport_string);
        $('#DOM-listRunways').html(list_runway_string);
        $('#DOM-listNavaids').html(list_navaid_string);


        update_traffic(msg.list_flights);
        update_airports(msg.list_airports);
        update_runways(msg.list_runways);
        update_navaids(msg.list_navaids);
    });


    socket.on('info', function(msg) {
        console.log('msg');
    });

});