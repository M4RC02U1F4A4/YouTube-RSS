# python first-time-upload.py http:.....

import requests
import sys

url = sys.argv[1]

with open("links.txt") as file:
    links = [line.rstrip() for line in file]

for link in links:
    r = requests.post(f"{url}/add", data={'link':link})
    print(f"{link} - {r.status_code}")