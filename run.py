from waitress import serve
from app import app
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.getenv('PORT', 5000))
    
    # Print startup message
    print(f"\nStarting Community App server on port {port}...")
    print("Visit http://localhost:5000 or http://127.0.0.1:5000 in your browser")
    print("Press Ctrl+C to stop the server\n")
    
    # Run the app with Waitress
    serve(app, host='0.0.0.0', port=port, threads=4)