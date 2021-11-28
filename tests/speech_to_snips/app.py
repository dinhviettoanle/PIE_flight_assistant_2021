from flask import Flask, render_template, request, jsonify
import logging

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['DEBUG'] = True


# ==========================================================================
# ====================== LOG UTILS =========================================
# ==========================================================================

def print_event(*args, **kwargs):
    # Pretty print text in blue in terminal
    print(f"\033[94m{args}\033[0m")

# ==========================================================================
# ======================== NLP =============================================
# ==========================================================================

def process_transcript(transcript):
    """Processes a speech recognition transcript with Snips-NLU
    and returns a string corresponding to a specific request

    Parameters
    ----------
    transcript : str
        Raw sentence recognized by the speech recognizer

    Returns
    -------
    str
        Normalized string correspoding to a specific request
        For example : 'DepartureAirport', 'NearestAirport', 'RunwaysAtArrival'...
    """
    query = ""
    print_event(transcript)
    # DO STUFF with Snips-NLU
    return query


# ==========================================================================
# ======================== WEB SERVER FUNCTIONS ============================
# ==========================================================================

@app.route('/')
def index():
    """ Main page
    """
    print(request)
    return render_template('index.html')


@app.route('/_transcript', methods=['GET'])
def get_speech_transcript():
    """ Handles the transcript of the client's SpeechRecognition
    """
    transcript = request.args.get('transcript')
    process_transcript(transcript)
    return jsonify({"success" : True})



if __name__ == '__main__':
    app.run()