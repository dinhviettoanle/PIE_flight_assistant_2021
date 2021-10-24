
var socket = null;

$(document).ready(function(){
    //connect to the socket server.
    var namespace = '/test'
    socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

    console.log("Ready !");
    
    //receive details from server
    socket.on('airspace', function(msg) {
        console.log(msg);

        var list_flights_string = '';
        msg.list_flights.forEach(f => {
            list_flights_string = list_flights_string + `${f.icao24} - ${f.callsign}<br>`;
        });
        
        $('#DOM-lastUpdate').html(msg.time_update_str);
        $('#DOM-numberFlights').html(msg.number_flights);
        $('#DOM-listFlights').html(list_flights_string);
        update_map(msg.list_flights);
    });

});