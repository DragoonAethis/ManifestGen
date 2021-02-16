#!/usr/bin/env bash
virtualenv3 .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 markov.py corpus-reddit-clean.txt
