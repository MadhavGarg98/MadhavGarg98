"""Runs when someone opens an 'Add my pixel' issue. Gives them one square of the face."""
import base64, io, json, os, random, re, sys, urllib.request
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_puzzle as rp

ROOT = rp.ROOT
user = os.environ.get("ISSUE_USER", "").strip()
result = os.path.join(ROOT, "result.txt")


def say(msg):
    open(result, "w", encoding="utf-8").write(msg)
    print(msg)


if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", user):
    say("Sorry, that username looks invalid, so I could not place a pixel.")
    sys.exit(0)

face, claimed = rp.load()
total = face["size"] ** 2
if any(c["user"].lower() == user.lower() for c in claimed):
    say(f"@{user} you already have a square in the portrait. One per person!")
    sys.exit(0)
if len(claimed) >= total:
    say("The portrait is complete, thank you all! No squares left.")
    sys.exit(0)

try:
    req = urllib.request.Request(f"https://github.com/{user}.png?size=64", headers={"User-Agent": "profile-pixel-bot"})
    raw = urllib.request.urlopen(req, timeout=30).read()
    img = Image.open(io.BytesIO(raw)).convert("RGB").resize((28, 28), Image.LANCZOS)
    buf = io.BytesIO()
    img.quantize(64).save(buf, "PNG", optimize=True)
    avatar = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
except Exception as e:  # network or image problem
    say(f"I could not download your GitHub photo ({e}). Close this issue and open a new one to retry.")
    sys.exit(0)

taken = {c["cell"] for c in claimed}
cell = random.Random(user.lower()).randrange(total)
while cell in taken:
    cell = (cell + 1) % total

claimed.append({"cell": cell, "user": user, "avatar": avatar})
json.dump(claimed, open(os.path.join(ROOT, "data", "claimed.json"), "w"), separators=(",", ":"))
open(os.path.join(ROOT, "assets", "puzzle.svg"), "w", encoding="utf-8").write(rp.render(face, claimed))
n = face["size"]
say(f"Done @{user}! Your photo is now square row {cell // n + 1}, column {cell % n + 1} of my face "
    f"({len(claimed)}/{total} placed). Refresh my profile in a minute to see it. Thank you!")
