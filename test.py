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

  with open("hist.json", "r") as file:
    hist = json.load(file)

  if inp == "quit":
    break

  hist.append({"type": "user_input", "content": [{"type": "text", "text": inp}]})
  params["input"] = hist

  conn.request("POST", "/v1beta/interactions", json.dumps(params), headers)

  resp = conn.getresponse()
  if resp.status == 200:
    data = json.loads(resp.read())

    content = data["steps"][1]["content"]

    hist.append({"type": "model_output", "content": content})

    with open("hist.json", "w") as file:
      json.dump(hist, file)

    out = content[0]["text"]
    print(out)

conn.close()
