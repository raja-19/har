import http.client
import json
import os
import re
import subprocess

api_key = os.environ["GEMINI_API_KEY"]
host = "generativelanguage.googleapis.com"

with open("system.md", "r") as file:
  system = file.read()

conn = http.client.HTTPSConnection(host)
headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
params = {
  "model": "gemini-3.5-flash-lite",
  "system_instruction": system,
  "input": []
}

cwd = os.getcwd()
proj_dir = f"{cwd}/.."

while True:
  print("You:")
  inp = input()
  print("------------------------------------------")

  if inp == "quit":
    print("Har:\nQuitting...")
    break

  matches = re.findall(r"`@([^\s]+)`", inp)

  ok = True

  for path in matches:
    full_path = f"{proj_dir}/{path}"
    if not os.path.isfile(full_path):
      print(f"Har:\nFile {full_path} does not exist.\nTry again.")
      ok = False
      break

    with open(full_path, "r") as file:
      content = file.read()

    ext = os.path.splitext(path)[1].lstrip(".")
    inp += (f"\n\n###{path}\n```{ext}\n{content}```")

  if not ok:
    continue

  with open("hist/hist.json", "r") as file:
    hist = json.load(file)

  hist.append({"type": "user_input", "content": [{"type": "text", "text": inp}]})

  params["input"] = hist

  conn.request("POST", "/v1beta/interactions", json.dumps(params), headers)

  resp = conn.getresponse()

  if resp.status == 200:
    data = json.loads(resp.read())
    outp = data["steps"][1]["content"][0]["text"]

    pattern = r"```diff(.*?)```"
    match = re.search(pattern, outp, re.DOTALL)
    if match:
      text = re.sub(pattern, r"", outp, flags=re.DOTALL).strip()
      diff = match.group(1)
      with open("tmp.patch", "w") as file:
        file.write(diff)
      os.chdir(proj_dir)
      subprocess.run(["git", "apply", "har/tmp.patch"])
      os.chdir(cwd)
      print(f"Model:\n{text}\n------------------------------------------")
    else:
      print(f"Model:\n{outp}\n------------------------------------------")

    hist.append({"type": "model_output", "content": [{"type": "text", "text": json.dumps(outp)}]})
    with open("hist/hist.json", "w") as file:
      json.dump(hist, file)
    os.chdir(f"{cwd}/hist")
    with open("log", "w") as log:
      subprocess.run(["git", "add", "hist.json"])
      subprocess.run(["git", "commit", "-m", inp[:20]])
    os.chdir(cwd)
  else:
    print(f"Har:\n{resp.status} {resp.reason}.")
    break

conn.close()
