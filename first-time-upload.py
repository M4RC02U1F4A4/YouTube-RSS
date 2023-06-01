# python first-time-upload.py http:.....

import requests
import sys

url = sys.argv[1]

with open("ids.txt") as file:
    ids = [line.rstrip() for line in file]

for id in ids:
    r = requests.get(f"{url}/add/{id}")
    print(f"{id} - {r.status_code}")