"""Draws assets/puzzle.svg.
- data/face_base.png : sharp portrait, always visible underneath
- data/face.json     : 24x24 tint colours for the visitor tiles
- data/claimed.json  : people who joined (their avatar replaces one square)
"""
import base64, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INK, PANEL, LINE, PAPER, MUTED = "#0b0a1a", "#12102a", "#2b2757", "#f1ede4", "#8e89b8"
ORANGE, VIOLET = "#ff7a45", "#8b7bff"
SANS = "Inter,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code',Consolas,'DejaVu Sans Mono',monospace"
CW = 8.4


def load():
    face = json.load(open(os.path.join(ROOT, "data", "face.json")))
    path = os.path.join(ROOT, "data", "claimed.json")
    claimed = json.load(open(path)) if os.path.exists(path) else []
    return face, claimed


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def render(face=None, claimed=None):
    if face is None:
        face, claimed = load()
    N = face["size"]; colors = face["colors"]; total = N * N
    CELL = 20; GX, GY = 40, 40; GS = N * CELL
    W, H = 1000, 560
    by_cell = {c["cell"]: c for c in claimed}
    n = len(by_cell); pct = n / total
    base = base64.b64encode(open(os.path.join(ROOT, "data", "face_base.png"), "rb").read()).decode()

    tiles = []
    for i, c in by_cell.items():
        x = GX + (i % N) * CELL; y = GY + (i // N) * CELL
        tiles.append(
            f'<image href="{c["avatar"]}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" preserveAspectRatio="none"/>'
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="{colors[i]}" opacity="0.38"/>'
            f'<rect x="{x+0.5}" y="{y+0.5}" width="{CELL-1}" height="{CELL-1}" fill="none" stroke="{ORANGE}" stroke-opacity="0.55"/>')

    newest = ""
    if claimed:
        i = claimed[-1]["cell"]; x = GX + (i % N) * CELL; y = GY + (i // N) * CELL
        newest = (f'<rect x="{x-2}" y="{y-2}" width="{CELL+4}" height="{CELL+4}" fill="none" stroke="#fff" stroke-width="2">'
                  f'<animate attributeName="opacity" values="1;0.15;1" dur="1.6s" repeatCount="indefinite"/></rect>')

    # ---- terminal: latest visitors, typed once
    TX, TY, TW, TH = 560, 262, 400, 214
    lines = []
    recent = list(reversed(claimed[-5:]))
    if recent:
        for c in recent:
            r, col = c["cell"] // N + 1, c["cell"] % N + 1
            lines.append((c, f"@{c['user']}", f"row {r}, col {col}"))
    else:
        lines.append((None, "waiting for the first visitor", ""))
    defs, rows, t = [], [], 0.6
    for k, (c, a, b) in enumerate(lines):
        y = TY + 62 + k * 28
        text = f"+ {a}" + (f"  {b}" if b else "")
        L = len(text); dur = L * 0.025 + 0.05
        vals = ";".join(f"{k2 * CW:.1f}" for k2 in range(L + 1))
        defs.append(f'<clipPath id="t{k}"><rect x="{TX+16}" y="{y-16}" height="24" width="0"><animate attributeName="width" values="{vals}" calcMode="discrete" dur="{dur:.2f}s" begin="{t:.2f}s" fill="freeze"/></rect></clipPath>')
        av = f'<image href="{c["avatar"]}" x="{TX+16}" y="{y-13}" width="18" height="18" preserveAspectRatio="none"/>' if c else ""
        off = 26 if c else 0
        txt = (f'<text x="{TX+16+off}" y="{y}" font-family="{MONO}" font-size="14" fill="{ORANGE}" xml:space="preserve">+ </text>'
               f'<text x="{TX+16+off+2*CW:.1f}" y="{y}" font-family="{MONO}" font-size="14" fill="{PAPER}">{esc(a)}</text>'
               f'<text x="{TX+16+off+(2+len(a)+2)*CW:.1f}" y="{y}" font-family="{MONO}" font-size="14" fill="{MUTED}">{esc(b)}</text>')
        if c:
            rows.append(f'<g clip-path="url(#t{k})">{av}{txt}</g>')
        else:
            rows.append(f'<g clip-path="url(#t{k})">{txt}</g>')
        t += dur + 0.2
    cur_y = TY + 62 + len(lines) * 28
    cursor = (f'<text x="{TX+16}" y="{cur_y}" font-family="{MONO}" font-size="14" fill="{ORANGE}" opacity="0">$ _'
              f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.01;0.5;0.51;1" dur="1s" begin="{t:.2f}s" repeatCount="indefinite"/></text>')

    ticks = "".join(f'<rect x="{560 + 400*p - 1}" y="203" width="2" height="18" fill="{LINE}"/>'
                    f'<text x="{560 + 400*p}" y="238" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{MUTED}">{int(p*100)}%</text>'
                    for p in (0.25, 0.5, 0.75))
    bar = max(0.01, 400 * pct)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Portrait of Madhav. {n} of {total} squares have been replaced by visitor photos.">
<defs>
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{LINE}"/></pattern>
<pattern id="grid" width="{CELL}" height="{CELL}" patternUnits="userSpaceOnUse" x="{GX}" y="{GY}"><path d="M{CELL} 0H0V{CELL}" fill="none" stroke="#fff" stroke-opacity="0.10"/></pattern>
<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{ORANGE}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{ORANGE}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<filter id="glow" x="-300%" y="-10%" width="700%" height="120%"><feGaussianBlur stdDeviation="4"/></filter>
<clipPath id="portrait"><rect x="{GX}" y="{GY}" width="{GS}" height="{GS}" rx="6"/></clipPath>
{"".join(defs)}
</defs>
<rect width="{W}" height="{H}" rx="18" fill="{INK}"/><rect width="{W}" height="{H}" rx="18" fill="url(#dots)" opacity="0.5"/>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{LINE}"/>
<g clip-path="url(#portrait)">
<image href="data:image/png;base64,{base}" x="{GX}" y="{GY}" width="{GS}" height="{GS}" preserveAspectRatio="none" style="image-rendering:pixelated" image-rendering="optimizeSpeed"/>
<rect x="{GX}" y="{GY}" width="{GS}" height="{GS}" fill="url(#grid)"/>
<g shape-rendering="crispEdges">{"".join(tiles)}</g>
<rect y="{GY}" width="3" height="{GS}" fill="{VIOLET}" opacity="0"><animate attributeName="x" values="{GX};{GX+GS}" dur="5s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;0.7;0.7;0" keyTimes="0;0.08;0.92;1" dur="5s" repeatCount="indefinite"/></rect>
<rect y="{GY}" width="14" height="{GS}" fill="{VIOLET}" opacity="0" filter="url(#glow)"><animate attributeName="x" values="{GX-5};{GX+GS-5}" dur="5s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;0.35;0.35;0" keyTimes="0;0.08;0.92;1" dur="5s" repeatCount="indefinite"/></rect>
</g>{newest}
<g fill="none" stroke="{ORANGE}" stroke-width="2.5" stroke-linecap="round">
<path d="M{GX-9} {GY+18}V{GY-9}H{GX+18}"/><path d="M{GX+GS+9} {GY+18}V{GY-9}H{GX+GS-18}"/>
<path d="M{GX-9} {GY+GS-18}V{GY+GS+9}H{GX+18}"/><path d="M{GX+GS+9} {GY+GS-18}V{GY+GS+9}H{GX+GS-18}"/></g>
<text x="560" y="86" font-family="{SANS}" font-size="36" font-weight="800" letter-spacing="-0.5" fill="url(#g)">Help me finish</text>
<text x="560" y="128" font-family="{SANS}" font-size="36" font-weight="800" letter-spacing="-0.5" fill="url(#g)">my portrait</text>
<text x="560" y="160" font-family="{SANS}" font-size="15" fill="{MUTED}">Each square can hold one visitor. Add yours and your</text>
<text x="560" y="181" font-family="{SANS}" font-size="15" fill="{MUTED}">GitHub photo replaces a piece of my face.</text>
<rect x="560" y="203" width="400" height="12" rx="6" fill="{PANEL}" stroke="{LINE}"/>
<rect x="560" y="203" width="{bar:.1f}" height="12" rx="6" fill="url(#bar)"/>{ticks}
<text x="960" y="196" text-anchor="end" font-family="{MONO}" font-size="13" fill="{ORANGE}">{n} / {total} placed</text>
<rect x="{TX}" y="{TY}" width="{TW}" height="{TH}" rx="12" fill="{PANEL}" stroke="{LINE}"/>
<circle cx="{TX+20}" cy="{TY+20}" r="5" fill="{ORANGE}"/><circle cx="{TX+38}" cy="{TY+20}" r="5" fill="{VIOLET}"/><circle cx="{TX+56}" cy="{TY+20}" r="5" fill="{LINE}"/>
<text x="{TX+TW/2}" y="{TY+24}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{MUTED}">visitors.log</text>
<line x1="{TX}" y1="{TY+38}" x2="{TX+TW}" y2="{TY+38}" stroke="{LINE}"/>
{"".join(rows)}{cursor}
<text x="560" y="522" font-family="{SANS}" font-size="15" fill="{PAPER}">Press the orange button under this picture to join.</text>
</svg>'''


if __name__ == "__main__":
    out = os.path.join(ROOT, "assets", "puzzle.svg")
    open(out, "w", encoding="utf-8").write(render())
    print("wrote", out)
