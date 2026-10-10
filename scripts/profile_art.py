"""All profile pictures: Instagram-style post, Spotify-style player, Wrapped, projects row,
inventory, daily quests and the contribution snake."""
import base64, datetime as dt, hashlib, json, math, os, textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INK, PANEL, LINE, PAPER, MUTED = "#0b0a1a", "#12102a", "#2b2757", "#f1ede4", "#8e89b8"
ORANGE, VIOLET = "#ff7a45", "#8b7bff"
ICE, GOLD, MINT = "#7dd3fc", "#ffd36b", "#6ee7b7"
SANS = "Inter,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code',Consolas,'DejaVu Sans Mono',monospace"
HEART = "M12 21s-7-4.5-9.5-9C.8 8.5 3 5 6.5 5c2 0 3.5 1 5.5 3 2-2 3.5-3 5.5-3C21 5 23.2 8.5 21.5 12 19 16.5 12 21 12 21z"
LOGOS = json.load(open(os.path.join(ROOT, "data", "logos.json")))


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;")


def b64(name, mime):
    return f"data:{mime};base64," + base64.b64encode(open(os.path.join(ROOT, "data", name), "rb").read()).decode()


def anim(attr, pts, T, extra=""):
    pts = sorted(pts, key=lambda p: p[0])
    if pts[0][0] > 0: pts.insert(0, (0, pts[0][1]))
    if pts[-1][0] < T: pts.append((T, pts[-1][1]))
    kt = ";".join(f"{min(p[0] / T, 1):.4f}" for p in pts)
    vs = ";".join(str(p[1]) for p in pts)
    return f'<animate attributeName="{attr}" dur="{T}s" repeatCount="indefinite" keyTimes="{kt}" values="{vs}" {extra}/>'


def frame(W, H, inner, defs=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>{defs}
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{LINE}"/></pattern>
<linearGradient id="grad" x1="0" x2="1"><stop offset="0" stop-color="{ORANGE}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>
<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{INK}"/><rect width="{W}" height="{H}" fill="url(#dots)" opacity="0.5"/>{inner}</g>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{LINE}"/>
</svg>'''


# ------------------------------------------------------------------ derived stats
def calc(d):
    days = d["days"]
    counts = [x["count"] for x in days]
    active = sum(1 for c in counts if c > 0)
    best = cur = 0
    for c in counts:
        cur = cur + 1 if c > 0 else 0
        best = max(best, cur)
    top = max(days, key=lambda x: x["count"])
    months = {}
    for x in days:
        months[x["date"][:7]] = months.get(x["date"][:7], 0) + x["count"]
    keys = sorted(months)[-12:]
    monthly = [(k, months[k]) for k in keys]
    return {"active": active, "longest": best, "busiest": top, "monthly": monthly}


# =================================================================== INSTAGRAM-STYLE POST
def instagram(d):
    W, H, PX = 1000, 640, 640
    p1, p2, av = b64("photo1.jpg", "image/jpeg"), b64("photo2.jpg", "image/jpeg"), b64("avatar.jpg", "image/jpeg")
    T = 12.0
    slide = f'<animateTransform attributeName="transform" type="translate" dur="{T}s" repeatCount="indefinite" keyTimes="0;0.4;0.45;0.9;0.95;1" values="0 0;0 0;-640 0;-640 0;0 0;0 0"/>'
    o = [f'<clipPath id="ph"><rect x="0" y="0" width="{PX}" height="{H}"/></clipPath><g clip-path="url(#ph)"><g>{slide}',
         f'<image href="{p1}" x="0" y="0" width="{PX}" height="{H}" preserveAspectRatio="xMidYMid slice"/>',
         f'<image href="{p2}" x="{PX}" y="0" width="{PX}" height="{H}" preserveAspectRatio="xMidYMid slice"/>',
         f'<g transform="translate(330 352)"><path d="M-6 0h12l-6 -8z" fill="#000" opacity="0.75"/><rect x="-62" y="0" width="124" height="26" rx="7" fill="#000" opacity="0.75"/>'
         f'<text x="0" y="17.5" text-anchor="middle" font-family="{SANS}" font-size="12" font-weight="600" fill="#fff">madhavgarg98</text></g></g>',
         f'<g transform="translate(320 300)" opacity="0"><g><animateTransform attributeName="transform" type="scale" dur="{T}s" begin="1.2s" repeatCount="indefinite" '
         f'keyTimes="0;0.03;0.06;0.11;1" values="0;1.25;1;1.5;1.5"/><path d="{HEART}" transform="translate(-60 -60) scale(5)" fill="#fff"/></g>'
         f'<animate attributeName="opacity" dur="{T}s" begin="1.2s" repeatCount="indefinite" keyTimes="0;0.03;0.08;0.11;1" values="0;0.95;0.95;0;0"/></g></g>']
    for i in range(2):
        pts = [(0, 1), (T * 0.4, 1), (T * 0.45, 0.4), (T * 0.9, 0.4), (T * 0.95, 1)] if i == 0 else [(0, 0.4), (T * 0.4, 0.4), (T * 0.45, 1), (T * 0.9, 1), (T * 0.95, 0.4)]
        o.append(f'<circle cx="{320 + (i - 0.5) * 16}" cy="{H - 22}" r="3.5" fill="#fff" opacity="0.4">{anim("opacity", pts, T)}</circle>')
    # right panel
    o.append(f'<rect x="{PX}" y="0" width="{W-PX}" height="{H}" fill="{PANEL}"/><line x1="{PX}" y1="0" x2="{PX}" y2="{H}" stroke="{LINE}"/>')
    acx, acy = PX + 38, 38
    o.append(f'<clipPath id="av"><circle cx="{acx}" cy="{acy}" r="20"/></clipPath>'
             f'<g><animateTransform attributeName="transform" type="rotate" from="0 {acx} {acy}" to="360 {acx} {acy}" dur="8s" repeatCount="indefinite"/>'
             f'<circle cx="{acx}" cy="{acy}" r="25" fill="none" stroke="url(#grad)" stroke-width="3" stroke-dasharray="52 9"/></g>'
             f'<circle cx="{acx}" cy="{acy}" r="21" fill="{PANEL}"/><image href="{av}" x="{acx-20}" y="{acy-20}" width="40" height="40" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>')
    o.append(f'<text x="{PX+78}" y="33" font-family="{SANS}" font-size="15" font-weight="700" fill="{PAPER}">madhavgarg98</text>'
             f'<text x="{PX+78}" y="52" font-family="{SANS}" font-size="12" fill="{MUTED}">{d["repos"]} repos · {d["followers"]} followers · {d["following"]} following</text>'
             f'<text x="{W-26}" y="42" text-anchor="end" font-family="{SANS}" font-size="20" font-weight="700" fill="{PAPER}">···</text>'
             f'<line x1="{PX}" y1="76" x2="{W}" y2="76" stroke="{LINE}"/>')
    cap = "CS student mastering DSA and backend development. Building with Java, Python and the MERN stack, one project at a time."
    y = 102
    for i, ln in enumerate(textwrap.wrap("madhavgarg98 " + cap, 40)):
        if i == 0:
            o.append(f'<text x="{PX+20}" y="{y}" font-family="{SANS}" font-size="13.5" fill="{PAPER}"><tspan font-weight="700">madhavgarg98 </tspan>{esc(ln[13:])}</text>')
        else:
            o.append(f'<text x="{PX+20}" y="{y}" font-family="{SANS}" font-size="13.5" fill="{PAPER}">{esc(ln)}</text>')
        y += 19
    o.append(f'<text x="{PX+20}" y="{y+4}" font-family="{SANS}" font-size="13.5" fill="{VIOLET}">#DSA #Java #Python #MERN #OpenSource</text>')
    comments = ["Looking to team up on beginner-friendly open source, college tech projects and learning hackathons.",
                "Levelling up: DSA optimization, system design fundamentals and clean code habits.",
                "Ask me about MongoDB, Java fundamentals and the MERN stack. Happy to explain.",
                "I turn complex CS ideas into simple explanations, and I don't give up easily."]
    cy = y + 30
    for i, c in enumerate(comments):
        t = 0.4 + i * 0.7
        g = [f'<circle cx="{PX+32}" cy="{cy+8}" r="12" fill="url(#grad)"/><text x="{PX+32}" y="{cy+12.5}" text-anchor="middle" font-family="{SANS}" font-size="11" font-weight="800" fill="{INK}">M</text>']
        yy = cy + 5
        for j, ln in enumerate(textwrap.wrap("madhavgarg98 " + c, 41)):
            if j == 0:
                g.append(f'<text x="{PX+54}" y="{yy}" font-family="{SANS}" font-size="13" fill="{PAPER}"><tspan font-weight="700">madhavgarg98 </tspan>{esc(ln[13:])}</text>')
            else:
                g.append(f'<text x="{PX+54}" y="{yy}" font-family="{SANS}" font-size="13" fill="{PAPER}">{esc(ln)}</text>')
            yy += 17
        g.append(f'<text x="{PX+54}" y="{yy+3}" font-family="{SANS}" font-size="11" fill="{MUTED}">{i+1}d    Reply</text>')
        o.append(f'<g opacity="0">{"".join(g)}<animate attributeName="opacity" values="0;1" dur="0.5s" begin="{t:.1f}s" fill="freeze"/></g>')
        cy += 68
    ay = 490
    st = 'fill="none" stroke="#f1ede4" stroke-width="1.8" stroke-linejoin="round"'
    o.append(f'<line x1="{PX}" y1="{ay}" x2="{W}" y2="{ay}" stroke="{LINE}"/>'
             f'<g transform="translate({PX+18} {ay+10}) scale(1.1)"><path d="{HEART}" fill="{ORANGE}"/></g>'
             f'<g transform="translate({PX+56} {ay+10}) scale(1.1)" {st}><path d="M4 4h16v12H9l-5 4z"/></g>'
             f'<g transform="translate({PX+94} {ay+10}) scale(1.1)" {st}><path d="M3 11L21 3l-6 18-3-8z"/></g>'
             f'<g transform="translate({W-48} {ay+10}) scale(1.1)" {st}><path d="M6 3h12v18l-6-4-6 4z"/></g>'
             f'<text x="{PX+20}" y="{ay+56}" font-family="{SANS}" font-size="13.5" fill="{PAPER}"><tspan font-weight="700">{d["total"]} contributions</tspan> in the last year</text>'
             f'<text x="{PX+20}" y="{ay+74}" font-family="{SANS}" font-size="10.5" letter-spacing="0.8" fill="{MUTED}">{d["streak"]}-DAY STREAK  ·  {d["today"]} TODAY</text>'
             f'<line x1="{PX}" y1="{ay+88}" x2="{W}" y2="{ay+88}" stroke="{LINE}"/>'
             f'<text x="{PX+20}" y="{ay+118}" font-family="{SANS}" font-size="13.5" fill="{MUTED}">Say hi, the links are just below</text>'
             f'<text x="{W-24}" y="{ay+118}" text-anchor="end" font-family="{SANS}" font-size="13.5" font-weight="700" fill="{ORANGE}">Post</text>')
    return frame(W, H, "".join(o))


# =================================================================== SPOTIFY-STYLE PLAYER
LYRICS = [("label", "INTRO"), ("line", "Hi, I'm Madhav, glad you came"),
          ("label", "VERSE 1"), ("line", "CS student, learning every day"), ("line", "DSA is how I find my way"),
          ("line", "Java and Python in my hands"), ("line", "Backend dreams, MERN stack plans"),
          ("label", "CHORUS"), ("line", "Open to collab, beginner-friendly"), ("line", "Hackathons and projects with me"),
          ("line", "Ask me MongoDB, ask me Java"), ("line", "I make the complex simple, see"),
          ("label", "OUTRO"), ("line", "I don't give up, I recompile"), ("line", "Commit by commit, I ship my best")]


def player(d):
    W, H = 1000, 604
    T = 45.0
    o = [f'<text x="48" y="48" font-family="{MONO}" font-size="11" letter-spacing="3" fill="{MUTED}">PLAYING FROM PLAYLIST</text>',
         f'<text x="48" y="70" font-family="{SANS}" font-size="16" font-weight="800" fill="{PAPER}">Madhav\'s Build Log</text>']
    cx = cy = 170
    art = [f'<g transform="translate(48 92)"><rect width="340" height="340" rx="14" fill="url(#cover)"/><circle cx="{cx}" cy="{cy}" r="96" fill="{INK}" opacity="0.92"/>']
    for k in range(36):
        a = k * math.pi * 2 / 36; c, s = math.cos(a), math.sin(a)
        l1, l2 = 8 + (k * 7) % 22, 22 + (k * 11) % 26
        x1, y1 = cx + c * 106, cy + s * 106
        xa, ya = cx + c * (106 + l1), cy + s * (106 + l1); xb, yb = cx + c * (106 + l2), cy + s * (106 + l2)
        du = 0.9 + (k % 5) * 0.25
        art.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{xa:.1f}" y2="{ya:.1f}" stroke="{PAPER}" stroke-width="4" stroke-linecap="round" opacity="0.9">'
                   f'<animate attributeName="x2" values="{xa:.1f};{xb:.1f};{xa:.1f}" dur="{du:.2f}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="y2" values="{ya:.1f};{yb:.1f};{ya:.1f}" dur="{du:.2f}s" repeatCount="indefinite"/></line>')
    art.append(f'<text x="{cx}" y="{cy+22}" text-anchor="middle" font-family="{MONO}" font-size="64" font-weight="800" fill="{PAPER}">MG</text>'
               f'<text x="22" y="322" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{INK}" font-weight="700">MADHAV GARG</text>'
               f'<text x="318" y="322" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{INK}" font-weight="700">VOL. 1</text></g>')
    o.append("".join(art))
    o.append(f'<text x="48" y="474" font-family="{SANS}" font-size="30" font-weight="800" fill="{PAPER}">Learning DSA</text>'
             f'<text x="48" y="500" font-family="{SANS}" font-size="15" fill="{MUTED}">Madhav Garg  ·  CS Student Era  ·  2026</text>'
             f'<g transform="translate(362 456) scale(1.15)"><path d="{HEART}" fill="{ORANGE}"/></g>')
    o.append(f'<rect x="48" y="520" width="340" height="4" rx="2" fill="{LINE}"/>'
             f'<rect x="48" y="520" width="0" height="4" rx="2" fill="{PAPER}"><animate attributeName="width" values="0;340" dur="{T}s" repeatCount="indefinite"/></rect>'
             f'<circle cx="48" cy="522" r="6" fill="{PAPER}"><animate attributeName="cx" values="48;388" dur="{T}s" repeatCount="indefinite"/></circle>')
    for s_ in range(int(T)):
        o.append(f'<text x="48" y="544" font-family="{MONO}" font-size="11" fill="#c9c4ec" opacity="0">0:{s_:02d}'
                 f'{anim("opacity", [(0, 0), (s_, 0), (s_ + 0.01, 1), (s_ + 0.99, 1), (s_ + 1, 0)], T)}</text>')
    o.append(f'<text x="388" y="544" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">0:{int(T)}</text>')
    cyc = 574
    o.append(f'<g fill="none" stroke="{MUTED}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
             f'<g transform="translate(58 {cyc-9}) scale(0.75)"><path d="M3 7h4l10 10h4M3 17h4l3-3M14 10l3-3h4M18 4l3 3-3 3M18 14l3 3-3 3"/></g>'
             f'<g transform="translate(356 {cyc-9}) scale(0.75)"><path d="M4 12V9a3 3 0 013-3h12M16 3l3 3-3 3M20 12v3a3 3 0 01-3 3H5M8 15l-3 3 3 3"/></g></g>'
             f'<g fill="{PAPER}"><path d="M141 {cyc-9}l-14 9 14 9z"/><rect x="118" y="{cyc-9}" width="3" height="18"/><path d="M296 {cyc-9}l14 9-14 9z"/><rect x="311" y="{cyc-9}" width="3" height="18"/></g>'
             f'<circle cx="218" cy="{cyc}" r="19" fill="{PAPER}"/><rect x="210" y="{cyc-8}" width="5" height="16" rx="1" fill="{INK}"/><rect x="221" y="{cyc-8}" width="5" height="16" rx="1" fill="{INK}"/>')
    # lyrics panel
    LX, LY, LW, LH = 440, 92, 512, 492
    o.append(f'<rect x="{LX}" y="{LY}" width="{LW}" height="{LH}" rx="16" fill="url(#lyr)"/>')
    o.append(f'<text x="{LX+32}" y="{LY+40}" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{MUTED}">LYRICS</text>')
    for k in range(4):
        h1, h2 = 6 + k * 3, 18 - k * 2
        o.append(f'<rect x="{LX+LW-72+k*11}" y="{LY+40-h1}" width="6" height="{h1}" rx="2" fill="{ORANGE}">'
                 f'<animate attributeName="height" values="{h1};{h2};{h1}" dur="{0.6+k*0.17:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="y" values="{LY+40-h1};{LY+40-h2};{LY+40-h1}" dur="{0.6+k*0.17:.2f}s" repeatCount="indefinite"/></rect>')
    # positions
    ypos, y_ = [], 0
    for kind, _ in LYRICS:
        ypos.append(y_); y_ += 30 if kind == "label" else 48
    lines_idx = [i for i, (k, _) in enumerate(LYRICS) if k == "line"]
    slot = T / len(lines_idx); CY = 290  # active line sits here
    pts = []
    for n, li in enumerate(lines_idx):
        t0 = n * slot
        ty = CY - ypos[li]
        pts += [(max(t0 - 0.0, 0), ty), (t0 + slot - 0.5, ty)]
    # make scroll smooth between holds
    scroll = f'<animateTransform attributeName="transform" type="translate" dur="{T}s" repeatCount="indefinite" calcMode="linear" keyTimes="{";".join(f"{min(p[0]/T,1):.4f}" for p in pts + [(T, pts[-1][1])])}" values="{";".join(f"0 {p[1]}" for p in pts + [(T, pts[-1][1])])}"/>'
    o.append(f'<clipPath id="lc"><rect x="{LX}" y="{LY+58}" width="{LW}" height="{LH-124}"/></clipPath><g clip-path="url(#lc)"><g>{scroll}')
    for i, (kind, txt) in enumerate(LYRICS):
        y = ypos[i]
        if kind == "label":
            o.append(f'<text x="{LX+32}" y="{y+6}" font-family="{MONO}" font-size="11" letter-spacing="3" fill="{ORANGE}" opacity="0.8">{txt}</text>')
        else:
            n = lines_idx.index(i)
            ops = []
            for m in range(len(lines_idx)):
                dist = abs(m - n); ops.append(1 if dist == 0 else 0.5 if dist == 1 else 0.28)
            apts = []
            for m, v in enumerate(ops):
                apts += [(m * slot + 0.4 if m else 0, v), ((m + 1) * slot, v)]
            o.append(f'<text x="{LX+32}" y="{y+22}" font-family="{SANS}" font-size="23" font-weight="800" fill="{PAPER}" opacity="{ops[0]}">{esc(txt)}{anim("opacity", apts, T)}</text>')
    o.append('</g></g>')
    o.append(f'<line x1="{LX+32}" y1="{LY+LH-52}" x2="{LX+LW-32}" y2="{LY+LH-52}" stroke="{LINE}"/>'
             f'<text x="{LX+32}" y="{LY+LH-26}" font-family="{SANS}" font-size="12" fill="{MUTED}">Written, produced and mixed by Madhav Garg  ·  Powered by curiosity</text>')
    defs = (f'<linearGradient id="cover" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{VIOLET}"/><stop offset="1" stop-color="{ORANGE}"/></linearGradient>'
            f'<linearGradient id="lyr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a2468"/><stop offset="1" stop-color="{PANEL}"/></linearGradient>')
    return frame(W, H, "".join(o), defs)


# =================================================================== WRAPPED
def wrapped(d):
    W, H = 1000, 540
    s = calc(d)
    b = s["busiest"]
    o = [f'<text x="48" y="66" font-family="{SANS}" font-size="40" font-weight="800" letter-spacing="-1" fill="url(#grad)">Madhav Wrapped</text>',
         f'<text x="48" y="92" font-family="{SANS}" font-size="14" fill="{MUTED}">My last 12 months on GitHub, straight from the data</text>',
         f'<text x="952" y="62" text-anchor="end" font-family="{SANS}" font-size="17" font-weight="800" fill="{PAPER}">This year: DSA, backend</text>',
         f'<text x="952" y="86" text-anchor="end" font-family="{SANS}" font-size="17" font-weight="800" fill="url(#grad)">and the MERN stack.</text>']
    tiles = [(ORANGE, d["total"], "contributions"), (VIOLET, s["active"], "days I showed up"),
             (PAPER, s["longest"], "day longest streak"), (ICE, b["count"], f'on my busiest day ({b["date"][5:]})')]
    for i, (bg, big, small) in enumerate(tiles):
        x = 48 + i * 230
        o.append(f'<g opacity="0"><rect x="{x}" y="116" width="214" height="136" rx="16" fill="{bg}"/>'
                 f'<text x="{x+20}" y="190" font-family="{SANS}" font-size="68" font-weight="900" letter-spacing="-3" fill="{INK}">{big}</text>'
                 f'<text x="{x+20}" y="228" font-family="{SANS}" font-size="14" font-weight="700" fill="{INK}">{esc(small)}</text>'
                 f'<animate attributeName="opacity" values="0;1" dur="0.5s" begin="{0.2+i*0.2:.2f}s" fill="freeze"/></g>')
    # languages
    o.append(f'<rect x="48" y="276" width="448" height="240" rx="16" fill="{PANEL}" stroke="{LINE}"/>'
             f'<text x="72" y="312" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{MUTED}">TOP LANGUAGES</text>')
    langs = d["langs"][:5]; top = max(p for _, p in langs) or 1
    for i, (name, pct) in enumerate(langs):
        y = 346 + i * 33; bw = 190 * pct / top
        o.append(f'<text x="72" y="{y+5}" font-family="{MONO}" font-size="17" font-weight="800" fill="{ORANGE}">{i+1}</text>'
                 f'<text x="100" y="{y+5}" font-family="{SANS}" font-size="15" font-weight="700" fill="{PAPER}">{esc(name)}</text>'
                 f'<rect x="228" y="{y-6}" width="190" height="12" rx="6" fill="{INK}"/>'
                 f'<rect x="228" y="{y-6}" width="0" height="12" rx="6" fill="url(#grad)"><animate attributeName="width" values="0;{bw:.1f}" dur="1.2s" begin="{0.6+i*0.15:.2f}s" fill="freeze"/></rect>'
                 f'<text x="430" y="{y+5}" font-family="{MONO}" font-size="12" fill="{MUTED}">{pct:.1f}%</text>')
    # months
    o.append(f'<rect x="512" y="276" width="440" height="240" rx="16" fill="{PANEL}" stroke="{LINE}"/>'
             f'<text x="536" y="312" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{MUTED}">MY YEAR BY MONTH</text>')
    mon = s["monthly"]; mx = max(v for _, v in mon) or 1; peak = max(mon, key=lambda x: x[1])
    names = "JFMAMJJASOND"
    o.append(f'<text x="928" y="312" text-anchor="end" font-family="{MONO}" font-size="12" fill="{ORANGE}">peak: {dt.date(int(peak[0][:4]), int(peak[0][5:]), 1).strftime("%b")}, {peak[1]}</text>')
    for i, (k, v) in enumerate(mon):
        x = 540 + i * 33; h = max(3, 120 * v / mx); y0 = 484
        col = ORANGE if (k, v) == peak else VIOLET
        o.append(f'<rect x="{x}" y="{y0}" width="22" height="0" rx="5" fill="{col}"><animate attributeName="height" values="0;{h:.1f}" dur="0.8s" begin="{0.8+i*0.07:.2f}s" fill="freeze"/>'
                 f'<animate attributeName="y" values="{y0};{y0-h:.1f}" dur="0.8s" begin="{0.8+i*0.07:.2f}s" fill="freeze"/></rect>'
                 f'<text x="{x+11}" y="504" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">{names[int(k[5:]) - 1]}</text>')
    for k, (sx, sy) in enumerate([(640, 50), (700, 80), (592, 36)]):
        o.append(f'<path d="M{sx} {sy-8}L{sx+2.2} {sy-2.2}L{sx+8} {sy}L{sx+2.2} {sy+2.2}L{sx} {sy+8}L{sx-2.2} {sy+2.2}L{sx-8} {sy}L{sx-2.2} {sy-2.2}z" fill="{GOLD}">'
                 f'<animate attributeName="opacity" values="1;0.2;1" dur="{1.8+k*0.5:.1f}s" repeatCount="indefinite"/></path>')
    return frame(W, H, "".join(o))


# =================================================================== PROJECTS (streaming-style row)
def projects(d):
    W, H = 1000, 380
    pin = d["pinned"][:6]
    o = [f'<text x="48" y="58" font-family="{SANS}" font-size="28" font-weight="800" fill="{PAPER}">Continue Watching</text>',
         f'<text x="48" y="82" font-family="{SANS}" font-size="14" fill="{MUTED}">My projects, pinned on GitHub</text>']
    grads = [(ORANGE, "#b3213b"), (VIOLET, "#3b3190"), ("#ff9a6b", VIOLET), (ICE, "#3b3190"), (GOLD, ORANGE), (MINT, "#3b3190")]
    now = dt.datetime.now(dt.timezone.utc)
    for i, r in enumerate(pin):
        x = 48 + i * 152; y = 108; w, h = 144, 232
        a, b = grads[int(hashlib.md5(r["name"].encode()).hexdigest(), 16) % len(grads)]
        nm = r["name"].replace("S85_", "").replace("_", " ").lstrip("- ").strip()
        words = nm.replace("-", " ").split()
        ini = ("".join(w_[0] for w_ in words[:2]) if len(words) > 1 else nm[:2]).upper()
        new = r.get("pushed") and (now - r["pushed"]).days < 14
        lines = textwrap.wrap(nm, 15)[:3]
        o.append(f'<defs><linearGradient id="pg{i}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'
                 f'<linearGradient id="pf{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK}" stop-opacity="0"/><stop offset="1" stop-color="{INK}" stop-opacity="0.92"/></linearGradient></defs>'
                 f'<g opacity="0"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="url(#pg{i})"/>'
                 f'<text x="{x+w/2}" y="{y+96}" text-anchor="middle" font-family="{SANS}" font-size="56" font-weight="900" fill="{INK}" opacity="0.85">{esc(ini)}</text>'
                 f'<rect x="{x}" y="{y+100}" width="{w}" height="{h-100}" rx="12" fill="url(#pf{i})"/>'
                 f'<circle cx="{x+w/2}" cy="{y+70}" r="0" fill="none"/>')
        for j, ln in enumerate(lines):
            o.append(f'<text x="{x+12}" y="{y+150+j*17}" font-family="{SANS}" font-size="13.5" font-weight="800" fill="{PAPER}">{esc(ln)}</text>')
        meta = r["lang"] or "Code"
        o.append(f'<text x="{x+12}" y="{y+h-14}" font-family="{MONO}" font-size="11" fill="{PAPER}" opacity="0.85">{esc(meta)}</text>'
                 f'<text x="{x+w-12}" y="{y+h-14}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{GOLD}">&#9733; {r["stars"]}</text>')
        if new:
            o.append(f'<rect x="{x+10}" y="{y+10}" width="44" height="18" rx="4" fill="{INK}"/><text x="{x+32}" y="{y+23}" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="800" fill="{ORANGE}">NEW</text>')
        o.append(f'<animate attributeName="opacity" values="0;1" dur="0.5s" begin="{0.1+i*0.12:.2f}s" fill="freeze"/></g>')
    o.append(f'<text x="48" y="366" font-family="{MONO}" font-size="11" fill="{MUTED}">live from my pinned repositories, updated automatically</text>')
    return frame(W, H, "".join(o))


# =================================================================== INVENTORY (real logos)
BRAND = {"Java": "#f89820", "Python": "#5aa6e0", "C++": "#4a90d9", "JavaScript": "#f7df1e", "TypeScript": "#4d9be6", "Node.js": "#6cc24a",
         "MongoDB": "#47a248", "MySQL": "#5aa6d0", "Firebase": "#ffca28", "React": "#61dafb", "HTML5": "#e34f26", "CSS3": "#3d9be0",
         "Figma": "#f24e1e", "Git": "#f05032", "GitHub": "#f1ede4", "Docker": "#2496ed", "AWS": "#ff9900", "Vercel": "#f1ede4", "Netlify": "#00c7b7"}
ITEMS = [  # name, logo key(s), category, status, blurb
    ("DSA", ["DSA"], "QUEST", "In progress", "Data structures and algorithms, every day"),
    ("Java", ["Java"], "LANGUAGE", "Learning", "Fundamentals and OOP"),
    ("Python", ["Python"], "LANGUAGE", "Using", "Projects and problem solving"),
    ("C++", ["C++"], "LANGUAGE", "Using", "In my toolkit"),
    ("JavaScript", ["JavaScript"], "LANGUAGE", "Using", "Powers my MERN projects"),
    ("TypeScript", ["TypeScript"], "LANGUAGE", "Using", "Typed JavaScript, a big part of my repos"),
    ("Node.js", ["Node.js"], "BACKEND", "Learning", "Backend runtime for MERN"),
    ("MongoDB", ["MongoDB"], "BACKEND", "Using", "Ask me the basics"),
    ("MySQL", ["MySQL"], "BACKEND", "Using", "Relational databases"),
    ("Firebase", ["Firebase"], "BACKEND", "Using", "Backend as a service"),
    ("React", ["React"], "FRONTEND", "Using", "Frontend of my MERN projects"),
    ("HTML & CSS", ["HTML5", "CSS3"], "FRONTEND", "Using", "Markup and styling"),
    ("Figma", ["Figma"], "FRONTEND", "Using", "Design and prototypes"),
    ("Git", ["Git"], "TOOL", "Learning", "Version control"),
    ("GitHub", ["GitHub"], "TOOL", "Learning", "Where I ship my work"),
    ("Docker", ["Docker"], "TOOL", "Using", "Containers"),
    ("AWS", ["AWS"], "TOOL", "Using", "Cloud basics"),
    ("Vercel", ["Vercel"], "TOOL", "Using", "Deployments"),
    ("Netlify", ["Netlify"], "TOOL", "Using", "Deployments"),
]
CAT = {"QUEST": MINT, "LANGUAGE": VIOLET, "BACKEND": ORANGE, "FRONTEND": ICE, "TOOL": GOLD}


def logo(keys, cx, cy, size):
    if keys == ["DSA"]:
        s = size / 40.0
        return (f'<g transform="translate({cx-size/2} {cy-size/2}) scale({s})" stroke="{MINT}" stroke-width="2.4" fill="none" stroke-linecap="round">'
                f'<path d="M20 9L8 30M20 9L32 30M8 30H32"/><circle cx="20" cy="9" r="5" fill="{INK}"/><circle cx="8" cy="30" r="5" fill="{INK}"/><circle cx="32" cy="30" r="5" fill="{INK}"/></g>')
    out = []; n = len(keys); each = size / n * (1.0 if n == 1 else 1.05)
    for i, k in enumerate(keys):
        L = LOGOS[k]; vb = [float(v) for v in L["vb"].split()]
        sz = size if n == 1 else each
        x = cx - size / 2 + (0 if n == 1 else i * (size / n) - (0 if i == 0 else 0))
        y = cy - sz / 2
        out.append(f'<svg x="{x:.1f}" y="{y:.1f}" width="{sz:.1f}" height="{sz:.1f}" viewBox="{L["vb"]}" fill="{BRAND[k]}"><path d="{L["d"]}"/></svg>')
    return "".join(out)


def inventory(d):
    W, H = 1000, 540
    o = [f'<text x="48" y="56" font-family="{MONO}" font-size="20" font-weight="800" letter-spacing="4" fill="{PAPER}">INVENTORY</text>',
         f'<text x="48" y="78" font-family="{MONO}" font-size="12" fill="{MUTED}">{len(ITEMS)} items equipped, 2 slots waiting for the next skill</text>']
    SL, G, X0, Y0, COLS = 72, 8, 48, 96, 7
    pos = []
    for i in range(COLS * 3):
        x = X0 + (i % COLS) * (SL + G); y = Y0 + (i // COLS) * (SL + G)
        if i >= len(ITEMS):
            o.append(f'<rect x="{x}" y="{y}" width="{SL}" height="{SL}" rx="8" fill="none" stroke="{LINE}" stroke-width="2" stroke-dasharray="6 6"/>'
                     f'<text x="{x+SL/2}" y="{y+SL/2+9}" text-anchor="middle" font-family="{MONO}" font-size="26" fill="{LINE}">+</text>')
            continue
        name, keys, cat, st, bl = ITEMS[i]; c = CAT[cat]; pos.append((x, y))
        o.append(f'<rect x="{x}" y="{y}" width="{SL}" height="{SL}" rx="8" fill="{PANEL}" stroke="{LINE}" stroke-width="2"/>'
                 f'<rect x="{x+6}" y="{y+6}" width="{SL-12}" height="{SL-12}" rx="6" fill="{c}" opacity="0.10"/>'
                 f'<rect x="{x+6}" y="{y+6}" width="{SL-12}" height="{SL-12}" rx="6" fill="none" stroke="{c}" stroke-opacity="0.7" stroke-width="1.5"/>'
                 + logo(keys, x + SL / 2, y + SL / 2 - 4, 36) +
                 f'<text x="{x+SL/2}" y="{y+SL-9}" text-anchor="middle" font-family="{MONO}" font-size="9" fill="{MUTED}">{esc(name)}</text>')
    T = 2.4 * len(ITEMS)
    o.append(f'<rect x="{pos[0][0]-3}" y="{pos[0][1]-3}" width="{SL+6}" height="{SL+6}" rx="10" fill="none" stroke="{PAPER}" stroke-width="3">'
             f'<animate attributeName="x" values="{";".join(str(p[0]-3) for p in pos)}" calcMode="discrete" dur="{T}s" repeatCount="indefinite"/>'
             f'<animate attributeName="y" values="{";".join(str(p[1]-3) for p in pos)}" calcMode="discrete" dur="{T}s" repeatCount="indefinite"/></rect>')
    TX, TY, TW, TH = 48, 360, 552, 152
    o.append(f'<rect x="{TX}" y="{TY}" width="{TW}" height="{TH}" rx="12" fill="{PANEL}" stroke="{LINE}"/>')
    for i, (name, keys, cat, st, bl) in enumerate(ITEMS):
        c = CAT[cat]; a, b = i * 2.4, (i + 1) * 2.4
        pts = [(0, 0), (a, 0), (a + 0.02, 1), (b, 1), (b + 0.02, 0)] if i else [(0, 1), (b, 1), (b + 0.02, 0), (T - 0.02, 0), (T, 1)]
        o.append(f'<g opacity="0">{anim("opacity", pts, T)}'
                 f'<rect x="{TX+22}" y="{TY+26}" width="100" height="100" rx="12" fill="{c}" opacity="0.12"/><rect x="{TX+22}" y="{TY+26}" width="100" height="100" rx="12" fill="none" stroke="{c}" stroke-width="2"/>'
                 + logo(keys, TX + 72, TY + 76, 60) +
                 f'<text x="{TX+148}" y="{TY+54}" font-family="{SANS}" font-size="26" font-weight="800" fill="{PAPER}">{esc(name)}</text>'
                 f'<text x="{TX+148}" y="{TY+78}" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{c}">{cat}</text>'
                 f'<text x="{TX+148}" y="{TY+102}" font-family="{SANS}" font-size="14" font-weight="700" fill="{PAPER}">Status: {st}</text>'
                 f'<text x="{TX+148}" y="{TY+126}" font-family="{SANS}" font-size="13" fill="{MUTED}">{esc(bl)}</text></g>')
    AX, AY, AW, AH = 624, 40, 328, 472
    ach = [("Hello, World", "Create your first repository", d["repos"], 1),
           ("Repo Collector", "25 public repositories", d["repos"], 25),
           ("On Fire", "7-day contribution streak", d["streak"], 7),
           ("Century", "100 contributions in a year", d["total"], 100),
           ("Polyglot", "Code in 5 languages", len(d["langs"]), 5),
           ("Social", "Reach 10 followers", d["followers"], 10)]
    done = sum(1 for _, _, v, t in ach if v >= t)
    o.append(f'<rect x="{AX}" y="{AY}" width="{AW}" height="{AH}" rx="14" fill="{PANEL}" stroke="{LINE}"/>'
             f'<text x="{AX+24}" y="{AY+38}" font-family="{MONO}" font-size="15" font-weight="800" letter-spacing="3" fill="{PAPER}">ACHIEVEMENTS</text>'
             f'<text x="{AX+AW-24}" y="{AY+38}" text-anchor="end" font-family="{MONO}" font-size="14" fill="{ORANGE}">{done} / {len(ach)}</text>'
             f'<line x1="{AX}" y1="{AY+54}" x2="{AX+AW}" y2="{AY+54}" stroke="{LINE}"/>')
    for i, (t, ds, v, tg) in enumerate(ach):
        y = AY + 92 + i * 65; ok = v >= tg; col = ORANGE if ok else MUTED; frac = min(1, v / tg)
        icon = (f'<path d="M-8 0l5 6 11-12" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>' if ok else
                f'<rect x="-6" y="-2" width="12" height="9" rx="2" fill="{MUTED}"/><path d="M-4 -2v-3a4 4 0 018 0v3" fill="none" stroke="{MUTED}" stroke-width="2"/>')
        o.append(f'<g opacity="{1 if ok else 0.75}"><circle cx="{AX+38}" cy="{y}" r="17" fill="{ORANGE if ok else LINE}"/><g transform="translate({AX+38} {y})">{icon}</g>'
                 f'<text x="{AX+70}" y="{y-6}" font-family="{SANS}" font-size="16" font-weight="800" fill="{PAPER if ok else MUTED}">{t}</text>'
                 f'<text x="{AX+70}" y="{y+12}" font-family="{SANS}" font-size="12" fill="{MUTED}">{ds}</text>'
                 f'<rect x="{AX+70}" y="{y+20}" width="170" height="4" rx="2" fill="{INK}"/><rect x="{AX+70}" y="{y+20}" width="{170*frac:.1f}" height="4" rx="2" fill="{col}"/>'
                 f'<text x="{AX+AW-24}" y="{y+25}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{col}">{min(v,tg) if ok else v}/{tg}</text></g>')
    return frame(W, H, "".join(o))


# =================================================================== DAILY QUESTS + TIP + MANTRA
PROBLEMS = [("Two Sum", "Easy", "Hash Map"), ("Valid Parentheses", "Easy", "Stack"), ("Merge Two Sorted Lists", "Easy", "Linked List"),
            ("Best Time to Buy and Sell Stock", "Easy", "Arrays"), ("Binary Search", "Easy", "Binary Search"), ("Maximum Subarray", "Medium", "Dynamic Programming"),
            ("Contains Duplicate", "Easy", "Hash Set"), ("Climbing Stairs", "Easy", "Dynamic Programming"), ("Reverse Linked List", "Easy", "Linked List"),
            ("Invert Binary Tree", "Easy", "Trees"), ("Valid Anagram", "Easy", "Hash Map"), ("Number of Islands", "Medium", "BFS / DFS"),
            ("Product of Array Except Self", "Medium", "Prefix Products"), ("3Sum", "Medium", "Two Pointers"), ("Longest Substring Without Repeating Characters", "Medium", "Sliding Window"),
            ("Coin Change", "Medium", "Dynamic Programming"), ("Merge Intervals", "Medium", "Sorting"), ("Group Anagrams", "Medium", "Hash Map"),
            ("Top K Frequent Elements", "Medium", "Heap"), ("Course Schedule", "Medium", "Graphs"), ("Lowest Common Ancestor of a BST", "Medium", "Trees"),
            ("Kth Largest Element in an Array", "Medium", "Heap"), ("Min Stack", "Medium", "Stack"), ("Linked List Cycle", "Easy", "Two Pointers"),
            ("Maximum Depth of Binary Tree", "Easy", "Trees"), ("Find Minimum in Rotated Sorted Array", "Medium", "Binary Search"), ("House Robber", "Medium", "Dynamic Programming"),
            ("Word Search", "Medium", "Backtracking"), ("Rotate Array", "Medium", "Arrays"), ("Palindrome Number", "Easy", "Math")]
CONCEPTS = ["Big-O notation", "Recursion", "Stacks and queues", "Hash maps", "Binary search", "Linked lists", "Trees and traversals",
            "Graphs: BFS and DFS", "Sorting algorithms", "Dynamic programming basics", "Two pointers", "Sliding window", "Heaps and priority queues",
            "OOP: encapsulation", "OOP: inheritance and polymorphism", "REST API basics", "Git branching", "SQL joins", "Async JavaScript", "React hooks"]
TIPS = [("DSA", "Read the constraints first. n up to 10^5 usually means you need O(n log n) or better."),
        ("DSA", "Stuck? Write the brute force, then ask where it repeats work. That repetition is your optimisation."),
        ("DSA", "Searching the same list twice? Put it in a HashMap or HashSet instead."),
        ("DSA", "Contiguous subarray or substring? Try a sliding window before anything else."),
        ("DSA", "Sorted input is a hint. Think binary search or two pointers."),
        ("DSA", "BFS finds shortest paths, DFS explores everything. Pick one on purpose."),
        ("DSA", "Draw the first three steps on paper. Most bugs are visible before you code."),
        ("DSA", "Dynamic programming is recursion plus memory. Write the recursion first."),
        ("DSA", "Test edge cases first: empty input, one element, duplicates, negatives."),
        ("JAVA", "Prefer ArrayDeque over Stack and LinkedList for stacks and queues in Java."),
        ("JAVA", "Use StringBuilder inside loops. Plain string concatenation creates a new object every time."),
        ("JAVA", "equals() compares content, == compares references. Know which one you need."),
        ("JAVA", "Program to interfaces: declare List, not ArrayList, so you can swap implementations later."),
        ("JAVA", "Use try-with-resources so files and connections always close."),
        ("GIT", "Commit small and often. A good message says why you changed something, not what."),
        ("GIT", "Make a branch for every feature. Your main branch should always work."),
        ("GIT", "Run git status before every commit. Two seconds that save a messy history."),
        ("GIT", "In a merge conflict, read both sides slowly, keep the intent, test, then commit."),
        ("WEB", "Never trust user input. Validate on the server even if the form already checks it."),
        ("WEB", "Keep secrets in environment variables. Never commit an API key, not even once."),
        ("WEB", "Design your database tables on paper before you write a single query."),
        ("WEB", "In React, keep state as low as possible and lift it only when two components need it."),
        ("WEB", "HTTP codes are a language: 2xx worked, 4xx you erred, 5xx the server erred."),
        ("CAREER", "Consistency beats intensity. One hour every day beats ten hours on Sunday."),
        ("CAREER", "Explain a concept to an imaginary friend. Gaps in your explanation are gaps in your understanding."),
        ("CAREER", "Read other people's code for 15 minutes a day. It is the fastest way to level up."),
        ("CAREER", "Ship the ugly version, then improve it. A deployed project beats a perfect idea."),
        ("CAREER", "Write three lines on what you learned today. Your future portfolio starts there."),
        ("CAREER", "Ask good questions: say what you tried, what you expected and what happened instead.")]
MANTRAS = ["Small commits. Big momentum.", "Progress, not perfection.", "Debug the problem, not yourself.", "Every expert once printed Hello World.",
           "Today's bug is tomorrow's story.", "Learn it. Build it. Ship it.", "Slow is smooth, smooth is fast.", "One more problem. One more level.",
           "Code today, thank yourself tomorrow.", "Stay curious. Stay consistent.", "Strong foundations build tall systems.", "Make it work, make it right, make it fast.",
           "Done is better than perfect.", "Your streak is a promise to yourself.", "Hard problems are easy ones in disguise.", "Keep going. The compiler believes in you.",
           "Build in public. Learn in public.", "Be one percent better than yesterday.", "Fail fast, learn faster.", "Read the error message. It is trying to help.",
           "Show up, write code, repeat.", "Dream big, commit small.", "Think twice, code once.", "Curiosity is your best debugger.",
           "Rest is part of the process.", "Write code that tomorrow-you can read.", "The best time to start was yesterday. The next best is now.",
           "Every bug fixed is a lesson earned.", "Never stop being a beginner.", "Be the engineer you needed when you started."]


def daily(d, now):
    W, H = 1000, 460
    n = now.date().toordinal()
    prob, conc = PROBLEMS[n % len(PROBLEMS)], CONCEPTS[(n * 3) % len(CONCEPTS)]
    tipcat, tip = TIPS[(n * 7) % len(TIPS)]
    mantra = MANTRAS[(n * 11) % len(MANTRAS)]
    done_commit = d["today"] > 0
    o = [f'<text x="48" y="54" font-family="{MONO}" font-size="18" font-weight="800" letter-spacing="4" fill="{PAPER}">DAILY QUESTS</text>',
         f'<text x="48" y="76" font-family="{MONO}" font-size="12" fill="{MUTED}">{now.strftime("%A, %d %B %Y")}  ·  new quests every day at midnight IST</text>']
    quests = [("Ship a commit", f'{d["today"]} commit{"s" if d["today"] != 1 else ""} so far today', done_commit, ORANGE),
              (f"Solve: {prob[0]}", f"{prob[1]}  ·  {prob[2]}", False, VIOLET),
              (f"Revise: {conc}", "Fifteen focused minutes is enough", False, ICE)]
    for i, (t, sub, ok, col) in enumerate(quests):
        y = 100 + i * 96
        o.append(f'<rect x="48" y="{y}" width="500" height="84" rx="14" fill="{PANEL}" stroke="{col if ok else LINE}" stroke-width="{2 if ok else 1}"/>'
                 f'<rect x="68" y="{y+20}" width="44" height="44" rx="10" fill="{col}" opacity="0.16"/><rect x="68" y="{y+20}" width="44" height="44" rx="10" fill="none" stroke="{col}" stroke-width="1.8"/>'
                 f'<text x="90" y="{y+49}" text-anchor="middle" font-family="{MONO}" font-size="20" font-weight="800" fill="{col}">{i+1}</text>'
                 f'<text x="130" y="{y+38}" font-family="{SANS}" font-size="17" font-weight="800" fill="{PAPER}">{esc(textwrap.shorten(t, 38, placeholder="..."))}</text>'
                 f'<text x="130" y="{y+60}" font-family="{SANS}" font-size="13" fill="{MUTED}">{esc(sub)}</text>'
                 f'<text x="476" y="{y+34}" text-anchor="end" font-family="{MONO}" font-size="12" font-weight="800" fill="{col}">+10 XP</text>')
        if ok:
            o.append(f'<circle cx="512" cy="{y+30}" r="14" fill="{ORANGE}"/><path d="M505 {y+30}l5 6 9-12" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
                     f'<text x="530" y="{y+66}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{ORANGE}">COMPLETE</text>')
        else:
            o.append(f'<circle cx="512" cy="{y+30}" r="14" fill="none" stroke="{LINE}" stroke-width="2"/>'
                     f'<text x="530" y="{y+66}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">TO DO</text>')
    o.append(f'<text x="48" y="404" font-family="{MONO}" font-size="12" fill="{MUTED}">{1 if done_commit else 0} / 3 complete  ·  streak bonus +20 XP at 7 days  ·  current streak {d["streak"]}</text>')
    # tip panel
    o.append(f'<rect x="572" y="40" width="380" height="204" rx="16" fill="{PANEL}" stroke="{LINE}"/>'
             f'<text x="596" y="74" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{MUTED}">TIP OF THE DAY</text>'
             f'<rect x="{952-24-62}" y="58" width="62" height="22" rx="11" fill="{ORANGE}" opacity="0.18"/><text x="{952-24-31}" y="73" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="800" fill="{ORANGE}">{tipcat}</text>')
    for j, ln in enumerate(textwrap.wrap(tip, 38)[:5]):
        o.append(f'<text x="596" y="{112+j*25}" font-family="{SANS}" font-size="16" font-weight="600" fill="{PAPER}">{esc(ln)}</text>')
    o.append(f'<rect x="596" y="224" width="332" height="4" rx="2" fill="{INK}"/><rect x="596" y="224" width="0" height="4" rx="2" fill="url(#grad)"><animate attributeName="width" values="0;332" dur="6s" repeatCount="indefinite"/></rect>')
    # mantra panel
    o.append(f'<rect x="572" y="260" width="380" height="160" rx="16" fill="url(#mant)"/>'
             f'<text x="596" y="294" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{INK}" opacity="0.7">DAILY MANTRA</text>')
    for j, ln in enumerate(textwrap.wrap(mantra, 22)[:3]):
        o.append(f'<text x="596" y="{342+j*34}" font-family="{SANS}" font-size="27" font-weight="900" fill="{INK}">{esc(ln)}</text>')
    defs = f'<linearGradient id="mant" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{ORANGE}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>'
    return frame(W, H, "".join(o), defs)


# =================================================================== CONTRIBUTION SNAKE (real graph)
def snake(d):
    weeks = d["weeks"]; cols = len(weeks)
    W, H = 1000, 292
    s = calc(d)
    pitch = 904.0 / cols; cell = pitch - 3.2
    gx, gy = 48, 108
    mx = max((c for wk in weeks for c in wk if c), default=1)
    EMPTY = "#1c1940"; G = ["#0e4429", "#006d32", "#26a641", "#39d353"]

    def color(c):
        if not c: return EMPTY
        r = c / mx
        return G[0] if r <= 0.25 else G[1] if r <= 0.5 else G[2] if r <= 0.75 else G[3]

    order = []
    for w in range(cols):
        rows = list(range(7)) if w % 2 == 0 else list(range(6, -1, -1))
        for r in rows:
            if weeks[w][r] is not None:
                order.append((w, r))
    N = len(order); step = 0.045; T = N * step + 4.0
    cen = {(w, r): (gx + w * pitch + cell / 2, gy + r * pitch + cell / 2) for w, r in order}
    path = "M" + " L".join(f"{cen[k][0]:.1f} {cen[k][1]:.1f}" for k in order)
    o = [f'<text x="48" y="52" font-family="{SANS}" font-size="26" font-weight="800" fill="{PAPER}">Contribution Snake</text>',
         f'<text x="48" y="76" font-family="{SANS}" font-size="14" fill="{MUTED}">{d["total"]} contributions in the last year  ·  {s["active"]} active days  ·  longest streak {s["longest"]} days</text>']
    idx = {k: i for i, k in enumerate(order)}
    for (w, r), i in idx.items():
        c = weeks[w][r]; x = gx + w * pitch; y = gy + r * pitch; col = color(c)
        if c:
            t0 = i * step
            kt = f"0;{t0/T:.4f};{(t0+0.15)/T:.4f};{(T-1.0)/T:.4f};{(T-0.6)/T:.4f};1"
            vals = f"{col};{col};{EMPTY};{EMPTY};{col};{col}"
            o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="3" fill="{col}"><animate attributeName="fill" dur="{T:.2f}s" repeatCount="indefinite" keyTimes="{kt}" values="{vals}"/></rect>')
        else:
            o.append(f'<rect x="{x:.1f}" y="{gy + r * pitch:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="3" fill="{EMPTY}"/>')
    segs = 9
    for k in range(segs - 1, -1, -1):
        sz = cell + (3 if k == 0 else 1.5 - k * 0.12)
        colr = ORANGE if k == 0 else VIOLET
        op = 1 if k == 0 else max(0.35, 1 - k * 0.08)
        lag = k * step * 1.4
        kt = f"0;{lag/T:.4f};{min((lag+N*step)/T,1):.4f};1"
        o.append(f'<rect x="{-sz/2:.1f}" y="{-sz/2:.1f}" width="{sz:.1f}" height="{sz:.1f}" rx="4" fill="{colr}" opacity="{op:.2f}">'
                 f'<animateMotion dur="{T:.2f}s" repeatCount="indefinite" calcMode="linear" keyPoints="0;0;1;1" keyTimes="{kt}"><mpath xlink:href="#sp"/></animateMotion></rect>')
    o.append(f'<path id="sp" d="{path}" fill="none" stroke="none"/>')
    for i, col in enumerate([EMPTY] + G):
        o.append(f'<rect x="{800+i*20}" y="258" width="14" height="14" rx="3" fill="{col}"/>')
    o.append(f'<text x="786" y="270" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">Less</text><text x="912" y="270" font-family="{MONO}" font-size="11" fill="{MUTED}">More</text>')
    o.append(f'<text x="48" y="270" font-family="{MONO}" font-size="11" fill="{MUTED}">the snake eats every day I contributed, then the year starts again</text>')
    return frame(W, H, "".join(o))
