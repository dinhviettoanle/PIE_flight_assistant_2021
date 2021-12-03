$(".DOM-queryButton").click(function(e) {
    sent_object = {q: e.currentTarget.id};

    $.ajax({
        type: "GET",
        url: "/_query",
        dataType: 'json',
        data: sent_object,
        success: function(data) {
            process_response_str(data.response.response_str);
        }
    });
});


function clean_query_response() {
    $('#DOM-responseQuery').html('&nbsp;<br>');
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