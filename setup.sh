#!/usr/bin/env bash

python -m venv .
source bin/activate
pip install -r requirements.txt
python app.py
