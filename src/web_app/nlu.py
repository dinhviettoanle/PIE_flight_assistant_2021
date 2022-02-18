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
    fprint("Loading NLU engine...", end=" ")
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
    intent_name = parsing['intent']['intentName']
    proba = parsing['intent']['probability']
    slots = parsing['slots']

    if intent_name is not None:
        # If nearestEntity request
        if intent_name == 'nearestEntity':
            entity_requested = slots[0]['value']['value']
            if entity_requested == 'airport':
                query = "nearestAirport"
            elif entity_requested == 'traffic':
                query = "nearestTrafic"
            elif entity_requested == 'runway':
                query = "runwaysAtNearestAirport"
            else:
                query = ""
        

        
        # If entityAtAirport request:
        elif intent_name == 'entityAtAirport':
            entity_requested = slots[0]['value']['value']
            if entity_requested == 'runway':
                query = "runwaysAtAirport"
                query += f"?{slots[1]['value']['value']}"
            else:
                # Weather: METAR or normal
                query = "weatherAtAirport"
                weather_param_requested = slots[0]['value']['value']
                if weather_param_requested == 'metar':
                    query = 'metarAtAirport'
                    query += f"?{slots[1]['value']['value']}"
                else:
                    query = 'weatherAtAirport'
                    for i, arg in enumerate(slots):
                        query += f"?{arg['value']['value']}"
            
        else:
            query = intent_name
            # Add arguments
            for i, arg in enumerate(slots):
                query += f"?{arg['value']['value']}"
    
    print_event(parsing)
    print_event("NLU", intent_name, proba, query)

    return query


if __name__ == '__main__':
    os.system(f'snips-nlu generate-dataset en {yaml_filename} > {json_filename}')
    fit_engine()