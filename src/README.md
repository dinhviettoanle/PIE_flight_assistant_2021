# Flight Assistant source code

## Setup
1. (Create an venv or conda environment) 
2. Install requirements `pip install -r requirements.txt`
    - (If needed, create individuals for the ontology with `python ontology_loader.py`) 
    - (If needed, train the Snips NLU engine with `python train_nlu_engine.py`)
3. Run `python app.py`
4. Open `localhost:5000`

## Files and folders
- `checklist/` : .csv files containing checklists.
- `nlu/` : Training dataset (`requests_dataset.yaml`) for the Snips NLU engine, and pre-trained Snips NLU engine (`engine.snips`).
- `ontology/` : Empty ontology (`final-archi.owl`) file and filled ontology with individuals (`final-archi-individuals.owl`).
- `web_app/` : Main source files.
  - `flightradar/` : FlightRadar24 API adapted from this [repo](https://github.com/alexbagirov/py-flightradar24).
  - `static/` : Static files (style, images and scripts).
  - `templates/` : Templates files (html).