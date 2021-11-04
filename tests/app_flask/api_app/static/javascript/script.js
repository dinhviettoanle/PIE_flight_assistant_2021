
var socket = null;
var mymap = null;

$(document).ready(function(){
    //connect to the socket server.
    var namespace = '/test'
    // socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
    socket = io();

    console.log("Ready !");
    
    //receive details from server
    socket.on('airspace', function(msg) {
        // console.log(msg.list_airports);

        var list_flights_string = '';
        msg.list_flights.forEach(f => {
            list_flights_string = list_flights_string + `${f.icao24} - ${f.callsign}<br>`;
        });

        var list_airport_string = '';
        msg.list_airports.forEach(a => {
            list_airport_string = list_airport_string + `${a.icao} (${a.iata})<br>`;
        });


        $('#DOM-lastUpdate').html(msg.time_update_str);
        $('#DOM-numberFlights').html(msg.number_flights);
        $('#DOM-listFlights').html(list_flights_string);
        $('#DOM-listAirports').html(list_airport_string);


        update_traffic(msg.list_flights);
        update_airports(msg.list_airports);
    });

});