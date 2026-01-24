#!/bin/bash

# Gereksinimleri yükle
pip install -r requirements.txt

# Spacy modelini indir
python -m spacy download en_core_web_sm

echo "Kurulum tamamlandı."