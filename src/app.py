from web_app.views import app, sio
import os

port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    sio.run(app, use_reloader=True, host="0.0.0.0", port=port)