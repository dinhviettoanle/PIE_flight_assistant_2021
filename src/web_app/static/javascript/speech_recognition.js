/* Adapted from : https://github.com/googlearchive/webplatform-samples */

var final_transcript = '';
var recognizing = false; // Is the recognizer recognizing ?
var recognition = null; // webkitSpeechRecognition object
var start_timestamp; // To get the duration of the speech
var ignore_onend; // To handle errors

var down = false; // Is the spacebar down ?
const DELAY_AFTER_SPEAK = 1000; // Delay after release of the spacebar before stoping the recording


function init_speech_recognizer() {
    /* Initializes the webkitSpeechRecognition object */
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    console.log("Speech recognizer initialized");

    // When the recognizer starts (triggered in trigger_button)
    recognition.onstart = function() {
        recognizing = true;

        set_status("Speak now");
        console.log("Recognizer started");
        $('#start_button').html("STOP and SEND to server");
    };

    // When the recognizer encounters an error
    recognition.onerror = function(event) {
        set_status(event.error);
        ignore_onend = true;
    };

    // When the recognizer is stopped (triggered in trigger_button)
    recognition.onend = function() {
        recognizing = false;
        if (ignore_onend) {
          return;
        }
        console.log("Final transcript :", final_transcript);
        console.log("Recognizer ended");
        
        send_transcript(final_transcript);

        set_status('Click the button');
        $('#start_button').html("START");
    };

    // When the recognizer receives data
    recognition.onresult = function(event) {
        var interim_transcript = '';
        for (var i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                final_transcript += event.results[i][0].transcript;
            } else {
                interim_transcript += event.results[i][0].transcript;
            }
        }
        final_span.innerHTML = capitalize(final_transcript);
        interim_span.innerHTML = capitalize(interim_transcript);
    };
}


var first_char = /\S/;
function capitalize(s) {
    /* Capitalizes a string (ONLY used for the UI) */
    return s.replace(first_char, function(m) { return m.toUpperCase(); });
}

/****************  TRIGGER FUNCTIONS ***************/

function start_recording(event) {
    final_transcript = '';
    recognition.lang = 'en-US';
    recognition.start();
    ignore_onend = false;

    final_span.innerHTML = '';
    interim_span.innerHTML = '';
    start_timestamp = event.timeStamp;

    // DISPLAY
    // init_audio_display();
    // unmute();
}

function end_recording(event) {
    console.log("Time elapsed :", event.timeStamp - start_timestamp);
    recognition.stop();
}


/* =========== BUTTON =========== */
function trigger_button(event) {
    /* Handles what happens when the button is clicked */
    if (recognizing) {
        end_recording(event);
        // DISPLAY
        // mute();
    }
    else {
        start_recording(event);
    }
}

/* =========== PUSH-TO-TALK =========== */
document.addEventListener('keydown', event => {
    if (event.code === 'Digit1' && isFollowing)  {
        if(down) return;
        down = true;
        start_recording(event);
    }
});


document.addEventListener('keyup', event => {
    if (event.code === 'Digit1' && isFollowing) {
    down = false;
    setTimeout(end_recording, DELAY_AFTER_SPEAK, event);
    // DISPLAY
    // mute();
    }
});



/****************  DOM FUNCTIONS ************** */

function set_status(status_str) {
    /* Displays the current status */
    $('#DOM-status').html(status_str);
}

/****************  NETWORK FUNCTIONS ************** */

function send_transcript(transcript) {
    /* Sends final transcript to the server */
    sent_object = {'transcript': transcript};

    $.ajax({
        type: "GET",
        url: "/_transcript",
        dataType: 'json',
        data: sent_object,
        success: function(data) {
            // console.log(data);
            process_response_str(data.response.response_str);
        }
    });
}

init_speech_recognizer();