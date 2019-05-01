#!/bin/bash
#gunicorn -b 0.0.0.0:8000 --reload api:APP
set -e
cd /project && gunicorn -b 0.0.0.0:8000 api:APP
