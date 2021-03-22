#!/usr/bin/env bash
export FLASK_APP="app:create_app"
export FLASK_ENV=development
flask run --port=50000