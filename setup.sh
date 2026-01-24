#!/bin/bash

# Install requirements
pip install -r requirements.txt

# Download Spacy model
python -m spacy download en_core_web_sm

echo "Setup completed."