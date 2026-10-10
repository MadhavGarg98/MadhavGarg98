"""Draws the Instagram-style post, Spotify-style player, Wrapped card and game inventory."""
import base64, math, os, textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INK, PANEL, LINE, PAPER, MUTED = "#0b0a1a", "#12102a", "#2b2757", "#f1ede4", "#8e89b8"
ORANGE, VIOLET = "#ff7a45", "#8b7bff"
ICE, GOLD, MINT = "#7dd3fc", "#ffd36b", "#6ee7b7"
SANS = "Inter,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code',Consolas,'DejaVu Sans Mono',monospace"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def b64(name, mime):
    return f"data:{mime};base64," + base64.b64encode(open(os.path.join(ROOT, "data", name), "rb").read()).decode()


def anim(attr, pts, T, extra=""):
    pts = sorted(pts, key=lambda p: p[0])
    if pts[0][0] > 0: pts.insert(0, (0, pts[0][1]))
    if pts[-1][0] < T: pts.append((T, pts[-1][1]))
    kt = ";".join(f"{p[0] / T:.4f}" for p in pts)
    vs = ";".join(str(p[1]) for p in pts)
    return f'<animate attributeName="{attr}" dur="{T}s" repeatCount="indefinite" keyTimes="{kt}" values="{vs}" {extra}/>'


def frame(W, H, inner, defs=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>{defs}
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{LINE}"/></pattern>
<linearGradient id="grad" x1="0" x2="1"><stop offset="0" stop-color="{ORANGE}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>
<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{INK}"/><rect width="{W}" height="{H}" fill="url(#dots)" opacity="0.5"/>{inner}</g>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{LINE}"/>
</svg>'''


HEART = "M12 21s-7-4.5-9.5-9C.8 8.5 3 5 6.5 5c2 0 3.5 1 5.5 3 2-2 3.5-3 5.5-3C21 5 23.2 8.5 21.5 12 19 16.5 12 21 12 21z"


# =================================================================== INSTAGRAM-STYLE POST
def instagram(d):
    W, H, PX = 1000, 640, 640
    photo, av = b64("photo.jpg", "image/jpeg"), b64("avatar.jpg", "image/jpeg")
    o = []
    o.append(f'<image href="{photo}" x="0" y="0" width="{PX}" height="{H}" preserveAspectRatio="xMidYMid slice"/>')
    # tag pill like a tagged person
    o.append(f'<g transform="translate(296 372)"><path d="M-6 0h12l-6 -8z" fill="#000" opacity="0.75"/><rect x="-62" y="0" width="124" height="26" rx="7" fill="#000" opacity="0.75"/>'
             f'<text x="0" y="17.5" text-anchor="middle" font-family="{SANS}" font-size="12" font-weight="600" fill="#fff">madhavgarg98</text></g>')
    # double-tap heart
    o.append(f'<g transform="translate(320 320)" opacity="0"><g><animateTransform attributeName="transform" type="scale" dur="9s" begin="1.5s" repeatCount="indefinite" '
             f'keyTimes="0;0.05;0.1;0.2;1" values="0;1.25;1;1.5;1.5"/><path d="{HEART}" transform="translate(-60 -60) scale(5)" fill="#fff"/></g>'
             f'<animate attributeName="opacity" dur="9s" begin="1.5s" repeatCount="indefinite" keyTimes="0;0.05;0.12;0.2;1" values="0;0.95;0.95;0;0"/></g>')
    # carousel dots
    for i in range(3):
        o.append(f'<circle cx="{320 + (i - 1) * 14}" cy="{H - 22}" r="3.5" fill="#fff" opacity="{1 if i == 0 else 0.45}"/>')
    # right panel
    o.append(f'<rect x="{PX}" y="0" width="{W-PX}" height="{H}" fill="{PANEL}"/><line x1="{PX}" y1="0" x2="{PX}" y2="{H}" stroke="{LINE}"/>')
    o.append(f'<clipPath id="av"><circle cx="{PX+36}" cy="36" r="17"/></clipPath>'
             f'<g><animateTransform attributeName="transform" type="rotate" from="0 {PX+36} 36" to="360 {PX+36} 36" dur="8s" repeatCount="indefinite"/>'
             f'<circle cx="{PX+36}" cy="36" r="22" fill="none" stroke="url(#grad)" stroke-width="3" stroke-dasharray="46 8"/></g>'
             f'<image href="{av}" x="{PX+19}" y="19" width="34" height="34" clip-path="url(#av)"/>')
    o.append(f'<text x="{PX+70}" y="31" font-family="{SANS}" font-size="15" font-weight="700" fill="{PAPER}">madhavgarg98</text>'
             f'<text x="{PX+70}" y="50" font-family="{SANS}" font-size="12" fill="{MUTED}">{d["repos"]} repos · {d["followers"]} followers · {d["following"]} following</text>'
             f'<text x="{W-26}" y="40" text-anchor="end" font-family="{SANS}" font-size="20" font-weight="700" fill="{PAPER}">···</text>'
             f'<line x1="{PX}" y1="72" x2="{W}" y2="72" stroke="{LINE}"/>')
    cap = "Computer Science student learning DSA, building in Java and Python, shipping MERN projects."
    cl = textwrap.wrap("madhavgarg98 " + cap, 40)
    y = 98
    for i, ln in enumerate(cl):
        x = PX + 20
        if i == 0:
            rest = ln[len("madhavgarg98 "):]
            o.append(f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="13.5" fill="{PAPER}"><tspan font-weight="700">madhavgarg98 </tspan>{esc(rest)}</text>')
        else:
            o.append(f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="13.5" fill="{PAPER}">{esc(ln)}</text>')
        y += 19
    o.append(f'<text x="{PX+20}" y="{y+4}" font-family="{SANS}" font-size="13.5" fill="{VIOLET}">#DSA #Java #Python #MERN #OpenSource</text>')
    comments = ["Collab: beginner-friendly open source, college projects, learning hackathons.",
                "Need help with: optimizing DSA, system design basics, clean code.",
                "Ask me about MongoDB basics, Java fundamentals and the MERN stack.",
                "Fun fact: I break complex CS ideas into simple explanations. I don't give up easily."]
    cy = 192
    for i, c in enumerate(comments):
        ls = textwrap.wrap("madhavgarg98 " + c, 40)
        t = 0.4 + i * 0.7
        g = [f'<circle cx="{PX+32}" cy="{cy+8}" r="12" fill="url(#grad)"/>'
             f'<text x="{PX+32}" y="{cy+12.5}" text-anchor="middle" font-family="{SANS}" font-size="11" font-weight="800" fill="{INK}">M</text>']
        yy = cy + 5
        for j, ln in enumerate(ls):
            if j == 0:
                rest = ln[len("madhavgarg98 "):]
                g.append(f'<text x="{PX+54}" y="{yy}" font-family="{SANS}" font-size="13" fill="{PAPER}"><tspan font-weight="700">madhavgarg98 </tspan>{esc(rest)}</text>')
            else:
                g.append(f'<text x="{PX+54}" y="{yy}" font-family="{SANS}" font-size="13" fill="{PAPER}">{esc(ln)}</text>')
            yy += 17
        g.append(f'<text x="{PX+54}" y="{yy+3}" font-family="{SANS}" font-size="11" fill="{MUTED}">{i+1}d    Reply</text>')
        o.append(f'<g opacity="0">{g and "".join(g)}<animate attributeName="opacity" values="0;1" dur="0.5s" begin="{t:.1f}s" fill="freeze"/></g>')
        cy += 70
    # actions
    ay = 486
    o.append(f'<line x1="{PX}" y1="{ay}" x2="{W}" y2="{ay}" stroke="{LINE}"/>')
    o.append(f'<g transform="translate({PX+18} {ay+10}) scale(1.1)"><path d="{HEART}" fill="{ORANGE}">'
             f'<animateTransform attributeName="transform" type="scale" values="1;1.18;1" dur="1.6s" repeatCount="indefinite" additive="sum"/></path></g>')
    o.append(f'<g transform="translate({PX+56} {ay+10}) scale(1.1)" fill="none" stroke="{PAPER}" stroke-width="1.8" stroke-linejoin="round"><path d="M4 4h16v12H9l-5 4z"/></g>')
    o.append(f'<g transform="translate({PX+94} {ay+10}) scale(1.1)" fill="none" stroke="{PAPER}" stroke-width="1.8" stroke-linejoin="round"><path d="M3 11L21 3l-6 18-3-8z"/></g>')
    o.append(f'<g transform="translate({W-48} {ay+10}) scale(1.1)" fill="none" stroke="{PAPER}" stroke-width="1.8" stroke-linejoin="round"><path d="M6 3h12v18l-6-4-6 4z"/></g>')
    o.append(f'<text x="{PX+20}" y="{ay+58}" font-family="{SANS}" font-size="13.5" fill="{PAPER}"><tspan font-weight="700">{d["total"]} contributions</tspan> in the last year</text>')
    o.append(f'<text x="{PX+20}" y="{ay+76}" font-family="{SANS}" font-size="10.5" letter-spacing="0.8" fill="{MUTED}">{d["streak"]}-DAY STREAK, {d["today"]} TODAY</text>')
    o.append(f'<line x1="{PX}" y1="{ay+92}" x2="{W}" y2="{ay+92}" stroke="{LINE}"/>')
    o.append(f'<text x="{PX+20}" y="{ay+122}" font-family="{SANS}" font-size="13.5" fill="{MUTED}">Say hi, links are just below</text>'
             f'<text x="{W-24}" y="{ay+122}" text-anchor="end" font-family="{SANS}" font-size="13.5" font-weight="700" fill="{ORANGE}">Post</text>')
    return frame(W, H, "".join(o))


# =================================================================== SPOTIFY-STYLE PLAYER
def player(d):
    W, H = 1000, 560
    o = []
    # album art
    cx = cy = 170
    art = [f'<g transform="translate(48 56)"><rect width="340" height="340" rx="14" fill="url(#cover)"/>'
           f'<circle cx="{cx}" cy="{cy}" r="96" fill="{INK}" opacity="0.92"/>']
    for k in range(36):
        a = k * math.pi * 2 / 36; c, s = math.cos(a), math.sin(a)
        l1, l2 = 8 + (k * 7) % 22, 22 + (k * 11) % 26
        x1, y1 = cx + c * 106, cy + s * 106
        x2a, y2a = cx + c * (106 + l1), cy + s * (106 + l1)
        x2b, y2b = cx + c * (106 + l2), cy + s * (106 + l2)
        art.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2a:.1f}" y2="{y2a:.1f}" stroke="{PAPER}" stroke-width="4" stroke-linecap="round" opacity="0.9">'
                   f'<animate attributeName="x2" values="{x2a:.1f};{x2b:.1f};{x2a:.1f}" dur="{0.9 + (k % 5) * 0.25:.2f}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="y2" values="{y2a:.1f};{y2b:.1f};{y2a:.1f}" dur="{0.9 + (k % 5) * 0.25:.2f}s" repeatCount="indefinite"/></line>')
    art.append(f'<text x="{cx}" y="{cy+22}" text-anchor="middle" font-family="{MONO}" font-size="64" font-weight="800" fill="{PAPER}">MG</text>'
               f'<text x="22" y="322" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{INK}" font-weight="700">MADHAV GARG</text>'
               f'<text x="318" y="322" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{INK}" font-weight="700">VOL. 1</text></g>')
    o.append("".join(art))
    # track info
    o.append(f'<text x="48" y="438" font-family="{SANS}" font-size="28" font-weight="800" fill="{PAPER}">Learning DSA</text>'
             f'<text x="48" y="464" font-family="{SANS}" font-size="15" fill="{MUTED}">Madhav Garg  ·  CS Student Era</text>'
             f'<g transform="translate(364 424) scale(1.1)"><path d="{HEART}" fill="{ORANGE}"/></g>')
    # progress
    o.append(f'<rect x="48" y="486" width="340" height="4" rx="2" fill="{LINE}"/>'
             f'<rect x="48" y="486" width="0" height="4" rx="2" fill="{PAPER}"><animate attributeName="width" values="0;340" dur="30s" repeatCount="indefinite"/></rect>'
             f'<circle cx="48" cy="488" r="6" fill="{PAPER}"><animate attributeName="cx" values="48;388" dur="30s" repeatCount="indefinite"/></circle>'
             f'<text x="48" y="508" font-family="{MONO}" font-size="11" fill="{MUTED}">0:00</text>'
             f'<text x="388" y="508" text-anchor="end" font-family="{MONO}" font-size="13" fill="{MUTED}">&#8734;</text>')
    # controls
    cyc = 534
    o.append(f'<g fill="none" stroke="{MUTED}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
             f'<g transform="translate(58 {cyc-9}) scale(0.75)"><path d="M3 7h4l10 10h4M3 17h4l3-3M14 10l3-3h4M18 4l3 3-3 3M18 14l3 3-3 3"/></g>'
             f'<g transform="translate(356 {cyc-9}) scale(0.75)"><path d="M4 12V9a3 3 0 013-3h12M16 3l3 3-3 3M20 12v3a3 3 0 01-3 3H5M8 15l-3 3 3 3"/></g></g>'
             f'<g fill="{PAPER}"><path d="M120 {cyc-9}v18M141 {cyc-9}l-14 9 14 9z"/><rect x="118" y="{cyc-9}" width="3" height="18"/>'
             f'<path d="M296 {cyc-9}l14 9-14 9z"/><rect x="311" y="{cyc-9}" width="3" height="18"/></g>'
             f'<circle cx="218" cy="{cyc}" r="19" fill="{PAPER}"/><rect x="210" y="{cyc-8}" width="5" height="16" rx="1" fill="{INK}"/><rect x="221" y="{cyc-8}" width="5" height="16" rx="1" fill="{INK}"/>')
    # lyrics panel
    LX, LY, LW, LH = 440, 56, 512, 448
    o.append(f'<rect x="{LX}" y="{LY}" width="{LW}" height="{LH}" rx="16" fill="url(#lyr)"/>')
    o.append(f'<text x="{LX+32}" y="{LY+40}" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{MUTED}">LYRICS</text>')
    for k in range(4):
        h1, h2 = 6 + k * 3, 18 - k * 2
        o.append(f'<rect x="{LX+LW-72+k*11}" y="{LY+40-h1}" width="6" height="{h1}" rx="2" fill="{ORANGE}">'
                 f'<animate attributeName="height" values="{h1};{h2};{h1}" dur="{0.6+k*0.17:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="y" values="{LY+40-h1};{LY+40-h2};{LY+40-h1}" dur="{0.6+k*0.17:.2f}s" repeatCount="indefinite"/></rect>')
    lines = ["Learning data structures and algorithms", "Building projects in Java and Python",
             "Getting comfortable with the backend", "Breaking complex ideas into simple ones",
             "Open to beginner-friendly open source", "College projects and learning hackathons",
             "Ask me about MongoDB, Java and MERN", "And I don't give up easily"]
    T = 3.6 * len(lines)
    for i, ln in enumerate(lines):
        a, b = i * 3.6, (i + 1) * 3.6
        pts = [(0, 0.34), (max(a - 0.01, 0.001), 0.34), (a + 0.3, 1), (b, 1), (b + 0.3, 0.34)]
        if i == 0: pts = [(0, 1), (b, 1), (b + 0.3, 0.34), (T - 0.3, 0.34), (T, 1)]
        o.append(f'<text x="{LX+32}" y="{LY+94+i*40}" font-family="{SANS}" font-size="21" font-weight="800" fill="{PAPER}" opacity="0.34">{esc(ln)}{anim("opacity", pts, T)}</text>')
    o.append(f'<line x1="{LX+32}" y1="{LY+LH-50}" x2="{LX+LW-32}" y2="{LY+LH-50}" stroke="{LINE}"/>'
             f'<text x="{LX+32}" y="{LY+LH-24}" font-family="{SANS}" font-size="12" fill="{MUTED}">Written and produced by Madhav Garg  ·  Powered by curiosity</text>')
    defs = (f'<linearGradient id="cover" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{VIOLET}"/><stop offset="1" stop-color="{ORANGE}"/></linearGradient>'
            f'<linearGradient id="lyr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a2468"/><stop offset="1" stop-color="{PANEL}"/></linearGradient>')
    return frame(W, H, "".join(o), defs)


# =================================================================== WRAPPED
def wrapped(d):
    W, H = 1000, 500
    o = [f'<text x="48" y="66" font-family="{SANS}" font-size="40" font-weight="800" letter-spacing="-1" fill="url(#grad)">Madhav Wrapped</text>',
         f'<text x="48" y="92" font-family="{SANS}" font-size="14" fill="{MUTED}">Your year on GitHub, straight from the data</text>']
    tiles = [(ORANGE, INK, str(d["total"]), "contributions in the last year"),
             (VIOLET, INK, f'{d["streak"]}', "day streak right now"),
             (PAPER, INK, str(d["repos"]), "public repositories")]
    for i, (bg, fg, big, small) in enumerate(tiles):
        x = 48 + i * 312
        o.append(f'<g opacity="0"><rect x="{x}" y="112" width="280" height="140" rx="16" fill="{bg}"/>'
                 f'<text x="{x+24}" y="190" font-family="{SANS}" font-size="78" font-weight="900" letter-spacing="-3" fill="{fg}">{big}</text>'
                 f'<text x="{x+24}" y="226" font-family="{SANS}" font-size="15" font-weight="700" fill="{fg}">{small}</text>'
                 f'<animate attributeName="opacity" values="0;1" dur="0.5s" begin="{0.2+i*0.25:.2f}s" fill="freeze"/></g>')
    o.append(f'<rect x="48" y="276" width="904" height="198" rx="16" fill="{PANEL}" stroke="{LINE}"/>')
    o.append(f'<text x="76" y="312" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{MUTED}">YOUR TOP LANGUAGES</text>')
    langs = d["langs"][:5]; top = max(p for _, p in langs) or 1
    for i, (name, pct) in enumerate(langs):
        y = 346 + i * 25; bw = 340 * pct / top
        o.append(f'<text x="76" y="{y+4}" font-family="{MONO}" font-size="16" font-weight="800" fill="{ORANGE}">{i+1}</text>'
                 f'<text x="104" y="{y+4}" font-family="{SANS}" font-size="15" font-weight="700" fill="{PAPER}">{esc(name)}</text>'
                 f'<rect x="240" y="{y-6}" width="340" height="12" rx="6" fill="{INK}"/>'
                 f'<rect x="240" y="{y-6}" width="0" height="12" rx="6" fill="url(#grad)"><animate attributeName="width" values="0;{bw:.1f}" dur="1.2s" begin="{0.6+i*0.15:.2f}s" fill="freeze"/></rect>'
                 f'<text x="596" y="{y+4}" font-family="{MONO}" font-size="13" fill="{MUTED}">{pct:.1f}%</text>')
    o.append(f'<text x="676" y="356" font-family="{SANS}" font-size="30" font-weight="800" fill="{PAPER}">This year</text>'
             f'<text x="676" y="394" font-family="{SANS}" font-size="30" font-weight="800" fill="{PAPER}">you learned</text>'
             f'<text x="676" y="436" font-family="{SANS}" font-size="40" font-weight="900" fill="url(#grad)">DSA.</text>')
    for k, (sx, sy) in enumerate([(930, 48), (884, 74), (962, 84), (640, 70)]):
        o.append(f'<path d="M{sx} {sy-9}L{sx+2.5} {sy-2.5}L{sx+9} {sy}L{sx+2.5} {sy+2.5}L{sx} {sy+9}L{sx-2.5} {sy+2.5}L{sx-9} {sy}L{sx-2.5} {sy-2.5}z" fill="{GOLD}">'
                 f'<animate attributeName="opacity" values="1;0.2;1" dur="{1.8+k*0.5:.1f}s" repeatCount="indefinite"/></path>')
    return frame(W, H, "".join(o))


# =================================================================== INVENTORY + ACHIEVEMENTS
ITEMS = [  # name, abbr, category, status, blurb
    ("DSA", "DS", "QUEST", "In progress", "Data structures and algorithms, daily"),
    ("Java", "Jv", "LANGUAGE", "Learning", "Fundamentals and OOP"),
    ("Python", "Py", "LANGUAGE", "Using", "Projects and problem solving"),
    ("C++", "C+", "LANGUAGE", "Using", "In my toolkit"),
    ("JavaScript", "JS", "LANGUAGE", "Using", "Powers my MERN projects"),
    ("Node.js", "No", "BACKEND", "Learning", "Backend runtime for MERN"),
    ("MongoDB", "Mo", "BACKEND", "Using", "Ask me the basics"),
    ("MySQL", "My", "BACKEND", "Using", "Relational databases"),
    ("Firebase", "Fb", "BACKEND", "Using", "Backend as a service"),
    ("React", "Re", "FRONTEND", "Using", "Frontend of my MERN projects"),
    ("HTML & CSS", "H5", "FRONTEND", "Using", "Markup and styling"),
    ("Figma", "Fg", "FRONTEND", "Using", "Design and prototypes"),
    ("Git", "Gt", "TOOL", "Learning", "Version control"),
    ("GitHub", "Gh", "TOOL", "Learning", "Where I ship my work"),
    ("Docker", "Dk", "TOOL", "Using", "Containers"),
    ("AWS", "AW", "TOOL", "Using", "Cloud basics"),
    ("Vercel", "Vc", "TOOL", "Using", "Deploys"),
    ("Netlify", "Nl", "TOOL", "Using", "Deploys"),
]
CAT = {"QUEST": MINT, "LANGUAGE": VIOLET, "BACKEND": ORANGE, "FRONTEND": ICE, "TOOL": GOLD}


def inventory(d):
    W, H = 1000, 520
    o = [f'<text x="48" y="56" font-family="{MONO}" font-size="20" font-weight="800" letter-spacing="4" fill="{PAPER}">INVENTORY</text>',
         f'<text x="48" y="78" font-family="{MONO}" font-size="12" fill="{MUTED}">{len(ITEMS)} items equipped</text>']
    SL, G, X0, Y0, COLS = 72, 8, 48, 96, 6
    pos = []
    for i, (name, ab, cat, st, bl) in enumerate(ITEMS):
        x = X0 + (i % COLS) * (SL + G); y = Y0 + (i // COLS) * (SL + G); pos.append((x, y)); c = CAT[cat]
        o.append(f'<rect x="{x}" y="{y}" width="{SL}" height="{SL}" rx="8" fill="{PANEL}" stroke="{LINE}" stroke-width="2"/>'
                 f'<rect x="{x+10}" y="{y+10}" width="{SL-20}" height="{SL-20}" rx="6" fill="{c}" opacity="0.16"/>'
                 f'<rect x="{x+10}" y="{y+10}" width="{SL-20}" height="{SL-20}" rx="6" fill="none" stroke="{c}" stroke-width="1.5"/>'
                 f'<text x="{x+SL/2}" y="{y+SL/2+8}" text-anchor="middle" font-family="{MONO}" font-size="22" font-weight="800" fill="{c}">{ab}</text>')
    T = 2.4 * len(ITEMS)
    xs = ";".join(str(p[0]) for p in pos); ys = ";".join(str(p[1]) for p in pos)
    o.append(f'<rect x="{pos[0][0]-3}" y="{pos[0][1]-3}" width="{SL+6}" height="{SL+6}" rx="10" fill="none" stroke="{PAPER}" stroke-width="3">'
             f'<animate attributeName="x" values="{";".join(str(p[0]-3) for p in pos)}" calcMode="discrete" dur="{T}s" repeatCount="indefinite"/>'
             f'<animate attributeName="y" values="{";".join(str(p[1]-3) for p in pos)}" calcMode="discrete" dur="{T}s" repeatCount="indefinite"/></rect>')
    # tooltip
    TX, TY, TW, TH = 48, 342, 472, 150
    o.append(f'<rect x="{TX}" y="{TY}" width="{TW}" height="{TH}" rx="12" fill="{PANEL}" stroke="{LINE}"/>')
    for i, (name, ab, cat, st, bl) in enumerate(ITEMS):
        c = CAT[cat]; a, b = i * 2.4, (i + 1) * 2.4
        pts = [(0, 0), (a, 0), (a + 0.02, 1), (b, 1), (b + 0.02, 0)] if i else [(0, 1), (b, 1), (b + 0.02, 0), (T - 0.02, 0), (T, 1)]
        o.append(f'<g opacity="0">{anim("opacity", pts, T)}'
                 f'<rect x="{TX+20}" y="{TY+24}" width="84" height="84" rx="10" fill="{c}" opacity="0.16"/><rect x="{TX+20}" y="{TY+24}" width="84" height="84" rx="10" fill="none" stroke="{c}" stroke-width="2"/>'
                 f'<text x="{TX+62}" y="{TY+78}" text-anchor="middle" font-family="{MONO}" font-size="32" font-weight="800" fill="{c}">{ab}</text>'
                 f'<text x="{TX+126}" y="{TY+46}" font-family="{SANS}" font-size="24" font-weight="800" fill="{PAPER}">{esc(name)}</text>'
                 f'<text x="{TX+126}" y="{TY+70}" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{c}">{cat}</text>'
                 f'<text x="{TX+126}" y="{TY+94}" font-family="{SANS}" font-size="14" font-weight="700" fill="{PAPER}">Status: {st}</text>'
                 f'<text x="{TX+126}" y="{TY+118}" font-family="{SANS}" font-size="13" fill="{MUTED}">{esc(bl)}</text></g>')
    # achievements
    AX, AY, AW, AH = 560, 40, 392, 452
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
        y = AY + 84 + i * 62; ok = v >= tg; col = ORANGE if ok else MUTED; frac = min(1, v / tg)
        icon = (f'<path d="M-8 0l5 6 11-12" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>' if ok else
                f'<rect x="-6" y="-2" width="12" height="9" rx="2" fill="{MUTED}"/><path d="M-4 -2v-3a4 4 0 018 0v3" fill="none" stroke="{MUTED}" stroke-width="2"/>')
        o.append(f'<g opacity="{1 if ok else 0.75}"><circle cx="{AX+40}" cy="{y}" r="17" fill="{ORANGE if ok else LINE}"/><g transform="translate({AX+40} {y})">{icon}</g>'
                 f'<text x="{AX+72}" y="{y-6}" font-family="{SANS}" font-size="16" font-weight="800" fill="{PAPER if ok else MUTED}">{t}</text>'
                 f'<text x="{AX+72}" y="{y+12}" font-family="{SANS}" font-size="12" fill="{MUTED}">{ds}</text>'
                 f'<rect x="{AX+72}" y="{y+20}" width="230" height="4" rx="2" fill="{INK}"/><rect x="{AX+72}" y="{y+20}" width="{230*frac:.1f}" height="4" rx="2" fill="{col}"/>'
                 f'<text x="{AX+AW-24}" y="{y+25}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{col}">{min(v,tg) if ok else v}/{tg}</text></g>')
    return frame(W, H, "".join(o))
