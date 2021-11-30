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


def process_transcript(transcript):
    query = ""
    print_event(transcript)
    # DO STUFF with Snips-NLU
    return query



@app.route('/')
def index():
    print(request)
    return render_template('index.html')


@app.route('/_transcript', methods=['GET'])
def get_speech_transcript():
    transcript = request.args.get('transcript')
    process_transcript(transcript)
    return jsonify({"success" : True})



if __name__ == '__main__':
    app.run()