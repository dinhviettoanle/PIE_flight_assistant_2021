from web_app.views import app, sio

if __name__ == "__main__":
    sio.run(app, use_reloader=True, host="0.0.0.0")