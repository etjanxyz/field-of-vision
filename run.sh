#!/bin/bash

# Suppress startup messages
export PYTHONWARNINGS=ignore
export PYGAME_HIDE_SUPPORT_PROMPT=1

# Activate virtual environment and start
source venv/bin/activate && python main.py
