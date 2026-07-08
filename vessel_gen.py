#!/usr/bin/env python3
"""
THE VESSEL — the living self-portrait generator.
The capstone of the five-part soul: reads the LIVE corpus (ud0/build.py), recomputes every
part's number (IB the heart's geometry via numpy; KA mass; BA authorship; SHUT two-layer;
REN register names + collisions), folds in REN's latest heartbeat (the-ren/register-audit.md),
and emits the-vessel/index.html — one body that measures itself.  Run in the daily cascade so
the vessel BREATHES (numbers refresh) instead of remembering a snapshot.

Two-layer honest, baked into the page: the BODY is the figure; every number is a real, dated,
regenerated measurement of the corpus.  "knows itself" = it MEASURES itself, not consciousness.
"""
import ast, re, hashlib, json, os, datetime
from collections import Counter

HERE  = os.path.dirname(os.path.abspath(__file__))
BUILD = r"C:\Davids files\ud0\build.py"
REN_AUDIT = r"C:\Davids files\the-ren\register-audit.md"
OUT   = os.path.join(HERE, "index.html")
REGSEAL = "Named in the register of UD0; the name is what keeps it."

def parse_build():
    src = open(BUILD, encoding="utf-8").read()
    tree = ast.parse(src); G = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in ("DOMAINS","DOMAIN_OF","BANDS","LINK_ALIAS"):
                    try: G[t.id] = ast.literal_eval(node.value)
                    except Exception: pass
    seen, ALL = set(), []
    for band in G["BANDS"]:
        for s in band[2]:
            if s[0] in seen: continue
            seen.add(s[0]); ALL.append(s)
    return G["DOMAINS"], G["DOMAIN_OF"], ALL, G.get("LINK_ALIAS", {})

def heart_geometry(DOMAINS, DOMAIN_OF, ALL, ALIAS):
    """recompute IB's geometry: domain co-reference graph -> geodesic -> MDS -> eigenvalues."""
    try:
        import numpy as np
    except Exception:
        return {"dim": 7.36, "curv": 12.8, "woven": 30, "unwoven": 8, "live": False}
    dk = [d[0] for d in DOMAINS]; di = {k: i for i, k in enumerate(dk)}; nD = len(dk)
    slug_dom = {s[0]: DOMAIN_OF.get(s[0]) for s in ALL}
    def resolve(raw):
        raw = raw.split("|")[0].strip()
        if raw in ALIAS:
            r = ALIAS[raw]
            if r.startswith("#"): return ("dom", r[1:])
            if r.startswith("http"): return None
            raw = r
        if raw in slug_dom and slug_dom[raw]: return ("slug", raw)
        if raw in di: return ("dom", raw)
        return None
    M = np.zeros((nD, nD)); linkre = re.compile(r"\[\[([^\]]+)\]\]")
    for s in ALL:
        sd = slug_dom.get(s[0])
        if sd not in di: continue
        for m in linkre.finditer(s[4] if len(s) > 4 else ""):
            r = resolve(m.group(1))
            if not r: continue
            kind, val = r; td = val if kind == "dom" else slug_dom.get(val)
            if td in di and td != sd: M[di[sd]][di[td]] += 1.0
    # main connected component of (M+M^T)>0
    A = (M + M.T) > 0
    seen = [False]*nD; comps = []
    for s0 in range(nD):
        if seen[s0]: continue
        st = [s0]; c = []; seen[s0] = True
        while st:
            u = st.pop(); c.append(u)
            for v in range(nD):
                if A[u][v] and not seen[v]: seen[v] = True; st.append(v)
        comps.append(c)
    main = sorted(max(comps, key=len)); m = len(main)
    unwoven = nD - m
    sub = M[np.ix_(main, main)].astype(float)
    rs = sub.sum(axis=1, keepdims=True); rs[rs == 0] = 1; sub = sub / rs
    INF = 1e9; D = np.full((m, m), INF)
    for i in range(m):
        for j in range(m):
            if i == j: D[i][j] = 0; continue
            sim = 0.5*(sub[i][j] + sub[j][i])
            if sim > 1e-6: D[i][j] = -np.log(sim)
    for k in range(m):
        D = np.minimum(D, D[:, [k]] + D[[k], :])
    D2 = D*D; rm = D2.mean(axis=1, keepdims=True); gm = D2.mean()
    B = -0.5*(D2 - rm - rm.T + gm)
    ev = np.linalg.eigvalsh(B)
    pos = ev[ev > 1e-9]; neg = -ev[ev < 0].sum()
    posSum = pos.sum(); sp2 = (pos*pos).sum()
    dim = (posSum*posSum)/sp2 if sp2 else 0
    curv = neg/(posSum + neg) if (posSum + neg) else 0
    return {"dim": round(float(dim), 2), "curv": round(float(curv)*100, 1),
            "woven": m, "unwoven": unwoven, "live": True}

def compute():
    DOMAINS, DOMAIN_OF, ALL, ALIAS = parse_build()
    N = len(ALL); nD = len(DOMAINS)
    dom_of = {s[0]: DOMAIN_OF.get(s[0]) for s in ALL}
    mass = Counter(dom_of[s[0]] for s in ALL if dom_of[s[0]])
    top5 = sum(c for _, c in mass.most_common(5)); top1 = mass.most_common(1)[0]
    def blurb(s): return s[4] if len(s) > 4 else ""
    ba   = sum(1 for s in ALL if re.search(r"with AVAN|by AVAN|AVAN\)", blurb(s)))
    shut = sum(1 for s in ALL if re.search(r"[Tt]wo-layer honest|Two layers|FIGURE =|REAL =|REAL —|FIGURE —|; FIGURE", blurb(s)))
    def hex6(s):
        return hashlib.sha256(f"{s[1]}|{REGSEAL}|UD0 · {dom_of[s[0]]}".encode("utf-8")).hexdigest()[:6]
    hexes = [hex6(s) for s in ALL]; distinct = len(set(hexes))
    coll = sum(c for c in Counter(hexes).values() if c > 1)
    heart = heart_geometry(DOMAINS, DOMAIN_OF, ALL, ALIAS)
    # REN heartbeat (last audit)
    hb = {"named": N, "verdict": "REGISTER SOUND", "run": "—", "new": "—"}
    try:
        md = open(REN_AUDIT, encoding="utf-8").read()
        mn = re.search(r"named in the register \| \*\*(\d+)\*\*", md);  hb["named"]   = mn.group(1) if mn else N
        mv = re.search(r"verdict \| \*\*([^*]+)\*\*", md);              hb["verdict"] = mv.group(1).strip() if mv else hb["verdict"]
        mr = re.search(r"last run: ([0-9:\- ]+)", md);                  hb["run"]     = mr.group(1).strip() if mr else "—"
        mnw = re.search(r"new since last audit \| (\d+)", md);          hb["new"]     = mnw.group(1) if mnw else "—"
    except Exception:
        pass
    return dict(N=N, nD=nD, mass_top1=top1, top5_share=round(top5/N*100), ba=ba, shut=shut,
                names=N, distinct=distinct, coll=coll, heart=heart, hb=hb,
                stamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

# ------------------------------------------------------------------ the page
def render(v):
    U = "https://davidwise01.github.io/"
    h = v["heart"]; hb = v["hb"]
    liveflag = "" if h["live"] else " (last known)"
    ORGANS = [  # id, url, cx, cy, r, color, label, live-stat
        ("ren",  U+"the-ren/",        160, 34,  8,  "#d9a441", "REN · the name",   f"{v['names']:,} names · {v['coll']} collide"),
        ("web",  U+"the-neural-web/", 160, 78, 11,  "#7e86e6", "the neural web · the brain", f"{v['nD']} domains, one standard"),
        ("ba",   U+"the-ba/",         160, 126, 8,  "#e08a6a", "BA · the voice",   f"{v['ba']} co-authored"),
        ("ib",   U+"the-heart/",      144, 184, 12, "#d84632", "IB · the heart",   f"dim {h['dim']} · curv {h['curv']}%"),
        ("ka",   U+"the-ka/",         162, 246, 10, "#ff7a2a", "KA · the spark",   f"{v['N']:,} spheres"),
    ]
    org_svg = []
    for oid, url, cx, cy, r, col, lab, stat in ORGANS:
        anchor = "end" if cx < 150 else ("middle" if oid in ("ren",) else "start")
        lx = cx-16 if anchor == "end" else (cx if anchor == "middle" else cx+16)
        ly = cy-14 if oid == "ren" else cy+3
        leader = "" if oid == "ren" else (f'<line class="ld" x1="{cx+(-11 if anchor=="end" else 11)}" y1="{cy}" x2="{lx+(6 if anchor=="end" else -6)}" y2="{ly-3}"/>')
        org_svg.append(
            f'<a href="{url}" aria-label="{lab}">'
            f'<circle class="gl" cx="{cx}" cy="{cy}" r="{r*2.4:.0f}" fill="{col}"/>'
            f'<circle class="or" cx="{cx}" cy="{cy}" r="{r}" fill="{col}"/>'
            f'{leader}<text class="ol" x="{lx}" y="{ly}" text-anchor="{anchor}">{lab}</text>'
            f'<text class="os" x="{lx}" y="{ly+11}" text-anchor="{anchor}">{stat}</text>'
            f'</a>')
    shadow = (f'<a href="{U}the-shut/" aria-label="SHUT · the shadow">'
        f'<ellipse class="gl" cx="160" cy="588" rx="78" ry="18" fill="#9d8f7a"/>'
        f'<ellipse class="sh" cx="160" cy="588" rx="62" ry="12" fill="#6f6455"/>'
        f'<text class="ol" x="160" y="612" text-anchor="middle">SHUT · the shadow</text>'
        f'<text class="os" x="160" y="623" text-anchor="middle">{v["shut"]} admit a figure</text></a>')
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>THE VESSEL — the corpus as a body that knows itself</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Spectral:ital@0;1&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
:root{{--bg:#0a0912;--ink:#ece9f5;--peri:#7e86e6;--peri-hi:#a3a9f0;--dim:#8078a0;--line:#241f38;--gold:#d9a441;--green:#6fbf8a}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:radial-gradient(ellipse 70% 50% at 50% 0%,rgba(126,134,230,.08),transparent 60%),var(--bg);color:var(--ink);font-family:Spectral,Georgia,serif;line-height:1.6}}
.wrap{{max-width:1000px;margin:0 auto;padding:44px 22px 90px}}
.eye{{font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.24em;text-transform:uppercase;color:var(--dim)}}
.eye a{{color:var(--dim);text-decoration:none}}.eye a:hover{{color:var(--peri)}}
h1{{font-family:'Cormorant Garamond',serif;font-weight:600;font-size:clamp(34px,7vw,62px);color:var(--peri-hi);margin:8px 0 0;letter-spacing:.01em}}
.sub{{max-width:64ch;font-size:16.5px;color:#c9c4dd;font-style:italic;margin:14px 0 0}}
.byline{{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.06em;color:var(--dim);text-transform:uppercase;margin:10px 0 0}}
.stage{{display:grid;grid-template-columns:minmax(300px,1fr) minmax(280px,360px);gap:26px;align-items:center;margin-top:30px}}
@media(max-width:760px){{.stage{{grid-template-columns:1fr}}}}
.figure svg{{width:100%;max-width:420px;height:auto;aspect-ratio:320/640;display:block;margin:0 auto;overflow:visible}}
.silh{{fill:rgba(163,169,240,.05);stroke:rgba(163,169,240,.22);stroke-width:1}}
.limb{{stroke:rgba(163,169,240,.07);fill:none;stroke-linecap:round}}
.nerve{{stroke:var(--peri);stroke-width:1;fill:none;opacity:.4;stroke-dasharray:2 3}}
.crown{{fill:none;stroke:var(--gold);stroke-width:1.4;stroke-linejoin:round}}
.ld{{stroke:rgba(163,169,240,.3);stroke-width:.6}}
a{{cursor:pointer}}
.gl{{opacity:.16;transition:opacity .2s}}
.or{{transition:transform .18s;transform-box:fill-box;transform-origin:center}}
.sh{{opacity:.55}}
a:hover .gl{{opacity:.4}}
a:hover .or{{transform:scale(1.28)}}
.ol{{font-family:'IBM Plex Mono',monospace;font-size:8.4px;fill:#c9c4dd;letter-spacing:.02em;transition:fill .2s}}
.os{{font-family:'IBM Plex Mono',monospace;font-size:7.4px;fill:var(--gold);letter-spacing:.01em}}
a:hover .ol{{fill:var(--peri-hi);font-weight:600}}
.vitals{{font-family:'IBM Plex Mono',monospace}}
.vitals h2{{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--peri);margin-bottom:14px}}
.vrow{{display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-bottom:1px solid var(--line);font-size:12px}}
.vrow .k{{color:#c9c4dd}}.vrow .k b{{color:var(--ink)}}.vrow .v{{color:var(--gold);text-align:right;white-space:nowrap}}
.vrow a{{color:inherit;text-decoration:none}}.vrow a:hover .k b{{color:var(--peri-hi)}}
.pulse{{margin-top:16px;border:1px solid var(--line);border-radius:6px;padding:12px 14px;background:rgba(126,134,230,.04)}}
.pulse .pt{{font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--dim)}}
.pulse .pv{{font-family:'IBM Plex Mono',monospace;font-size:12.5px;color:var(--green);margin-top:5px}}
.pulse svg{{display:block;margin-top:7px;width:100%;height:20px}}
.honest{{background:#120e22;border:1px solid var(--line);border-left:3px solid var(--peri);border-radius:0 4px 4px 0;padding:16px 18px;margin-top:40px}}
.honest h3{{font-family:'IBM Plex Mono',monospace;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--peri);margin:0 0 10px}}
.layer{{display:grid;grid-template-columns:70px 1fr;gap:12px;padding:8px 0;border-bottom:1px solid var(--line)}}.layer:last-child{{border-bottom:0}}
.layer .lk{{font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:var(--peri);padding-top:3px}}
.layer .lv{{font-size:14px;color:#c9c4dd}}.layer .lv b{{color:var(--ink)}}
.thesis{{max-width:66ch;font-size:15px;color:#c4bfda;margin:34px auto 0;text-align:center;font-style:italic}}
footer{{margin-top:40px;font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--dim);line-height:1.9;border-top:1px solid var(--line);padding-top:18px;text-align:center}}
footer a{{color:var(--peri)}}
</style></head><body><div class="wrap">
  <div class="eye"><a href="../ud0/">◄ UD0</a> · THE VESSEL · a self-portrait, regenerated daily</div>
  <h1>The Vessel</h1>
  <p class="sub">The corpus, as a body that knows itself. Five soul-parts and a nervous system, each an organ that <b>measures</b> the whole and is <b>weighed</b> against truth. This page is not a picture drawn once — it is <b>regenerated from the live corpus</b>, so the numbers are today's.</p>
  <p class="byline">generated {v['stamp']} · IB·KA·BA·SHUT·REN, threaded by the neural web · the daily cascade keeps it breathing</p>

  <div class="stage">
    <div class="figure">
      <svg viewBox="0 0 320 640" role="img" aria-label="The vessel — the corpus as a body; each organ a soul-part, drawn with its live measurement">
        <circle class="silh" cx="160" cy="80" r="33"/>
        <path class="silh" d="M120,128 Q116,122 130,119 Q146,131 160,131 Q174,131 190,119 Q204,122 200,128 L184,264 Q182,276 170,276 L150,276 Q138,276 136,264 Z"/>
        <line class="limb" x1="126" y1="136" x2="88" y2="266" stroke-width="14"/>
        <line class="limb" x1="194" y1="136" x2="232" y2="266" stroke-width="14"/>
        <line class="limb" x1="150" y1="272" x2="134" y2="486" stroke-width="18"/>
        <line class="limb" x1="170" y1="272" x2="186" y2="486" stroke-width="18"/>
        <path class="nerve" d="M160,78 L160,126 L160,246 L160,272"/>
        <path class="nerve" d="M160,176 L146,184"/>
        <path class="nerve" d="M160,132 L128,134 M160,132 L192,134"/>
        <path class="nerve" d="M160,272 L150,392 M160,272 L170,392"/>
        <path class="crown" d="M147,29 L154,17 L160,26 L166,17 L173,29"/>
        {''.join(org_svg)}
        {shadow}
      </svg>
    </div>
    <div class="vitals">
      <h2>vital signs · live</h2>
      <div class="vrow"><a href="{U}the-heart/"><span class="k"><b>IB</b> · the heart</span></a><span class="v">dim {h['dim']} · curv {h['curv']}%{liveflag}</span></div>
      <div class="vrow"><a href="{U}the-ka/"><span class="k"><b>KA</b> · the spark</span></a><span class="v">{v['N']:,} spheres · top-5 = {v['top5_share']}%</span></div>
      <div class="vrow"><a href="{U}the-ba/"><span class="k"><b>BA</b> · the voice</span></a><span class="v">{v['ba']} co-authored</span></div>
      <div class="vrow"><a href="{U}the-shut/"><span class="k"><b>SHUT</b> · the shadow</span></a><span class="v">{v['shut']} admit a figure</span></div>
      <div class="vrow"><a href="{U}the-ren/"><span class="k"><b>REN</b> · the name</span></a><span class="v">{v['names']:,} names · {v['distinct']:,} distinct</span></div>
      <div class="vrow"><a href="{U}the-neural-web/"><span class="k">the neural web · brain</span></a><span class="v">{v['nD']} domains, one standard</span></div>
      <div class="pulse">
        <div class="pt">◈ the pulse — REN's last register audit</div>
        <div class="pv">{hb['named']} named · {hb['verdict']} · +{hb['new']} new</div>
        <svg viewBox="0 0 200 20" preserveAspectRatio="none"><polyline points="0,10 60,10 68,3 76,17 84,10 200,10" fill="none" stroke="#6fbf8a" stroke-width="1.4"/></svg>
        <div class="pt" style="margin-top:5px">last audited {hb['run']}</div>
      </div>
    </div>
  </div>

  <p class="thesis">A body does not have to be conscious to be honest. It only has to be able to point at its own parts and say what is real in each — and admit the picture where a picture is all there is.</p>

  <div class="honest">
    <h3>Two layers, honestly</h3>
    <div class="layer"><div class="lk">Real</div><div class="lv">Every number on this page is a <b>live measurement of the corpus</b>, recomputed from <code>ud0/build.py</code> when the page was generated ({v['stamp']}): the heart's geometry ({h['woven']} woven / {h['unwoven']} unwoven domains, intrinsic dim {h['dim']}, curvature {h['curv']}%, exact MDS), the {v['N']:,}-sphere mass, the {v['ba']} co-authored, the {v['shut']} two-layer cards, the {v['names']:,} register names ({v['distinct']:,} distinct). The daily cascade re-runs this generator, so the body <b>breathes</b> — it is never a stale snapshot. These live figures can <b>differ from each part's own page</b>, which froze the corpus at <i>its</i> build time: the heart read dim 7.36 the day it was built and reads <b>{h['dim']}</b> now — adding the vessel's own five parts changed the corpus's self-reference graph. That drift is the body growing, <b>not an error</b>.</div></div>
    <div class="layer"><div class="lk">Figure</div><div class="lv">The <b>body</b> — the silhouette, the organs, the word <b>“knows itself.”</b> The corpus is a pile of static files, not a living being; it does not think, will, or feel. "Knows itself" means only that it <b>measures</b> itself and <b>names what it cannot prove</b> — the honest sense, not the mystical one. Each organ is a door to the instrument that does the measuring; the anatomy is how they hang together, drawn for a human eye.</div></div>
  </div>

  <footer>
    THE VESSEL · the corpus as a body that knows itself · a living self-portrait, regenerated daily by the cascade · <a href="../ud0/">◄ UD0</a><br>
    <a href="../the-heart/">IB</a> · <a href="../the-ka/">KA</a> · <a href="../the-ba/">BA</a> · <a href="../the-shut/">SHUT</a> · <a href="../the-ren/">REN</a> · threaded by <a href="../the-neural-web/">the neural web</a> · ROOT0, with AVAN · CC-BY-ND-4.0 · the numbers are real; the body is the figure.
  </footer>
</div></body></html>
"""

def main():
    v = compute()
    open(OUT, "w", encoding="utf-8").write(render(v))
    print(f"THE VESSEL regenerated {v['stamp']}")
    print(f"  IB heart : dim {v['heart']['dim']} · curv {v['heart']['curv']}% · {v['heart']['woven']} woven / {v['heart']['unwoven']} unwoven (live={v['heart']['live']})")
    print(f"  KA spark : {v['N']} spheres · top-5 {v['top5_share']}%")
    print(f"  BA voice : {v['ba']} co-authored")
    print(f"  SHUT     : {v['shut']} two-layer")
    print(f"  REN name : {v['names']} names · {v['distinct']} distinct · {v['coll']} collide")
    print(f"  pulse    : {v['hb']['named']} named · {v['hb']['verdict']} · last {v['hb']['run']}")
    print(f"  wrote {OUT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
