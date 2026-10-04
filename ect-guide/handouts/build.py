"""Build the ECT reference handouts (one PDF per topic).

Run:  python3 build.py
Needs Chromium; set CHROME to override the default path.
"""
import html
import os
import subprocess

CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
HERE = os.path.dirname(os.path.abspath(__file__))

COPPER, TEAL, BLUE, NAVY = "#c4652a", "#1d7f86", "#3b5ba5", "#13294b"

# ---------------------------------------------------------------- figures
GRID = '<path d="M{x} {y0}V{y1}M{x0} {y}H{x1}" stroke="#dfdacd" stroke-width="1"/>'
EIGHT = ("M0 0 C 20 -6, 70 -34, 80 -14 C 88 2, 40 4, 0 0 "
         "C -40 -4, -88 -2, -80 14 C -70 34, -20 6, 0 0 Z")

FIG_FLAW = f"""
<svg viewBox="0 0 230 190" fill="none" font-family="JetBrains Mono" font-size="8">
  {GRID.format(x=115, y0=10, y1=180, x0=10, x1=220, y=95)}
  <text x="12" y="108" fill="#6b7384">probe motion</text>
  <g transform="translate(115 95) rotate(40) scale(1 -1)">
    <line x1="-100" y1="0" x2="100" y2="0" stroke="{NAVY}" stroke-dasharray="3 4"/>
    <path d="{EIGHT}" stroke="{COPPER}" stroke-width="2.6" stroke-linejoin="round"/>
  </g>
  <path d="M80 95 A 35 35 0 0 1 88.2 72.5" stroke="{NAVY}" stroke-width="1.4"/>
  <text x="90" y="108" fill="{NAVY}" text-anchor="middle">≈40°</text>
  <circle cx="115" cy="95" r="3.2" fill="{NAVY}"/>
  <text x="121" y="88" fill="{NAVY}">null</text>
  <text x="12" y="26" fill="{COPPER}">coil A loop</text>
  <text x="218" y="172" fill="{COPPER}" text-anchor="end">coil B loop</text>
  <text x="218" y="22" fill="{NAVY}" text-anchor="end">angle → depth</text>
  <text x="218" y="34" fill="{NAVY}" text-anchor="end">size → volts</text>
</svg>"""

def _blip(x, odd=False):
    if odd:
        return (f'<path d="M{x-12} 62 q4 -26 8 -4 q3 10 5 -8 q3 34 9 10 q4 -8 8 2" '
                f'stroke="{COPPER}" stroke-width="2.4" stroke-linejoin="round"/>'
                f'<circle cx="{x}" cy="60" r="21" stroke="{COPPER}" stroke-dasharray="3 3"/>')
    return f'<path d="M{x-10} 60 q5 -30 10 0 q5 30 10 0" stroke="{TEAL}" stroke-width="2.4"/>'

FIG_SUPPORTS = f"""
<svg viewBox="0 0 230 120" fill="none" font-family="JetBrains Mono" font-size="7.5">
  <line x1="6" y1="60" x2="224" y2="60" stroke="#dfdacd"/>
  {''.join(_blip(x, odd=(x == 151)) for x in (27, 69, 110, 151, 193))}
  {''.join(f'<text x="{x}" y="105" text-anchor="middle" fill="#13294b">TSP {i}</text>'
           for i, x in enumerate((27, 69, 110, 151, 193), 1))}
  <text x="151" y="20" text-anchor="middle" fill="{COPPER}">odd one out</text>
</svg>"""

FIG_MIRROR = f"""
<svg viewBox="0 0 230 140" fill="none" font-family="JetBrains Mono" font-size="8">
  {GRID.format(x=58, y0=12, y1=112, x0=8, x1=108, y=62)}
  {GRID.format(x=172, y0=12, y1=112, x0=122, x1=222, y=62)}
  <g transform="translate(58 62) rotate(40) scale(.55 -.55)">
    <line x1="-100" y1="0" x2="100" y2="0" stroke="{NAVY}" stroke-dasharray="5 6"/>
    <path d="{EIGHT}" stroke="{TEAL}" stroke-width="4.4" stroke-linejoin="round"/></g>
  <g transform="translate(172 62) rotate(40) scale(.55)">
    <line x1="-100" y1="0" x2="100" y2="0" stroke="{NAVY}" stroke-dasharray="5 6"/>
    <path d="{EIGHT}" stroke="{COPPER}" stroke-width="4.4" stroke-linejoin="round"/></g>
  <text x="58" y="128" text-anchor="middle" fill="{TEAL}">✓ matches cal</text>
  <text x="172" y="128" text-anchor="middle" fill="{COPPER}">✗ mirrored</text>
</svg>"""

FIG_DEPTH = f"""
<svg viewBox="0 0 230 160" fill="none" font-family="JetBrains Mono" font-size="7.5">
  <rect x="62" y="8" width="44" height="140" fill="#f1dccd"/>
  <line x1="62" y1="8" x2="62" y2="148" stroke="{NAVY}" stroke-width="2"/>
  <line x1="106" y1="8" x2="106" y2="148" stroke="{NAVY}" stroke-width="2"/>
  <circle cx="128" cy="30" r="9" fill="#cdbfa6"/><circle cx="140" cy="36" r="6" fill="#cdbfa6"/>
  <text x="152" y="34" fill="{NAVY}">deposit</text>
  <text x="62" y="158" text-anchor="middle" fill="{NAVY}">ID</text>
  <text x="106" y="158" text-anchor="middle" fill="{NAVY}">OD</text>
  <text x="84" y="158" text-anchor="middle" fill="#6b7384">wall</text>
  <g stroke-width="3" stroke-linecap="round">
    <line x1="14" y1="54" x2="74" y2="54" stroke="{TEAL}"/>
    <line x1="14" y1="70" x2="90" y2="70" stroke="{TEAL}"/>
    <line x1="14" y1="86" x2="104" y2="86" stroke="{TEAL}"/>
    <line x1="14" y1="112" x2="212" y2="112" stroke="{COPPER}" stroke-dasharray="1 0"/>
  </g>
  <rect x="150" y="98" width="70" height="26" rx="4" fill="#dfe3ea" stroke="{NAVY}"/>
  <text x="185" y="114" text-anchor="middle" fill="{NAVY}">support</text>
  <g fill="{NAVY}"><text x="14" y="50">CH1</text><text x="14" y="66">CH3</text><text x="14" y="82">CH5</text></g>
  <text x="14" y="108" fill="{COPPER}">CH7 (very low)</text>
</svg>"""

def _support_panel(x, label, kind):
    tl, tr = x + 30, x + 50
    tilt = 4 if kind == "edge" else 0
    parts = [
        f'<rect x="{x}" y="60" width="27" height="20" fill="#dfe3ea" stroke="{NAVY}"/>',
        f'<rect x="{x+53}" y="60" width="27" height="20" fill="#dfe3ea" stroke="{NAVY}"/>',
        f'<line x1="{tl-tilt}" y1="6" x2="{tl+tilt}" y2="132" stroke="{NAVY}" stroke-width="2"/>',
        f'<line x1="{tr-tilt}" y1="6" x2="{tr+tilt}" y2="132" stroke="{NAVY}" stroke-width="2"/>',
    ]
    if kind == "full":
        parts += [f'<line x1="{tl+2}" y1="60" x2="{tl+2}" y2="80" stroke="{COPPER}" stroke-width="5"/>',
                  f'<line x1="{tr-2}" y1="60" x2="{tr-2}" y2="80" stroke="{COPPER}" stroke-width="5"/>']
    elif kind == "edge":
        parts += [f'<line x1="{tl+1}" y1="60" x2="{tl+1.5}" y2="67" stroke="{COPPER}" stroke-width="5"/>',
                  f'<line x1="{tr-1}" y1="73" x2="{tr-0.5}" y2="80" stroke="{COPPER}" stroke-width="5"/>']
    else:
        parts += [f'<ellipse cx="{x+20}" cy="55" rx="9" ry="5" fill="#cdbfa6"/>',
                  f'<ellipse cx="{x+60}" cy="56" rx="7" ry="4" fill="#cdbfa6"/>']
    parts.append(f'<text x="{x+40}" y="148" text-anchor="middle" fill="{NAVY}">{label}</text>')
    return "".join(parts)

FIG_WEAR = f"""
<svg viewBox="0 0 250 155" fill="none" font-family="JetBrains Mono" font-size="7.5">
  {_support_panel(2, "full width", "full")}
  {_support_panel(86, "edge wear", "edge")}
  {_support_panel(170, "deposit on top", "deposit")}
</svg>"""

# ---------------------------------------------------------------- content
DOCS = [
    dict(
        file="01-flaw-signals", accent=COPPER, kicker="ECT Reference · 01", title="FLAW SIGNALS",
        banner="ON THE LISSAJOUS",
        intro="What a real flaw looks like on a bobbin differential, and how it should behave.",
        key="Angle tells you depth. Voltage tells you size. A real flaw is clean, closed, repeatable, and shows on more than one channel.",
        sections=[
            ("The shape", None, [
                "Differential: a figure-8, with one loop for each coil as it passes the flaw.",
                "A clean flaw is smooth, closed, and fairly even. It starts and ends at null.",
                "Absolute: a single loop. Better for gradual change like wear or thinning.",
                "Differential is better for sudden change like pits and cracks."]),
            ("Reading the angle", None, [
                "A through-wall hole sits on your reference line (about 40° on most setups).",
                "OD flaws rotate past that line as they get shallower.",
                "ID flaws sit on the other side of the line.",
                "Decide ID or OD before you read depth off the curve."]),
            ("How a real flaw behaves", None, [
                "Shows on more than one frequency, at the same axial spot.",
                "Traces the same way as your cal flaws.",
                "Repeats on a rescan. Noise doesn't.",
                "Doesn't lie flat along the probe-motion line. Flat is usually wobble or lift-off."]),
            ("Which frequency sees what", None, [
                "High frequency (CH1) is most sensitive at the ID surface.",
                "Lower frequencies reach deeper into the wall and help with OD flaws.",
                "Very low frequency is for supports, deposits, and landmarks, not sizing."]),
        ],
        figure=(FIG_FLAW, "Typical through-wall flaw on a differential channel (illustrative)."),
        cards=[("Red flags", "red", [
            "Messy or open shape that doesn't return to null",
            "Shows on one frequency only",
            "Mostly horizontal",
            "Changes from scan to scan",
            "Lobes mirrored compared with the cal flaws"])],
        tips=["Compare every call with the same flaw type on the cal standard.",
              "Size on the channel your procedure names.",
              "Not sure? Flag it. Don't guess."],
    ),
    dict(
        file="02-support-signals", accent=TEAL, kicker="ECT Reference · 02", title="SUPPORT SIGNALS",
        banner="WHAT NORMAL LOOKS LIKE",
        intro="Supports are your landmarks and a common place for damage. Know what normal looks like so the odd one stands out.",
        key="Every support of the same type should look nearly identical. The odd one out is the one to look at.",
        sections=[
            ("What they are", None, [
                "Tube support plates, baffles, and anti-vibration bars (AVBs) in the U-bend.",
                "Usually carbon steel, which is magnetic, so they make a large signal.",
                "Stainless steel supports make a much smaller signal."]),
            ("How they should look", None, [
                "A big signal, usually much larger than a typical flaw.",
                "Strongest on the low frequencies.",
                "Shape depends on plate type (drilled or broached), material, and frequency."]),
            ("How they should act", None, [
                "Regular spacing that matches the drawing. Count them to know where you are.",
                "Same shape, size, and angle at every support of the same type.",
                "After a good mix, only a small, similar residual remains at each one."]),
            ("What to look for", None, [
                "Distortion: an extra loop, a lopsided shape, or a tail the neighbors don't have.",
                "A larger mix residual than the other supports.",
                "Wear from rubbing, best seen on the mix, within the support width.",
                "Dents (DNT), and deposits or sludge, especially on the lower plates.",
                "A missing or extra support. Re-check your count."]),
        ],
        figure=(FIG_SUPPORTS, "Supports in a tube should all match. The distorted one gets a closer look (illustrative)."),
        cards=[("Compare against", "", [
            "Neighboring supports in the same tube",
            "The same support in nearby tubes",
            "The previous inspection, if you have it"])],
        tips=["Count supports from a known landmark in every tube.",
              "Switch to the mix before calling anything at a support.",
              "A bigger residual than its neighbors deserves a second look."],
    ),
    dict(
        file="03-mirrored-lobes", accent=COPPER, kicker="ECT Reference · 03", title="MIRRORED LOBES",
        banner="WHY WE DON'T CALL THEM",
        intro="The transition is still on the ~40° line, but the loops bulge the opposite way from the cal flaws. Here's what that means.",
        key="The angle says through-wall. The loops say it isn't behaving like a wall flaw. Don't size it on the flaw curve.",
        sections=[
            ("Why there are loops at all", "Solid", [
                "A differential channel shows coil A minus coil B.",
                "If the angle stayed exactly the same as the coils passed, you'd get a straight line, not loops.",
                "The loops exist because the angle shifts a little during the pass."]),
            ("Why the angle shifts", "Reasoning", [
                "Directly over the flaw, eddy currents reach it by the shortest path.",
                "Approaching or leaving, they reach it at an angle through more metal, so there's a little more lag.",
                "With a real wall flaw this drift always goes the same way. That's why all your cal flaws open the same way."]),
            ("What mirrored means", None, [
                "The drift runs the opposite way, so the signal doesn't behave like a flaw seen through the wall.",
                "Two things overlapping: a small flaw plus a dent, deposit, or support edge.",
                "A shape or fit change: a ding, dent, or probe wobble.",
                "Something outside the tube: a loose part, deposit, or support."]),
            ("Not the same as a reversed trace", None, [
                "If the whole signal traces backward, check scan direction (push vs. pull) first.",
                "If everything in the tube is reversed, it's setup, not the signal.",
                "A lone reversed signal can mean added material, or the far end of a long flaw (it pairs with the start)."]),
        ],
        figure=(FIG_MIRROR, "Same transition line, loops on opposite sides (illustrative)."),
        cards=[("Check it", "", [
            "Compare with the ID groove and OD flaws on your cal standard",
            "Mirrored on every channel, or only one?",
            "Which way does the absolute channel swing?",
            "Same spot on nearby tubes and previous data"]),
            ("If the ID groove opens this way", "dark", [
                "Some setups may show ID signals like this. Ask your Level III how your procedure treats it."])],
        tips=["Your depth curve only works for signals that behave like the cal flaws.",
              "'Reasoning' sections are physics-based. Confirm with your Level III.",
              "Can't explain it? Flag it."],
    ),
    dict(
        file="04-channel-disagreement", accent=BLUE, kicker="ECT Reference · 04", title="CHANNEL CHECK",
        banner="CH1, 3, 5 AGREE · CH7 DOESN'T",
        intro="What it means when the very low frequency swings into OD but the other differentials tell a consistent story.",
        key="Trust the channels that agree. Very low frequency is for supports, landmarks, and the mix, not for depth.",
        sections=[
            ("Why CH7 acts differently", None, [
                "It reaches well past the tube wall, so it sees supports, deposits, sludge, magnetite, nearby tubes, and loose parts.",
                "It reacts strongly to magnetic material.",
                "Its angle-to-depth spread is very compressed, so small disturbances swing the angle a lot."]),
            ("What's probably happening", None, [
                "CH7 is showing the flaw plus something outside the tube, added together.",
                "The combined signal lands at a different angle, often rotated toward OD."]),
            ("Checks", None, [
                "Does the mix agree with CH1, 3, and 5?",
                "Is it at or near a support, AVB, tube sheet, or sludge pile?",
                "Does CH7 look normal elsewhere in this tube and on the cal standard?",
                "Does the low-frequency absolute show a deposit or gradual change?",
                "What does the same spot look like on nearby tubes?"]),
            ("How to call it", None, [
                "Size on the prime frequency your procedure names.",
                "Use CH7 to explain what's around the flaw, not to decide depth."]),
        ],
        figure=(FIG_DEPTH, "Lower frequencies reach farther. CH7 reaches past the wall to supports and deposits (illustrative)."),
        cards=[("Escalate only if", "dark", [
            "CH7 shows a strong, clean, flaw-shaped signal",
            "None of the other channels or the mix see it",
            "Nothing outside the tube explains it"])],
        tips=["Check which channel your procedure uses for sizing.",
              "A setup problem on CH7 shows up on every signal, not just one.",
              "When channels disagree and you can't explain why, flag it."],
    ),
    dict(
        file="05-wear-at-supports", accent=TEAL, kicker="ECT Reference · 05", title="WEAR AT SUPPORTS",
        banner="EDGE, FULL WIDTH, OR BUILDUP?",
        intro="A sharp signal at one edge of a support can be real edge wear, or something sitting there.",
        key="Wear happens where the tube touches the support. It often spans the full support width. A signal clearly outside the support is probably not wear.",
        sections=[
            ("Where wear happens", None, [
                "Within the support's thickness, where the tube makes contact.",
                "At plates and baffles it often runs the full width of the support.",
                "Heavier at one edge if the tube leans or pivots in the hole (edge wear).",
                "AVBs are thin, so their wear is short and right at the bar."]),
            ("Wear or buildup?", None, [
                "Absolute channel: wall loss swings one way, added material the other.",
                "Trace and lobes on the mix should match your wall-loss cal flaws.",
                "Outside material gets stronger as frequency drops. Wear also shows on high frequencies.",
                "Magnetic buildup is very strong on the very low frequency."]),
            ("Location clues", None, [
                "In vertical units, deposits settle on the top of support plates.",
                "Edge wear tends to be on the same edge at several supports if the tube leans.",
                "A cluster of tubes at the same height suggests a loose part or deposit pile.",
                "A loose part can also cause wear. Many sites code it PLP."]),
            ("History and confirmation", None, [
                "Wear grows slowly and stays put between inspections.",
                "Deposits and loose parts can appear, move, or disappear.",
                "A rotating probe (+Point or RPC) can confirm what it is.",
                "A suspected loose part may justify a secondary-side visual."]),
        ],
        figure=(FIG_WEAR, "Three ways a signal can sit at a support (illustrative)."),
        cards=[("Before you call WAR", "dark", [
            "Wall-loss direction confirmed",
            "Lines up with the support location",
            "Not explained by buildup or a loose part"])],
        tips=["Don't size it as WAR until wall loss is confirmed.",
              "Check the same support on neighboring tubes.",
              "A sharp signal at the edge is a fair reason to escalate."],
    ),
    dict(
        file="06-sizing-sharp-wear", accent=BLUE, kicker="ECT Reference · 06", title="SIZING SHARP WEAR",
        banner="M1 DIFFERENTIAL OR M2 ABSOLUTE?",
        intro="Wall-loss direction, very sharp, right at the support edge, and the absolute reads much deeper. Which number do you use?",
        key="Pick the code first. The code picks the channel. WAR is sized on M2 absolute, after you check the number isn't inflated.",
        table=(["", "Differential (M1)", "Absolute (M2)"], [
            ["Sees", "Only the change between two close coils", "The whole change in one coil"],
            ["Best for", "Small, localized flaws like pits", "Gradual or flat wall loss like wear and thinning"],
            ["Sharp or long flaws", "Tends to under-call: sees edges, coils partly cancel", "Closer to the full depth"],
            ["Weak spots", "Misses gradual change", "Residual, wobble, drift, and where you put the endpoints"],
        ]),
        sections=[
            ("Decide the code", None, [
                "Wall loss at a support from contact: WAR, sized on M2.",
                "A localized pit that happens to sit at the support: ODI, called on M1.",
                "The code decides the channel, not which number looks more believable."]),
            ("Sanity-check M2", None, [
                "Measure M2 at clean supports in the same tube. A baseline offset there means part of your reading is residual.",
                "Re-check the null and measurement points. On a sharp signal a small shift changes the percentage a lot.",
                "Confirm M2 was calibrated per procedure. Many sites use a wear standard, not drilled holes, for the wear curve."]),
            ("If it still reads much deeper", None, [
                "Don't quietly pick the smaller number.",
                "The usual NDE approach is to report conservatively and flag it. Your procedure decides.",
                "A rotating-probe exam would settle the shape and depth."]),
        ],
        figure=None,
        cards=[("Never", "red", [
            "Average the two channels",
            "Pick the smaller number to avoid a call",
            "Size wear on a drilled-hole curve without checking procedure"]),
            ("Escalate when", "dark", [
                "M2 and M1 disagree by a lot after your checks",
                "You can't tell wear from a pit"])],
        tips=["Code first, channel second.",
              "Big channel disagreement is a reason to flag on its own.",
              "Your procedure decides how conservative to be."],
    ),
    dict(
        file="07-wear-vs-erosion", accent=COPPER, kicker="ECT Reference · 07", title="WEAR OR EROSION?",
        banner="TUBE-TO-TUBE WEAR VS. EROSION",
        intro="Two kinds of wall loss that can look alike. Location and the neighboring tube usually settle it.",
        key="Ask two things: where is it, and does the tube next door have the same thing at the same spot?",
        table=(["", "Tube-to-tube wear", "Erosion"], [
            ["Where", "Free span between supports, often mid-span or in the U-bend", "Usually the inlet end, just past the tube sheet. Sometimes near the shell inlet or impingement area"],
            ["ID or OD", "OD: tubes rub on each other's outside", "Inlet erosion is usually ID. Impingement erosion is OD"],
            ["Shape", "Fairly localized: a defined spot or short length", "Gradual and long: a slow drift on the absolute"],
            ["Neighbor tube", "Matching wear at the same spot", "No matching partner. Many tubes in the same region"],
            ["Low frequency", "Often a proximity signal from close tubes", "Nothing special"],
        ]),
        sections=[
            ("Location first", None, [
                "Inlet end near the tube sheet: think erosion.",
                "Free span or U-bend, away from supports: think tube-to-tube wear."]),
            ("Check the neighbor", "Strongest test", [
                "Tube-to-tube wear takes two tubes, so both should show wall loss at the same spot.",
                "If the neighbor is clean there, tube-to-tube wear is unlikely."]),
            ("ID or OD, shape, proximity", None, [
                "ID signals are strongest on CH1. Tube-to-tube wear is always OD.",
                "Erosion starts gradually and fades out. Tube-to-tube wear is a defined spot.",
                "A proximity signal on the low-frequency absolute supports tube-to-tube wear."]),
        ],
        figure=None,
        cards=[("The tricky case", "dark", [
            "OD erosion near the shell inlet can sit in the free span and look like tube-to-tube wear",
            "Partner tube plus proximity signal: tube-to-tube wear",
            "No partner, broad area across tubes facing the inlet: erosion"]),
            ("Bundle pattern", "", [
                "Erosion: many tubes in the same region",
                "Tube-to-tube: pairs of adjacent tubes"])],
        tips=["Always look up the adjacent tube at the same elevation.",
              "Your site may code tube-to-tube wear separately. Check your list.",
              "Can't tell which it is? Flag it."],
    ),
]

# ---------------------------------------------------------------- render
WAVES = """<svg width="0" height="0" style="position:absolute"><defs>
<pattern id="wv" width="160" height="60" patternUnits="userSpaceOnUse">
<path d="M0 30 Q 20 5 40 30 T 80 30 T 120 30 T 160 30" fill="none" stroke="#e6dfcf" stroke-width="7" stroke-linecap="round"/>
</pattern></defs></svg>"""

e = html.escape

def render(d):
    secs = []
    for i, (head, tag, items) in enumerate(d["sections"], 1):
        tag_html = f'<span class="tag{" warn" if tag == "Reasoning" else ""}">{e(tag)}</span>' if tag else ""
        lis = "".join(f"<li>{e(t)}</li>" for t in items)
        secs.append(f'<div class="sec"><div class="head"><div class="num">{i}</div>'
                    f'<div class="pill">{e(head)}</div>{tag_html}</div><ul>{lis}</ul></div>')
    side = []
    if d.get("figure"):
        svg, cap = d["figure"]
        side.append(f'<div class="card fig">{svg}<div class="cap">{e(cap)}</div></div>')
    for title, kind, items in d["cards"]:
        lis = "".join(f"<li>{e(t)}</li>" for t in items)
        side.append(f'<div class="card {kind}"><h4>{e(title)}</h4><ul>{lis}</ul></div>')
    table = ""
    if d.get("table"):
        head, rows = d["table"]
        ths = "".join(f"<th>{e(h)}</th>" for h in head)
        trs = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in rows)
        table = f'<table class="cmp full"><tr>{ths}</tr>{trs}</table>'
    tips = "".join(f"<div>{e(t)}</div>" for t in d["tips"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{e(d['title'].title())}</title>
<link rel="stylesheet" href="handout.css"><style>:root {{ --accent: {d['accent']}; }}</style></head>
<body>{WAVES}
<section class="page">
  <svg class="waves" width="100%" height="100%"><rect width="100%" height="100%" fill="url(#wv)"/></svg>
  <header><div class="kicker">{e(d['kicker'])}</div><h1>{e(d['title'])}</h1>
    <div class="banner">{e(d['banner'])}</div><p class="intro">{e(d['intro'])}</p></header>
  <div class="key"><b>KEY IDEA</b><p>{e(d['key'])}</p></div>
  <div class="main">{table}<div>{''.join(secs)}</div><div>{''.join(side)}</div></div>
  <div class="tips"><div class="t">QUICK<br>TIPS</div>{tips}</div>
  <footer><span>Draft · check names &amp; values against your site procedure</span><span>{e(d['kicker'])}</span></footer>
</section></body></html>"""

if __name__ == "__main__":
    for d in DOCS:
        src = os.path.join(HERE, d["file"] + ".html")
        with open(src, "w") as f:
            f.write(render(d))
        subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        "--virtual-time-budget=10000", f"--print-to-pdf={os.path.join(HERE, d['file'] + '.pdf')}",
                        "file://" + src], check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        print("built", d["file"])
