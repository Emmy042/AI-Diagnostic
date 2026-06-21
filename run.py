import os
from dotenv import load_dotenv

load_dotenv()

from app.web import create_app
app = create_app()


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "0").lower() in ["1", "true"]
    app.run(host="127.0.0.1", port=5000, debug=debug_mode, use_reloader=False)
