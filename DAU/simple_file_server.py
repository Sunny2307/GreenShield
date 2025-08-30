#!/usr/bin/env python3
"""
Simple file server for testing photos locally.
Run this to serve photos from a local directory.
"""

import http.server
import socketserver
import os
from pathlib import Path

# Create photos directory if it doesn't exist
photos_dir = Path("photos")
photos_dir.mkdir(exist_ok=True)

# Create a sample photo placeholder
sample_photo_path = photos_dir / "sample_mangrove.jpg"
if not sample_photo_path.exists():
    # Create a simple text file as placeholder
    with open(sample_photo_path, "w") as f:
        f.write("This is a placeholder for a mangrove photo")

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(photos_dir), **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_file_server(port=8080):
    """Start a simple file server."""
    with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
        print(f"🌿 File server started at http://localhost:{port}")
        print(f"📁 Serving files from: {photos_dir.absolute()}")
        print(f"📸 Sample photo URL: http://localhost:{port}/sample_mangrove.jpg")
        print("\n📋 Instructions:")
        print("1. Put your photos in the 'photos' folder")
        print("2. Use URLs like: http://localhost:8080/your_photo.jpg")
        print("3. Press Ctrl+C to stop the server")
        print("\n" + "="*50)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 File server stopped")

if __name__ == "__main__":
    start_file_server()
