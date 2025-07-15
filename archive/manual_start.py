#!/usr/bin/env python3
"""
Simple test script to manually start the app and test topscorer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        # Import and run the app
        from app import initialize_app, app
        
        print("Initializing app...")
        if initialize_app():
            print("App initialized successfully!")
            print("Starting Flask server on http://localhost:5000")
            app.run(host='0.0.0.0', port=5000, debug=True)
        else:
            print("Failed to initialize app")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
