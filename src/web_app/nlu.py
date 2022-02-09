from .query_ontology import *
from .log_utils import *

from snips_nlu import SnipsNLUEngine

# =======================================================================
# ===================== NLP =============================================
# =======================================================================

nlu_engine_filename = "./nlu/engine.snips"
nlu_engine = None


def load_nlu_engine():
    global nlu_engine
    fprint("Loading NLU engine...")
    with open(nlu_engine_filename,'rb') as f:
        engine_bytes = f.read()
    nlu_engine = SnipsNLUEngine.from_byte_array(engine_bytes)
    fprint("NLU engine loaded !")




def process_transcript(transcript):
    global nlu_engine
    query = ""
    print_event("SPEECH RECOGNITION", transcript)

    question = transcript.lower()
    parsing = nlu_engine.parse(question)
    query = parsing['intent']['intentName']

    print_event("NLU", parsing['intent'], parsing['slots'])

    # if transcript.lower() == "what is the nearest airport":
    #     query = "NearestAirport"

    # elif transcript.lower() == "what are the runways at arrival":
    #     query = "RunwaysAtArrival"
    
    # elif transcript.lower() == "what is the departure airport":
    #     query = "DepartureAirport"

    # elif transcript.lower() == "what is the temperature at arrival":
    #     query = "TemperatureAtArrival"

    # elif transcript.lower() in ["what is the wind at LFBO", "what is the wind at toulouse blagnac"]:
    #     query = "WindAtAirport?LFBO"

    # elif transcript.lower() in ["give me the landing checklist", "landing checklist"]:
    #     query = "ChecklistLanding"

    # elif transcript.lower() in ["give me the approach checklist", "approach checklist"]:
    #     query = "ChecklistApproach"

    return query


if __name__ == '__main__':
    os.system(f'snips-nlu generate-dataset en {yaml_filename} > {json_filename}')
    fit_engine()