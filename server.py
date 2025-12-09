# app.py

from app import create_flask_app

from config import PORT

if __name__ == "__main__":
    server = create_flask_app()
    server.run(host="0.0.0.0", port=PORT, debug=False)
