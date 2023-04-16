import requests

url = "http://127.0.0.1:5001"

with open("links.txt") as file:
    links = [line.rstrip() for line in file]

for link in links:
    r = requests.post(f"{url}/add", data={'link':link})
    print(f"{link} - {r.status_code}")