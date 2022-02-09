# PIE Flight Assistant 2021

## Repository
You will need Git Large File Storage (git-lfs) to clone the repository. Follow these [instructions](https://git-lfs.github.com/).

## Setup 
Works under Python 3.8

If you are under native Windows (not WSL), follow [this](https://snips-nlu.readthedocs.io/en/latest/installation.html) to install Snips-NLU - you will need to install Rust first.
If you are in a venv, you must be admin ??
### Full setup
In the folder `src/`:
1. (Create an venv or conda environment) 
2. Install requirements `pip install -r requirements.txt`
3. Run `python app.py`
4. Open `localhost:5000`

### Docker 
*Only for test purposes*

In the root folder (where the `Dockerfile` is located) :
1. Build the image : `docker build -t flightassistant:latest .`
2. Run the image in a container : `docker run -it -p 5000:5000 flightassistant`
3. Open `localhost:5000`

## Deployment
In the root folder (where the `Dockerfile` and `gunicorn_starter.sh` are located) :

0. Check that the eol in `gunicorn_starter.sh` is LF.
1. Create an app : `heroku create --region eu <appname>`
2. Login to the containers : `heroku container:login`
3. Push the image : `heroku container:push web -a <appname>`
4. Release : `heroku container:release web -a <appname>`