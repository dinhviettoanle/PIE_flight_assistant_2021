
var socket = null;
var mymap = null;
var isInitialized = false;
var isFollowing = false;
var currentFollowing = "";

$(document).ready(function(){
    //connect to the socket server.
    // var namespace = '/test'
    // socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
    socket = io();

    socket.emit('init_worker');
    
    console.log("Ready !");
    
    //receive details from server
    socket.on('airspace', function(msg) {
        // console.log(msg);

        if (!isInitialized) {
            init_graphics(msg.center, msg.radius);
            isInitialized = true;
            myModal.toggle();
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
            list_runway_string = list_runway_string + `${r.couple} (${r.airport})<br>`;
        });

        var list_navaid_string = '';
        msg.list_navaids.forEach(r => {
            list_navaid_string = list_navaid_string + `(${r.nav_type}) ${r.ident} ${r.name}<br>`;
        });

        var list_waypoint_string = '';
        msg.list_waypoints.forEach(w => {
            list_waypoint_string = list_waypoint_string + `${w.ident} (${w.country})<br>`;
        });


        $('#DOM-lastUpdate').html(msg.time_update_str);
        $('#DOM-numberFlights').html(msg.number_flights);
        $('#DOM-listFlights').html(list_flights_string);
        $('#DOM-listAirports').html(list_airport_string);
        $('#DOM-listRunways').html(list_runway_string);
        $('#DOM-listNavaids').html(list_navaid_string);
        $('#DOM-listWaypoints').html(list_waypoint_string);


        update_traffic(msg.list_flights);
        update_airports(msg.list_airports);
        update_runways(msg.list_runways);
        update_navaids(msg.list_navaids);
        update_waypoints(msg.list_waypoints);
    });


    socket.on('info', function(msg) {
        console.log(msg);
    });

    socket.on('follow_flight_info', function(data) {
        // console.log(data);
        var flight_data_str = "&nbsp;<br>&nbsp;<br>&nbsp;";
        isFollowing = data.is_following;

        if (isFollowing) {

            if (data.callsign != currentFollowing){
                if (currentFollowing != "") { // If we were already following a flight
                    dict_airplanes[currentFollowing].set_traffic_marker();
                }
                dict_airplanes[data.callsign].set_follow_marker();
                currentFollowing = data.callsign;
            }

            var flight_data_str = `
                <b>Callsign : </b>${data.callsign} ; 
                <b>Registration : </b> ${data.registration} ; 
                <b>Model : </b> ${data.model} (${data.model_text})
                <br>
                <b>Route : </b> ${data.origin} ⟶ ${data.destination} ;
                <b>Last contact : </b> ${data.last_contact}
                <br>
                <b>Position : </b> (${data.lat}, ${data.lon}) ; 
                <b>Altitude : </b> ${data.alt} ft ; 
                <b>Vg : </b> ${data.speed} kt ; 
                <b>Vz : </b> ${data.vertical_speed} ft/min ; 
                <b>Heading : </b> ${data.heading}`;

            if (center[0] != data.lat || center[1] != data.lon){
                change_focus(data.lat, data.lon, true);
            }
            $(".DOM-queryButton").attr("disabled", false);
            $(".DOM-queryArg").attr("disabled", false);

        }
        else {
            // Disable query buttons
            $('.DOM-queryButton').attr('disabled', true);
            $('.DOM-queryArg').attr('disabled', true);
        }

        $('#DOM-flightDescription').html(flight_data_str);
 
    });
});


function dev_mode_checked() {
    var checkBox = document.getElementById("checkbox_dev");
    var DOM_devbuttons = document.getElementById("DOM-dev_buttons");
    var DOM_devdata = document.getElementById("DOM-dev_data");
  
    if (checkBox.checked == true){
        DOM_devbuttons.style.display = "block";
        DOM_devdata.style.display = "block";
    } else {
        DOM_devbuttons.style.display = "none";
        DOM_devdata.style.display = "none";
    }
  }