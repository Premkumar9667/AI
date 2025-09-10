#!/usr/bin/env python3
"""
Local development runner for Prem Kumar's AI Engineer Portfolio
Run this file to start the development server locally
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the Flask app
from app_local import app

if __name__ == '__main__':
    # Run the development server
    app.run(
        host='127.0.0.1',  # localhost for local development
        port=5000,
        debug=True
    )