#!/bin/bash

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting background job..."
python3 app.py
