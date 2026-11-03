import http.client
import json
# import urllib.parse
import os

api_key = os.environ["GEMINI_API_KEY"]
host = "generativelanguage.googleapis.com"
system = ""


conn = http.client.HTTPSConnection(host)
headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
params = {
  "model": "gemini-3.5-flash-lite",
  "system_instruction": system,
  "input": []
}

while True:
  inp = input()
  if inp == "quit":
    break

  params["input"].append({"type": "user_input", "content": [{"type": "text", "text": inp}]})
  print(params)
  conn.request("POST", "/v1beta/interactions", json.dumps(params), headers)

  resp = conn.getresponse()
  if resp.status == 200:
    data = json.loads(resp.read())
    content = data["steps"][1]["content"][0]
    params["input"].append(content)
    out = content["text"]
    print(out)

conn.close()
