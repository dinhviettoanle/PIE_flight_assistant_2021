from .query_ontology import *
from .log_utils import *


# =======================================================================
# ===================== NLP =============================================
# =======================================================================

def process_transcript(transcript):
    query = ""
    print_event("SPEECH RECOGNITION", transcript)
    # DO STUFF with Snips-NLU

    if transcript.lower() == "what is the nearest airport":
        query = "NearestAirport"

    elif transcript.lower() == "what are the runways at arrival":
        query = "RunwaysAtArrival"
    
    elif transcript.lower() == "what is the departure airport":
        query = "DepartureAirport"

    elif transcript.lower() == "what is the temperature at arrival":
        query = "TemperatureAtArrival"

    elif transcript.lower() in ["what is the wind at LFBO", "what is the wind at toulouse blagnac"]:
        query = "WindAtAirport?LFBO"

    elif transcript.lower() in ["give me the landing checklist", "landing checklist"]:
        query = "ChecklistLanding"

    elif transcript.lower() in ["give me the approach checklist", "approach checklist"]:
        query = "ChecklistApproach"

    return query
