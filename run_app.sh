#!/bin/bash

# Script to run the application with environment variables from .env file

# Load environment variables from .env if present
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Activate virtual environment
source venv/bin/activate

# Ensure required packages are installed
pip install -r requirements.txt

# Run the application
python main.py

