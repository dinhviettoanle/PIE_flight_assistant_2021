$(".DOM-queryButton").click(function(e) {
    sent_object = {q: e.currentTarget.id};

    $.ajax({
        type: "GET",
        url: "/_query",
        dataType: 'json',
        data: sent_object,
        success: function(data) {
            if (data.response.response_str == 'CHECKLIST') {
                process_checklist(data.response.args);
            }
            else {
                process_response_str(data.response.response_str);
            }
        }
    });
});


function clean_query_response() {
    $('#DOM-responseQuery').html('&nbsp;<br>');
    $('#final_span').html('');
    $('#interim_span').html('');
}

/* SPEECH SYNTHESIS */
const msg = new SpeechSynthesisUtterance();

// Voices
var voices = null;
speechSynthesis.addEventListener("voiceschanged", () => {
    voices = speechSynthesis.getVoices()
  })



function process_response_str(response_str) {
    $('#DOM-responseQuery').html(response_str);
    msg.voice = voices.find(voice => voice.name === "Google UK English Male");
    msg.text = response_str_to_speak(response_str);
    console.log("Is speaking...")
    speechSynthesis.cancel();
    speechSynthesis.speak(msg);
}


const abbreviations = {
    " nm" : " nautical miles",
    "N/A" : "not available"
}

String.prototype.allReplace = function(obj) {
    var retStr = this;
    for (var x in obj) {
        retStr = retStr.replace(new RegExp(x, 'g'), obj[x]);
    }
    return retStr;
};


function response_str_to_speak(response_str) {
    // Abbreviations
    response_speak = response_str.allReplace(abbreviations);

    // Runways Right and Left
    var pattern = /([0-9]{2})R/g;
    response_speak = response_speak.replace(pattern, "$1 right");
    var pattern = /([0-9]{2})L/g;
    response_speak = response_speak.replace(pattern, "$1 left");

    return response_speak;
}


function test_checklist() {
    process_checklist({
        'name' : 'Landing checklist',
        'checklist' : [["Landing gear", "DOWN"], ["Autopilot", "DISCONNECTED"], ["Go-around altitude", "SET"]]
    });
}


function set_gui_checklist(checklist_tuple) {
    $("#checklistTable tr").remove(); 
    var DOMChecklistTable = document.getElementById('checklistTable');

    checklist_tuple.forEach(tuple => {
        var item = tuple[0];
        var response = tuple[1];
        
        var new_row = DOMChecklistTable.insertRow();
        var cell1 = new_row.insertCell(0);
        var cell2 = new_row.insertCell(1);

        cell1.innerHTML = item;
        cell2.innerHTML = `<span id="DOMCheck-${response}" style="color:#FF0000"> ${response} </span>`;
    });
}


function process_talking_checklist(checklist_tuple) {

    msg.voice = voices.find(voice => voice.name === "Google UK English Male");
    
    checklist_tuple.forEach(tuple => {
        var item = tuple[0];
        var response = tuple[1];
        
        // TODO HERE
        msg.text = item;
        speechSynthesis.cancel();
        speechSynthesis.speak(msg);
    });


    return
}

function process_checklist(data) {
    var checkModal = new bootstrap.Modal(document.getElementById('checklistModal'));

    var checklist_name = data.name;
    var checklist_tuple = data.checklist
    console.log(checklist_tuple)

    $('#checklistModalLabel').html(checklist_name);
    set_gui_checklist(checklist_tuple);

    process_talking_checklist(checklist_tuple);

    checkModal.show();
}