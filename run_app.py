import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import init_db

init_db()
print("Database initialized successfully")
from app import app

print("Starting Flask server on http://0.0.0.0:5000")
app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
