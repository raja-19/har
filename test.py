import http.client
import json
# import urllib.parse
import os

api_key = os.environ["GEMINI_API_KEY"]
host = "generativelanguage.googleapis.com"
conn = http.client.HTTPSConnection(host)
headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
params = {"model": "gemini-3.5-flash-lite", "input": "hello"}

while True:
  inp = input()
  if inp == "quit":
    break

  params["input"] = inp
  conn.request("POST", "/v1beta/interactions", json.dumps(params), headers)

  resp = conn.getresponse()
  if resp.status == 200:
    out = json.loads(resp.read())["steps"][1]["content"][0]["text"]
    print(out)

conn.close()
