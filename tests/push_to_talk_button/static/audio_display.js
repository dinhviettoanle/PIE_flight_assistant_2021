/* Adapted from https://github.com/mdn/voice-change-o-matic/tree/gh-pages */

// Canvas
var canvas = document.querySelector('.visualizer');
var canvasCtx = canvas.getContext("2d");
WIDTH = canvas.width;
HEIGHT = canvas.height;
canvasCtx.clearRect(0, 0, WIDTH, HEIGHT);
canvasCtx.fillStyle = 'rgb(0, 0, 0)';
canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);

// Variables
var is_init_audio = false;
var audioCtx = null;
var analyser = null;
var gainNode = null;
var is_mute = true;





function init_audio_display() {
    if (is_init_audio) return;

    // For the mic
    if (navigator.mediaDevices === undefined) {
        navigator.mediaDevices = {};
    }

    if (navigator.mediaDevices.getUserMedia === undefined) {
        navigator.mediaDevices.getUserMedia = function (constraints) {

            var getUserMedia = navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
            if (!getUserMedia) {
                return Promise.reject(new Error('getUserMedia is not implemented in this browser'));
            }
            return new Promise(function (resolve, reject) {
                getUserMedia.call(navigator, constraints, resolve, reject);
            });
        }
    }

    // Audio context
    audioCtx = new(window.AudioContext || window.webkitAudioContext)();
    gainNode = audioCtx.createGain();

    analyser = audioCtx.createAnalyser();
    analyser.minDecibels = -90;
    analyser.maxDecibels = -10;
    analyser.smoothingTimeConstant = 0.8;
    analyser.fftSize = 32;


    if (navigator.mediaDevices.getUserMedia) {
        console.log('getUserMedia supported.');
        var constraints = {
            audio: true
        }
        navigator.mediaDevices.getUserMedia(constraints)
            .then(
                function (stream) {
                    source = audioCtx.createMediaStreamSource(stream);
                    source.connect(gainNode);
                    gainNode.connect(analyser);
                    visualize();
                })
            .catch(function (err) {
                console.log('The following gUM error occured: ' + err);
            })
    } else {
        console.log('getUserMedia not supported on your browser!');
    }

    is_init_audio = true;
}


function mute() {
    gainNode.gain.value = 0;
}

function unmute() {
    gainNode.gain.value = 1;
}

const average = arr => arr.reduce( ( p, c ) => p + c, 0 ) / arr.length;

function visualize() {
    // Make a circle that becomes more or less big (less space)
    var bufferLengthAlt = analyser.frequencyBinCount;
    var dataArrayAlt = new Uint8Array(bufferLengthAlt);

    var drawAlt = function () {
        drawVisual = requestAnimationFrame(drawAlt);

        analyser.getByteFrequencyData(dataArrayAlt);

        canvasCtx.fillStyle = 'rgb(0, 0, 0)';
        canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);

        var barWidth = (WIDTH / bufferLengthAlt) * 2.5;
        var barHeight;
        var x = 0;

        for (var i = 0; i < bufferLengthAlt; i++) {
            barHeight = dataArrayAlt[i];
            // barHeight = Math.max(...dataArrayAlt);
            // barHeight = average(dataArrayAlt);
            
            canvasCtx.fillStyle = 'rgb(' + (barHeight + 100) + ',50,50)';
            canvasCtx.fillRect(x, HEIGHT - barHeight / 2, barWidth, barHeight / 2);

            x += barWidth + 1;
        }
    };

    drawAlt();

}