# PIE Flight Assistant 2021

A web deployment of the app is available [here](https://pie2021-flightassistant-v21.herokuapp.com/).


## Repository
You will need Git Large File Storage (git-lfs) to clone the repository. Follow these [instructions](https://git-lfs.github.com/).

### Content description
- `data/` : 
- `doc/` : 
- `report/` : 
- `src/` : 
- `tests/` : 

## Setup 
Works under Python 3.8

**Prerequisites**
- You need to have an OpenWeatherMap account with an active API key. Set the environment variable `OWM_APIKEY=<your-owm-api-key>`.
- Set the environment variable `PORT=5000`.


### Full setup

- If you are under native Windows (not WSL), follow [this](https://snips-nlu.readthedocs.io/en/latest/installation.html) to install Snips-NLU beforehand.

In the folder `src/`:
1. (Create an venv or conda environment) 
2. Install requirements `pip install -r requirements.txt`
3. Run `python app.py`
4. Open `localhost:5000`

### Docker 
*Only for test purposes*

In the root folder (where the `Dockerfile` is located) :

1. Build the image : `docker build -t flightassistant:latest .`
2. Run the image in a container : `docker run -it --rm -p 5000:5000 flightassistant:latest`
3. Open `localhost:5000`

## Deployment

### Heroku
In the root folder (where the `Dockerfile` and `gunicorn_starter.sh` are located) :

1. Check that the eol in `gunicorn_starter.sh` is LF.
2. Create an app : `heroku create --region eu <appname>`
3. Login to the containers : `heroku container:login`
4. Push the image : `heroku container:push web -a <appname>`
5. Release : `heroku container:release web -a <appname>`


## Remaining issues
- [ ] Speech Recognition : it doesn't know when the user is spelling or not. Ex : for an ICAO airport containing "..RU", it understands ".. are you"
- [ ] Query WeatherAtWaypoint is impossible to detect using SpeechRecognition
- [ ] The app often (always) crashes when it runs for a long time. See `FlightSpecificQueryHandlerFR24.query_dynamic_data()`