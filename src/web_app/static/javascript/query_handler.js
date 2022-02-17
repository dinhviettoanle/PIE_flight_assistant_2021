$(".DOM-queryButton").click(function(e) {
    sent_object = {
        q: e.currentTarget.id,
        arg1: document.getElementById("dev_arg1").value,
        arg2: document.getElementById("dev_arg2").value
    };

    $.ajax({
        type: "GET",
        url: "/_query",
        dataType: 'json',
        data: sent_object,
        success: function(data) {
            if (data.response.response_str == 'CHECKLIST') {
                console.log("CHECKLIST");
                process_checklist(data.response.args);
            }
            else if (data.response.response_str == 'METAR') {
                console.log("METAR");
                process_metar(data.response.args);
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

/* ******************************************************** */
/* **************** SPEECH SYNTHESIS ********************** */
/* ******************************************************** */
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
    " kt" : " knots",
    "N/A" : "not available",
    "TWR" : "tower",
    "GND" : "ground",
    "APP" : "approach",
    "BKN" : "broken",
    "OVC" : "overcast",
    "&nbsp;" : ""
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

/* ******************************************************** */
/* ********************** METAR *************************** */
/* ******************************************************** */

function speak_one_metar_item(phrases) {
    // Create a new utterrance at each item
    const utterance = new SpeechSynthesisUtterance();
    utterance.voice = voices.find(voice => voice.name === "Google UK English Male");
    
    // If there is no item
    if (phrases.length == 0) {
        speechSynthesis.cancel();
        return
    }
    
    // Take the first item
    phrase = phrases[0];
    
    utterance.text = phrase;
    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);

    // Pop the first item and reloop
    utterance.onend = (event) => {
        var remaining_phrases = phrases.slice(1);
        speak_one_metar_item(remaining_phrases);
    }
}


function process_metar(metar) {
    $('#DOM-responseQuery').html(metar);
    metar_clean = response_str_to_speak(metar);
    var phrases = metar_clean.split(';');
    speak_one_metar_item(phrases);
}


/* ******************************************************** */
/* ********************** CHECKLISTS ********************** */
/* ******************************************************** */

function set_gui_checklist(checklist_tuple) {
    $("#checklistTable tr").remove(); 
    var DOMChecklistTable = document.getElementById('checklistTable');

    checklist_tuple.forEach(tuple => {
        var item = tuple[0];
        var response = tuple[1];
        var id_item = tuple[2]
        
        var new_row = DOMChecklistTable.insertRow();
        var cell1 = new_row.insertCell(0);
        var cell2 = new_row.insertCell(1);

        cell1.innerHTML = item;
        cell2.innerHTML = `<span id="DOMCheck-Item${id_item}" style="color:#FF0000"> ${response} </span>`;
    });
}

function process_talking_checklist(checklist_name, checklist_tuple) {

    const title_check_msg = new SpeechSynthesisUtterance();
    title_check_msg.voice = voices.find(voice => voice.name === "Google UK English Male");
    
    title_check_msg.text = checklist_name;
    speechSynthesis.cancel();
    speechSynthesis.speak(title_check_msg);

    title_check_msg.onend = function(event) {
        loop_items(checklist_tuple, checklist_name);
    }
    return
}



var response_transcript = '';
function loop_items(checklist_tuple, checklist_name) {
    const item_msg = new SpeechSynthesisUtterance();
    item_msg.voice = voices.find(voice => voice.name === "Google UK English Male");
    
    // If the checklist is empty (all the items have been done)
    if (checklist_tuple.length == 0) {
        item_msg.text = `${checklist_name} complete`;
        speechSynthesis.cancel();
        speechSynthesis.speak(item_msg);
        checkModal.hide();
        return
    }

    var item = checklist_tuple[0][0];
    var response = checklist_tuple[0][1];
    var id_item = checklist_tuple[0][2];

    // Speak item
    item_msg.text = item;
    speechSynthesis.cancel();
    speechSynthesis.speak(item_msg);

    // Speech recognition
    const check_recognition = new webkitSpeechRecognition();
    check_recognition.continuous = true;
    check_recognition.interimResults = true;
    check_recognition.lang = 'en-US';


    // When ends speaking, begin speech recognition
    item_msg.onend = function(event) {
        check_recognition.start();
        // console.log("[CHECKLIST] Begin recognition")  
    }

    // When there is a recognition
    response_transcript = '';
    check_recognition.onresult = function(event) {
        for (var i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                response_transcript += event.results[i][0].transcript;
            } 
        }

        if (response_transcript.length > 0) {
            // If the response is correct, continue with the remaining checklist
            if (response_is_correct(response.toLowerCase(), response_transcript)) {
                document.getElementById(`DOMCheck-Item${id_item}`).style.color = '#00FF00';
                check_recognition.stop();
                
                var remaining_checklist = checklist_tuple.slice(1);
                loop_items(remaining_checklist, checklist_name);
            }
            // Else repeat the current item
            else {
                console.log(response, response_transcript);
                check_recognition.stop();
                loop_items(checklist_tuple, checklist_name);
            }
            
        }
    };
}



function response_is_correct(expected, transcript) {
    // TODO : il faudrait que si ca "ressemble un minimum", ca passe
    return expected == transcript;
}





var checkModal = new bootstrap.Modal(document.getElementById('checklistModal'));
function process_checklist(data) {
    var checklist_name = data.name;
    var checklist_tuple = data.checklist

    $('#checklistModalLabel').html(checklist_name);
    set_gui_checklist(checklist_tuple);

    process_talking_checklist(checklist_name, checklist_tuple);

    checkModal.show();
}