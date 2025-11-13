#!/bin/bash
# Start the AFL Player Over/Under Search API server

# Activate virtual environment
source .venv/bin/activate

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

