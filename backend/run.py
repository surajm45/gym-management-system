# run.py
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Read host/port/debug from environment (easy to override)
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "production") == "development"

    # Run Flask
    app.run(host="0.0.0.0", port=5000)

    app.run(host=host, port=port, debug=debug)
    
