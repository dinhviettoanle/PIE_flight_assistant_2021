# Flight Assistant source code

## Lancement
- Installer les packages requis `pip install -r requirements.txt`
- Si besoin, créer les individus pour l'ontologie : `python3 ./ontology_loader.py`
- Lancer ici `python3 ./run.py`
- Aller sur `localhost:5000`

## Files
- `ontology/`
  - `final-archi.owl` :
  - `final-archi-individuals.owl` :
- `web_app/`
  - `flightradar/` : FlightRadar24 API adapted from this [repo](https://github.com/alexbagirov/py-flightradar24)
  - `static/` : Static files (scripts and images)
  - `templates/` : Templates files (html)
  - `flight_data_handler.py` : Functions to interact with dynamic traffic data
  - `query_ontology` : Functions to query the ontology
  - `views.py` : Flask app views
- `data_loader.py` : Classes for static data (Airport, Runway, Navaid, Frequency)
- `ontology_loader.py` : Individual loader for the ontology
- `run.py` : Run server script