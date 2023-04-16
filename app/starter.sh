#!/bin/sh
python rss.py & gunicorn main:app -w 4 --threads 4 -b 0.0.0.0:5001