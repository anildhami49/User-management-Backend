#!/bin/bash
# Azure App Service startup command for Python Flask
gunicorn --bind=0.0.0.0:$PORT --workers=1 --threads=4 --timeout=0 --access-logfile=- --error-logfile=- app:app
