"""Builds every picture on the profile from your real GitHub data (town, post, player, wrapped, inventory).
Usage:  python scripts/build_scene.py            (real data, needs GITHUB_TOKEN)
        python scripts/build_scene.py --demo     (fake data, for previews)
"""
import datetime as dt, json, math, os, random, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import profile_art as pa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER = os.environ.get("PROFILE_USER", "MadhavGarg98")
INK, PANEL, LINE, PAPER, MUTED = "#0b0a1a", "#12102a", "#2b2757", "#f1ede4", "#8e89b8"
ORANGE, VIOLET = "#ff7a45", "#8b7bff"
GOLD = "#ffd36b"
SANS = "Inter,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code',Consolas,'DejaVu Sans Mono',monospace"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
LANG = {"Java": "#ED8B00", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Python": "#3572A5",
        "C++": "#f34b7d", "HTML": "#e34c26", "CSS": "#8b5cf6", "Dart": "#00b4ab", "C": "#888888"}


# ------------------------------------------------------------------ data
def fetch():
    token = os.environ["GITHUB_TOKEN"]
    q = """query($login:String!){user(login:$login){
      followers{totalCount} following{totalCount}
      allRepos: repositories(privacy:PUBLIC,ownerAffiliations:OWNER){totalCount}
      contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount weekday}}}}
      repositories(first:12,privacy:PUBLIC,ownerAffiliations:OWNER,isFork:false,orderBy:{field:PUSHED_AT,direction:DESC}){
        nodes{name stargazerCount pushedAt diskUsage primaryLanguage{name}}}
      pinnedItems(first:6,types:REPOSITORY){nodes{... on Repository{name stargazerCount pushedAt primaryLanguage{name}}}}
      langRepos: repositories(first:100,privacy:PUBLIC,ownerAffiliations:OWNER,isFork:false){
        nodes{languages(first:6,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}}}"""
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": q, "variables": {"login": USER}}).encode(),
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                                          "User-Agent": "profile-scene"})
    u = json.load(urllib.request.urlopen(req, timeout=30))["data"]["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    raw_days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    days = [{"date": d["date"], "count": d["contributionCount"], "weekday": d["weekday"]} for d in raw_days]
    counts = [d["count"] for d in days]
    today = counts[-1]
    i = len(counts) - 1 if today > 0 else len(counts) - 2
    streak = 0
    while i >= 0 and counts[i] > 0:
        streak += 1; i -= 1
    repos = []
    for r in u["repositories"]["nodes"]:
        pushed = dt.datetime.fromisoformat(r["pushedAt"].replace("Z", "+00:00"))
        repos.append({"name": r["name"], "stars": r["stargazerCount"], "pushed": pushed,
                      "size": r["diskUsage"] or 1, "lang": (r["primaryLanguage"] or {}).get("name", "")})
    sizes = {}
    for rp in u["langRepos"]["nodes"]:
        for e in rp["languages"]["edges"]:
            sizes[e["node"]["name"]] = sizes.get(e["node"]["name"], 0) + e["size"]
    tot = sum(sizes.values()) or 1
    langs = sorted(((n, v * 100.0 / tot) for n, v in sizes.items()), key=lambda x: -x[1])[:6]
    pinned = []
    for r in u["pinnedItems"]["nodes"]:
        pinned.append({"name": r["name"], "stars": r["stargazerCount"], "lang": (r["primaryLanguage"] or {}).get("name", ""),
                       "pushed": dt.datetime.fromisoformat(r["pushedAt"].replace("Z", "+00:00"))})
    return {"repos_list": repos, "today": today, "streak": streak, "total": cal["totalContributions"],
            "repos": u["allRepos"]["totalCount"], "followers": u["followers"]["totalCount"],
            "following": u["following"]["totalCount"], "langs": langs, "days": days, "weeks": to_weeks(days), "pinned": pinned}


def to_weeks(days):
    weeks, cur = [], [None] * 7
    for i, d in enumerate(days):
        if d["weekday"] == 0 and i > 0:
            weeks.append(cur); cur = [None] * 7
        cur[d["weekday"]] = d["count"]
    weeks.append(cur)
    return weeks


def synthetic_calendar(total, seed=7):
    """Placeholder activity until the first real run; replaced by real data."""
    rnd = random.Random(seed)
    end = dt.datetime.now(IST).date()
    days = []
    for k in range(371):
        day = end - dt.timedelta(days=370 - k)
        wd = (day.weekday() + 1) % 7
        p = 0.07 if day < dt.date(end.year, 1, 1) else (0.55 if day.month in (2, 3, 8, 9) else 0.4)
        if wd in (0, 6): p *= 0.6
        c = 0
        if rnd.random() < p:
            c = 1 + int(rnd.expovariate(0.45))
        days.append({"date": day.isoformat(), "count": c, "weekday": wd})
    cur = sum(x["count"] for x in days)
    i = 0
    while cur != total and i < 5000:
        x = days[rnd.randrange(len(days))]
        if cur < total and x["count"] > 0: x["count"] += 1; cur += 1
        elif cur > total and x["count"] > 1: x["count"] -= 1; cur -= 1
        i += 1
    days[-1]["count"] = 0
    return days


def initial():
    """Honest placeholders taken from the profile page; replaced by the first workflow run."""
    d = demo(0, 0)
    now = dt.datetime.now(dt.timezone.utc)
    d["repos_list"] = [r for r in d["repos_list"] if r["name"] in ("salessaarthi", "Capstone_Coffee-Chat", "DocuQuery-AI", "Gym_Management_System")]
    d.update({"repos": 86, "followers": 3, "following": 5, "total": 693,
              "langs": [("JavaScript", 52.5), ("TypeScript", 17.6), ("Python", 9.8), ("Dart", 9.4), ("Assembly", 7.8), ("CSS", 3.0)]})
    d["days"] = synthetic_calendar(693); d["weeks"] = to_weeks(d["days"])
    d["pinned"] = [{"name": n, "stars": st, "lang": lg, "pushed": now - dt.timedelta(days=ago)} for n, st, lg, ago in [
        ("salessaarthi", 0, "JavaScript", 3), ("S85_Madhav_Capstone_Coffee-Chat", 1, "JavaScript", 40), ("S85_DocuQuery-AI", 1, "JavaScript", 60),
        ("S85_Gym_Management_System", 1, "JavaScript", 90), ("-Madhav_S85_Attendance_management_project", 1, "Java", 120), ("SAMBHAV", 0, "JavaScript", 20)]]
    return d


def demo(today=3, streak=2):
    now = dt.datetime.now(dt.timezone.utc)
    names = [("salessaarthi", "JavaScript", 2400, 1), ("Capstone_Coffee-Chat", "JavaScript", 900, 5),
             ("DocuQuery-AI", "Python", 600, 12), ("Gym_Management_System", "Java", 300, 40),
             ("dsa-practice", "C++", 120, 2), ("portfolio", "TypeScript", 1500, 9)]
    repos = [{"name": n, "stars": 1 if i == 1 else 0, "pushed": now - dt.timedelta(days=d), "size": s, "lang": l}
             for i, (n, l, s, d) in enumerate(names)]
    return {"repos_list": repos, "today": today, "streak": streak, "total": 410, "repos": 86, "followers": 3, "following": 5,
            "langs": [("JavaScript", 52.5), ("TypeScript", 17.6), ("Python", 9.8), ("Dart", 9.4), ("Assembly", 7.8)],
            "days": [], "weeks": [], "pinned": []}


# ------------------------------------------------------------------ pixel art helpers
PAL = {"H": "#17151f", "S": "#e9b58c", "K": "#2b2a36", "R": "#b3213b", "A": "#b3213b", "D": "#15141c", "P": "#d8c8a6"}
BASE = ["...HHHHHH...", "..HHHHHHHH..", "..HSSSSSSH..", "..KKKKKKKK..", "..SSSSSSSS..", "...SSSSSS...",
        "..RRDDDDRR..", ".ARRRDDRRRA.", ".ARRRDDRRRA.", ".ARRRRRRRRA.", ".SRRRRRRRRS.", "..PPPPPPPP..",
        "..PPP..PPP..", "..PPP..PPP..", "..DDD..DDD.."]
assert all(len(r) == 12 for r in BASE)


def sprite(rows, x0, y0, P=6):
    out = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch == ".":
                c += 1; continue
            c2 = c
            while c2 + 1 < len(row) and row[c2 + 1] == ch:
                c2 += 1
            out.append(f'<rect x="{x0 + c * P}" y="{y0 + r * P}" width="{(c2 - c + 1) * P}" height="{P}" fill="{PAL[ch]}"/>')
            c = c2 + 1
    return "".join(out)


def anim(attr, values, dur, begin=0, extra=""):
    return f'<animate attributeName="{attr}" values="{values}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite" {extra}/>'


def move(values, dur, begin=0):
    return f'<animateTransform attributeName="transform" type="translate" values="{values}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'


# ------------------------------------------------------------------ scene
def phase_of(h):
    if 5 <= h < 7: return "dawn"
    if 7 <= h < 17: return "day"
    if 17 <= h < 20: return "dusk"
    return "night"


SKY = {"day": ("#6db6ff", "#dff1ff"), "dawn": ("#2d2a63", "#ff9a6b"), "dusk": ("#3b2a70", "#ff7a45"), "night": ("#080920", "#211e52")}
BODY = {"day": "#4b4694", "dawn": "#37337f", "dusk": "#33307a", "night": "#1f1b4a"}
GROUND = {"day": "#2b2860", "dawn": "#1f1c4a", "dusk": "#1f1c4a", "night": "#100e2c"}


def build(data, now, state_override=None, phase_override=None):
    W, H = 1000, 470; GY = 400
    phase = phase_override or phase_of(now.hour)
    rnd = random.Random(now.strftime("%Y%m%d%H"))
    night = phase == "night"
    today, streak = data["today"], data["streak"]
    state = state_override or ("celebrate" if (streak >= 7 and today > 0) else "code" if today > 0 else "sleep")
    top, bot = SKY[phase]
    o = []

    # game HUD
    total = data["total"]; lvl = 1 + total // 40; xp = total % 40
    o.append(f'<rect width="{W}" height="96" fill="{INK}"/><line x1="0" y1="96" x2="{W}" y2="96" stroke="{LINE}" stroke-width="2"/>')
    o.append(f'<rect x="40" y="22" width="104" height="52" rx="10" fill="{ORANGE}"/><text x="92" y="42" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="800" letter-spacing="2" fill="{INK}">LEVEL</text>'
             f'<text x="92" y="66" text-anchor="middle" font-family="{MONO}" font-size="26" font-weight="800" fill="{INK}">{lvl}</text>')
    o.append(f'<text x="168" y="40" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{MUTED}">XP</text>'
             f'<rect x="196" y="28" width="260" height="16" rx="8" fill="{PANEL}" stroke="{LINE}"/><rect x="196" y="28" width="{max(6, 260 * xp / 40):.0f}" height="16" rx="8" fill="url(#hg)"/>'
             f'<text x="168" y="68" font-family="{MONO}" font-size="12" fill="{PAPER}">{xp} / 40 to level {lvl + 1}</text>')
    hearts = ""
    for k in range(7):
        full = k < min(streak, 7)
        hearts += (f'<g transform="translate({500 + k * 30} 24) scale(1.0)"><path d="M12 21s-7-4.5-9.5-9C.8 8.5 3 5 6.5 5c2 0 3.5 1 5.5 3 2-2 3.5-3 5.5-3C21 5 23.2 8.5 21.5 12 19 16.5 12 21 12 21z" '
                   f'fill="{ORANGE if full else "none"}" stroke="{ORANGE if full else LINE}" stroke-width="1.8"/></g>')
    o.append(hearts + f'<text x="500" y="68" font-family="{MONO}" font-size="12" fill="{PAPER}">{streak}-day streak, {today} today</text>')
    icon = ('<circle cx="0" cy="0" r="9" fill="#f4f1d8"/>' if night else f'<circle cx="0" cy="0" r="9" fill="{GOLD}"/>')
    o.append(f'<g transform="translate(930 36)">{icon}</g><text x="900" y="40" text-anchor="end" font-family="{MONO}" font-size="20" font-weight="800" fill="{PAPER}">{now.strftime("%H:%M")}</text>'
             f'<text x="960" y="68" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{MUTED}">IST  {phase.upper()}</text>')

    # sky
    o.append(f'<rect y="96" width="{W}" height="{GY-96}" fill="url(#sky)"/>')
    if night:
        for _ in range(70):
            x, y = rnd.randrange(10, 990), rnd.randrange(104, 330); s = rnd.choice([2, 2, 3])
            o.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="#fff" opacity="0.8">{anim("opacity", "0.9;0.15;0.9", rnd.uniform(2, 5), rnd.uniform(0, 3))}</rect>')
        o.append(f'<circle cx="880" cy="150" r="22" fill="#f4f1d8"/><circle cx="890" cy="143" r="20" fill="#080920" opacity="0.0"/>')
        o.append(f'<circle cx="871" cy="144" r="4" fill="#d9d5b0"/><circle cx="888" cy="158" r="3" fill="#d9d5b0"/>')
    else:
        sx, sy = {"day": (880, 150), "dawn": (160, 345), "dusk": (640, 350)}[phase]
        sun = "#fff2a8" if phase == "day" else "#ffd08a"
        o.append(f'<circle cx="{sx}" cy="{sy}" r="34" fill="{sun}" opacity="0.35"/><circle cx="{sx}" cy="{sy}" r="22" fill="{sun}"/>')
        cc = "#ffffff" if phase == "day" else "#e9c6c0"
        for k in range(4):
            cx, cy = rnd.randrange(40, 900), rnd.randrange(112, 220); w = rnd.choice([60, 84, 108])
            o.append(f'<g fill="{cc}" opacity="0.85" shape-rendering="crispEdges">{move(f"0 0;{rnd.choice([30,-30])} 0;0 0", rnd.uniform(40, 70))}'
                     f'<rect x="{cx}" y="{cy}" width="{w}" height="12"/><rect x="{cx+12}" y="{cy-12}" width="{w-30}" height="12"/><rect x="{cx+w//3}" y="{cy-22}" width="{w//3}" height="10"/></g>')

    # ground
    o.append(f'<rect y="{GY}" width="{W}" height="{H-GY}" fill="{GROUND[phase]}"/><rect y="{GY}" width="{W}" height="6" fill="{LINE}"/>')

    # buildings
    repos = data["repos_list"][:9]
    bx = 34
    for r in repos:
        w = 58
        h = int(54 + min(120, math.log(r["size"] + 1) * 14))
        top_y = GY - h
        age = (now.astimezone(dt.timezone.utc) - r["pushed"]).total_seconds() / 86400
        frac = 0.9 if age < 1.5 else 0.6 if age < 7 else 0.3 if age < 30 else 0.0
        rows = max(1, (h - 26) // 22); total_w = rows * 2; lit = round(total_w * frac)
        roof = LANG.get(r["lang"], VIOLET)
        o.append(f'<rect x="{bx}" y="{top_y}" width="{w}" height="{h}" fill="{BODY[phase]}" stroke="{LINE}"/>')
        o.append(f'<rect x="{bx-3}" y="{top_y-8}" width="{w+6}" height="8" fill="{roof}"/>')
        k = 0
        for rr in range(rows):
            for cc in range(2):
                wx, wy = bx + 11 + cc * 24, top_y + 14 + rr * 22
                on = k < lit
                fill = "#ffd36b" if on else "#15132f"
                op = (1 if night else 0.75) if on else 0.9
                glow = f'<rect x="{wx-3}" y="{wy-3}" width="20" height="22" fill="#ffd36b" opacity="0.18"/>' if on and night else ""
                o.append(f'{glow}<rect x="{wx}" y="{wy}" width="14" height="16" fill="{fill}" opacity="{op}"/>')
                k += 1
        if r["stars"]:
            o.append(f'<text x="{bx+w/2}" y="{top_y-14}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="#ffd36b">&#9733;{r["stars"]}</text>')
        name = r["name"].replace("S85_", "")
        name = name.replace("-", "").replace("_", " ").strip()
        name = name if len(name) <= 9 else name[:8] + "…"
        ly = GY + 22 + (14 if repos.index(r) % 2 else 0)
        o.append(f'<text x="{bx+w/2}" y="{ly}" text-anchor="middle" font-family="{MONO}" font-size="10.5" font-weight="700" fill="{PAPER}" opacity="0.9">{name.replace("&","&amp;")}</text>')
        bx += 66
    # lamps
    for lx in (bx + 4, 676):
        o.append(f'<rect x="{lx}" y="{GY-46}" width="4" height="46" fill="{LINE}"/><rect x="{lx-5}" y="{GY-52}" width="14" height="8" fill="#ffd36b" opacity="{1 if night else 0.35}"/>')
        if night:
            o.append(f'<rect x="{lx-14}" y="{GY-56}" width="32" height="16" fill="#ffd36b" opacity="0.12"/>')

    # ---------------- home room with Madhav
    RX0, RX1, RY0 = 704, 964, 232; FLOOR = GY - 8
    o.append(f'<rect x="{RX0}" y="{RY0}" width="{RX1-RX0}" height="{GY-RY0}" fill="#1b1842" stroke="{LINE}" stroke-width="2"/>')
    o.append(f'<rect x="{RX0}" y="{FLOOR}" width="{RX1-RX0}" height="8" fill="#2d2864"/>')
    o.append(f'<rect x="{RX0+14}" y="{RY0+16}" width="46" height="36" fill="#0b0a1a" stroke="{LINE}"/><rect x="{RX0+14}" y="{RY0+16}" width="46" height="36" fill="url(#sky)" opacity="0.9"/>')
    msg, mood = {"code": (f"Coding now: {today} commit{'s' if today != 1 else ''} today", ORANGE),
                 "celebrate": (f"{streak}-day streak, on fire!", ORANGE),
                 "sleep": ("Resting: no commits yet today", VIOLET)}[state]

    if state == "code":
        x0, y0 = 840, 300
        o.append(sprite(BASE[:7] + [BASE[7].replace("A", "R"), BASE[8].replace("A", "R"), BASE[9].replace("A", "R"), BASE[10].replace("S", "R")], x0, y0))
        o.append(f'<rect x="736" y="358" width="188" height="8" fill="#6a4f8f"/><rect x="744" y="366" width="172" height="{FLOOR-366}" fill="#4a3770"/>')
        o.append(f'<rect x="752" y="298" width="76" height="52" rx="3" fill="#0d0c22" stroke="{LINE}" stroke-width="2"/><rect x="786" y="350" width="8" height="8" fill="{LINE}"/>')
        for i in range(6):
            wdt = rnd.choice([18, 30, 42, 24, 36, 50]); col = rnd.choice([ORANGE, VIOLET, PAPER])
            o.append(f'<rect x="{758 + (6 if i % 3 == 1 else 0)}" y="{305 + i * 7}" width="{wdt}" height="3" fill="{col}">{anim("opacity", "0.2;1;1", rnd.uniform(1.4, 2.6), rnd.uniform(0, 1.5))}</rect>')
        o.append(f'<rect x="{x0-2}" y="350" width="76" height="8" rx="2" fill="#23213f"/>')
        o.append(f'<rect x="{x0+6}" y="343" width="12" height="8" fill="{PAL["S"]}">{move("0 0;0 3;0 0", 0.35)}</rect>')
        o.append(f'<rect x="{x0+54}" y="343" width="12" height="8" fill="{PAL["S"]}">{move("0 3;0 0;0 3", 0.35)}</rect>')
    elif state == "celebrate":
        x0, y0 = 800, FLOOR - 90
        body = [r.replace("A", "R").replace("S", "S") if i in (7, 8, 9) else r for i, r in enumerate(BASE)]
        body[10] = ".RRRRRRRRRR."
        o.append(f'<g>{move("0 0;0 -12;0 0", 0.7)}{sprite(body, x0, y0)}'
                 f'<rect x="{x0-2}" y="{y0-6}" width="12" height="12" fill="{PAL["S"]}"/><rect x="{x0}" y="{y0+6}" width="8" height="30" fill="#b3213b"/>'
                 f'<rect x="{x0+62}" y="{y0-6}" width="12" height="12" fill="{PAL["S"]}"/><rect x="{x0+64}" y="{y0+6}" width="8" height="30" fill="#b3213b"/></g>')
        for i in range(16):
            cx = rnd.randrange(RX0 + 10, RX1 - 10); col = rnd.choice([ORANGE, VIOLET, "#ffd36b", PAPER])
            o.append(f'<rect x="{cx}" y="{RY0}" width="5" height="5" fill="{col}"><animate attributeName="y" values="{RY0};{FLOOR}" dur="{rnd.uniform(2, 4):.1f}s" begin="{rnd.uniform(0, 3):.1f}s" repeatCount="indefinite"/></rect>')
    else:
        o.append(f'<rect x="{RX0+22}" y="330" width="12" height="{FLOOR-330}" fill="#6a4f8f"/><rect x="{RX0+22}" y="{FLOOR-22}" width="226" height="22" fill="#6a4f8f"/>')
        o.append(f'<rect x="{RX0+40}" y="346" width="64" height="22" rx="4" fill="{PAPER}"/>')
        head = BASE[:3] + ["..SDDSSDDS..", "..SSSSSSSS..", "...SSSSSS..."]
        o.append(sprite(head, RX0 + 44, 330))
        o.append(f'<rect x="{RX0+36}" y="364" width="212" height="{FLOOR-364}" fill="#b3213b"/><rect x="{RX0+36}" y="372" width="212" height="5" fill="#d8465f"/>')
        for k, (zx, zs) in enumerate([(0, 14), (14, 18), (30, 22)]):
            o.append(f'<text x="{RX0+130+zx}" y="326" font-family="{MONO}" font-size="{zs}" font-weight="700" fill="{VIOLET}" opacity="0">z'
                     f'{anim("opacity", "0;1;0", 3, k)}<animateTransform attributeName="transform" type="translate" values="0 0;8 -22" dur="3s" begin="{k}s" repeatCount="indefinite"/></text>')
    bw = len(msg) * 7.4 + 26; bxx = (RX0 + RX1) / 2 - bw / 2
    o.append(f'<g><rect x="{bxx:.0f}" y="190" width="{bw:.0f}" height="32" rx="8" fill="{PAPER}"/><path d="M{(RX0+RX1)/2-8:.0f} 222h16l-8 10z" fill="{PAPER}"/>'
             f'<text x="{(RX0+RX1)/2:.0f}" y="211" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="700" fill="{INK}">{msg}</text></g>')

    o.append(f'<text x="{RX1-12}" y="{RY0+22}" text-anchor="end" font-family="{MONO}" font-size="11" letter-spacing="2" fill="{MUTED}">MY ROOM, LIVE</text>')
    # legend: how to read the town
    LXP, LYP = 24, 110
    o.append(f'<rect x="{LXP}" y="{LYP}" width="318" height="100" rx="12" fill="{INK}" opacity="0.9"/>'
             f'<text x="{LXP+16}" y="{LYP+22}" font-family="{MONO}" font-size="11" letter-spacing="2" fill="{ORANGE}" font-weight="800">HOW TO READ THIS TOWN</text>'
             f'<rect x="{LXP+18}" y="{LYP+34}" width="12" height="16" fill="{BODY[phase]}" stroke="{PAPER}" stroke-width="1"/>'
             f'<text x="{LXP+44}" y="{LYP+47}" font-family="{SANS}" font-size="12.5" fill="{PAPER}">Each building is one of my repos</text>'
             f'<rect x="{LXP+14}" y="{LYP+62}" width="8" height="10" fill="{BODY[phase]}" stroke="{PAPER}" stroke-width="1"/><rect x="{LXP+25}" y="{LYP+56}" width="8" height="16" fill="{BODY[phase]}" stroke="{PAPER}" stroke-width="1"/>'
             f'<text x="{LXP+44}" y="{LYP+70}" font-family="{SANS}" font-size="12.5" fill="{PAPER}">Taller building means a bigger repo</text>'
             f'<rect x="{LXP+18}" y="{LYP+80}" width="10" height="12" fill="#ffd36b"/>'
             f'<text x="{LXP+44}" y="{LYP+90}" font-family="{SANS}" font-size="12.5" fill="{PAPER}">Lit window means I pushed code recently</text>')
    # caption
    o.append(f'<text x="40" y="{H-14}" font-family="{MONO}" font-size="12" fill="{MUTED}">Live from my GitHub. The sky follows India time, and my character codes when I commit.</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Pixel town built from Madhav's GitHub activity. Madhav is {'celebrating a streak' if state=='celebrate' else 'coding' if state=='code' else 'sleeping'}.">
<defs><linearGradient id="hg" x1="0" x2="1"><stop offset="0" stop-color="{ORANGE}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{ORANGE}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></linearGradient>
<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>
<g clip-path="url(#card)" shape-rendering="crispEdges">{"".join(o)}</g>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{LINE}"/>
</svg>'''
    return svg


def main():
    now = dt.datetime.now(IST)
    if "--demo" in sys.argv:
        data = initial(); data["today"], data["streak"] = 3, 2
    elif "--initial" in sys.argv:
        data = initial()
    else:
        try:
            data = fetch()
        except Exception as e:  # never break the profile because of an API hiccup
            print("GitHub API failed, keeping the old pictures:", e)
            sys.exit(0)
    out = os.path.join(ROOT, "assets")
    os.makedirs(out, exist_ok=True)
    files = {"scene.svg": build(data, now), "instagram.svg": pa.instagram(data), "player.svg": pa.player(data),
             "wrapped.svg": pa.wrapped(data), "projects.svg": pa.projects(data), "inventory.svg": pa.inventory(data),
             "daily.svg": pa.daily(data, now), "snake.svg": pa.snake(data)}
    for name, svg in files.items():
        open(os.path.join(out, name), "w", encoding="utf-8").write(svg)
    print("wrote", ", ".join(files), "| today:", data["today"], "streak:", data["streak"], "total:", data["total"])


if __name__ == "__main__":
    main()
