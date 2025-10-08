#!/bin/bash

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Start gunicorn with uvicorn worker
gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
