from api_app import app, sio

if __name__ == "__main__":
    sio.run(app)