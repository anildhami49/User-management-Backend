#!/bin/bash
# Azure App Service startup command for Python Flask
gunicorn --bind=0.0.0.0:8000 --workers=4 --timeout=600 --access-logfile '-' --error-logfile '-' app:app
