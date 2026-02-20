
from waitress import serve
from app import create_app
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    # Create app instance
    app = create_app()
    
    # Get port from environment or default to 5000
    port = int(os.getenv('PORT', 5000))
    
    # Print startup message
    print(f"\nStarting Community App server on port {port}...")
    print(f"Visit http://localhost:{port} or http://127.0.0.1:{port} in your browser")
    print("Press Ctrl+C to stop the server\n")
    
    # Run the app with Waitress
    serve(app, host='0.0.0.0', port=port, threads=4)