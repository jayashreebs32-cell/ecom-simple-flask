#!/usr/bin/env python
import sys
print("Python version:", sys.version)
print("Starting app...")

try:
    from app import app as flask_app
    print("App imported successfully")
    print("Starting Flask server on 0.0.0.0:5000...")
    flask_app.run(host='0.0.0.0', port=5000, debug=True)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
