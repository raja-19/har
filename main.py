import http.client
import json
import os

api_key = os.environ["GEMINI_API_KEY"]
host = "generativelanguage.googleapis.com"
system = "The response format (no codeblock or extra characters): {\"text\": \"<text output>\"} or {\"text\": \"<text output>\", \"file\": {\"path\": \"<path>\", \"content\": \"<content>\"}, if the response suggests a file modification (in such a case, the response should contain the full updated contents of the modified file). The path must match a path from one of the requests (they follow the same format)."

conn = http.client.HTTPSConnection(host)
headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
params = {
  "model": "gemini-3.5-flash-lite",
  "system_instruction": system,
  "input": []
}

with open("input.json", "r") as file:
  req = json.load(file)

with open("hist.json", "r") as file:
  hist = json.load(file)

if "file" in req:
  path = req["file"]["path"]
  with open(path, "r") as file:
    content = file.read()
  req["file"]["content"] = content

params["input"] = json.dumps(req)

conn.request("POST", "/v1beta/interactions", json.dumps(params), headers)

resp = conn.getresponse()

if resp.status == 200:
  data = json.loads(resp.read())
  res = json.loads(data["steps"][1]["content"][0]["text"])

  hist.append({"type": "user_input", "content": [{"type": "text", "text": json.dumps(req)}]})
  hist.append({"type": "model_output", "content": json.dumps(res)})

  with open("hist.json", "w") as file:
    json.dump(hist, file)

  print(res)
  if "file" in res:
    path = res["file"]["path"]
    content = res["file"]["content"]
    with open(path, "w") as file:
      file.write(content)
else:
  print(resp.status, resp.reason)

conn.close()
