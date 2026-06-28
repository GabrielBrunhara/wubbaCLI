"""Export ASCII art to TXT and HTML files."""
from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from pathlib import Path

from api import Character
from settings import settings
from utils import EXPORTS_DIR


def _filename(char: Character, ext: str) -> Path:
    safe_name = char.name.lower().replace(" ", "_").replace("/", "-")
    return EXPORTS_DIR / f"{safe_name}_{char.id}.{ext}"


def export_txt(char: Character, ascii_art: str) -> Path:
    path = _filename(char, "txt")
    lines = [
        f"WubbaCLI Export — {char.name}",
        "=" * 60,
        f"ID:       {char.id}",
        f"Status:   {char.status}",
        f"Species:  {char.species}",
        f"Gender:   {char.gender}",
        f"Origin:   {char.origin}",
        f"Location: {char.location}",
        f"Episodes: {char.episode_count}",
        "=" * 60,
        "",
        ascii_art,
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ── HTML export helpers ───────────────────────────────────────────────────────

_STATUS = {
    "alive":   {"color": "#00ff41", "icon": "●", "label": "ALIVE"},
    "dead":    {"color": "#ff1744", "icon": "✕", "label": "DEAD"},
    "unknown": {"color": "#ffb300", "icon": "◌", "label": "UNKNOWN"},
}

_SPECIES_COLOR = {
    "human":                 "#00e5ff",
    "humanoid":              "#00e5ff",
    "alien":                 "#e040fb",
    "robot":                 "#2979ff",
    "mythological creature": "#e040fb",
    "cronenberg":            "#ff6d00",
    "poopybutthole":         "#ff69b4",
    "disease":               "#ffb300",
    "animal":                "#ffb300",
    "parasite":              "#76ff03",
    "unknown":               "#888888",
}

_GENDER_ICON = {"male": "♂", "female": "♀", "genderless": "∅", "unknown": "?"}

_SEASONS = [
    ("S1", range(1, 12)),
    ("S2", range(12, 22)),
    ("S3", range(22, 32)),
    ("S4", range(32, 42)),
    ("S5", range(42, 52)),
]


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _episode_grid(char: Character, accent: str) -> str:
    appeared = set()
    for url in char.episodes:
        try:
            appeared.add(int(url.rstrip("/").split("/")[-1]))
        except ValueError:
            pass

    dim = _rgba(accent, 0.2)
    glow = _rgba(accent, 0.5)
    rows = []
    for label, ep_range in _SEASONS:
        cells = []
        for n in ep_range:
            if n in appeared:
                cells.append(
                    f'<div class="ep on" title="Episode {n}">{n}</div>'
                )
            else:
                cells.append(
                    f'<div class="ep" title="Episode {n}">{n}</div>'
                )
        rows.append(
            f'<div class="s-row"><span class="s-label">{label}</span>'
            f'<div class="ep-cells">{"".join(cells)}</div></div>'
        )
    return "\n".join(rows)


_HTML_ART_WIDTH = 200   # higher resolution specifically for HTML export


def export_html(char: Character, ascii_art: str) -> Path:
    path = _filename(char, "html")

    # Re-render at higher resolution for HTML (uses cache — no extra download)
    try:
        from ascii_engine import image_url_to_ascii
        html_art = image_url_to_ascii(char.image, width=_HTML_ART_WIDTH)
    except Exception:
        html_art = ascii_art

    # ── Dynamic theme from character data ─────────────────────────────────────
    st        = _STATUS.get(char.status.lower(), _STATUS["unknown"])
    accent    = st["color"]
    dim       = _rgba(accent, 0.18)
    glow      = _rgba(accent, 0.45)
    mid       = _rgba(accent, 0.07)

    sp_color  = _SPECIES_COLOR.get(char.species.lower(), accent)
    sp_dim    = _rgba(sp_color, 0.2)

    gender_icon = _GENDER_ICON.get(char.gender.lower(), "?")

    # Dimension extracted from origin like "Earth (C-137)" → "C-137"
    dim_match  = re.search(r"\(([^)]+)\)", char.origin)
    dimension  = dim_match.group(1) if dim_match else "UNKNOWN"

    # Sub-type row (only if present)
    type_row = (
        f'<span class="sk">Type</span>'
        f'<span class="sv">{html.escape(char.type)}</span>'
        if char.type else ""
    )

    # Created date
    try:
        dt = datetime.fromisoformat(char.created.replace("Z", "+00:00"))
        created_str = dt.strftime("%b %d, %Y").upper()
    except Exception:
        created_str = char.created[:10]

    export_ts  = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    escaped_art = html.escape(html_art)
    ep_grid    = _episode_grid(char, accent)

    # First / last episode numbers
    ep_nums   = sorted(
        int(u.rstrip("/").split("/")[-1])
        for u in char.episodes
        if u.rstrip("/").split("/")[-1].isdigit()
    )
    first_ep  = ep_nums[0]  if ep_nums else None
    last_ep   = ep_nums[-1] if ep_nums else None

    type_stat     = (
        f'<span class="csk">Type</span>'
        f'<span class="csv">{html.escape(char.type)}</span>'
        if char.type else ""
    )
    first_ep_stat = (
        f'<span class="csk">First seen</span>'
        f'<span class="csv">Episode {first_ep}</span>'
        if first_ep else ""
    )
    last_ep_stat  = (
        f'<span class="csk">Last seen</span>'
        f'<span class="csv">Episode {last_ep}</span>'
        if last_ep else ""
    )

    # ── HTML ──────────────────────────────────────────────────────────────────
    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WubbaCLI — {html.escape(char.name)}</title>
  <style>
    :root {{
      --a:   {accent};
      --dim: {dim};
      --glow:{glow};
      --mid: {mid};
      --sp:  {sp_color};
      --sp-dim:{sp_dim};
    }}
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    body{{
      background:#040404;
      color:#b8b8b8;
      font-family:'Courier New',Courier,monospace;
      min-height:100vh;
    }}
    /* CRT scanlines */
    body::after{{
      content:'';position:fixed;inset:0;pointer-events:none;z-index:9999;
      background:repeating-linear-gradient(
        to bottom,
        transparent 0px,transparent 3px,
        rgba(0,0,0,0.13) 3px,rgba(0,0,0,0.13) 4px
      );
    }}

    .wrap{{max-width:960px;margin:0 auto;padding:2rem 2rem 3rem}}

    /* ── Header ── */
    .hdr{{
      display:flex;justify-content:space-between;align-items:center;
      padding-bottom:1rem;margin-bottom:2rem;
      border-bottom:1px solid var(--a);
    }}
    .hdr-brand{{
      font-size:1.2rem;letter-spacing:.4em;color:var(--a);
      text-shadow:0 0 12px var(--glow);
    }}
    .hdr-rec{{
      font-size:.65rem;letter-spacing:.2em;
      color:rgba(255,255,255,.22);
    }}

    /* ── Hero ── */
    .hero{{
      display:grid;grid-template-columns:200px 1fr;gap:2rem;
      margin-bottom:2rem;
    }}
    @media(max-width:600px){{.hero{{grid-template-columns:1fr}}}}
    .photo-wrap{{position:relative}}
    .photo-wrap img{{
      width:100%;display:block;
      border:2px solid var(--a);
      box-shadow:0 0 18px var(--glow);
      filter:saturate(.75) contrast(1.1);
      transition:opacity .45s ease;
    }}
    .info{{display:flex;flex-direction:column;justify-content:center;gap:.9rem}}
    .char-name{{
      font-size:2rem;font-weight:bold;color:#f0f0f0;letter-spacing:.08em;
      animation:glitch 9s infinite;
    }}
    .badges{{display:flex;gap:.75rem;flex-wrap:wrap}}
    .badge{{
      padding:.2rem .65rem;font-size:.65rem;letter-spacing:.15em;
      border:1px solid currentColor;
    }}
    .b-status{{color:var(--a);border-color:var(--a);box-shadow:0 0 6px var(--dim)}}
    .b-species{{color:var(--sp);border-color:var(--sp)}}
    .b-gender{{color:rgba(255,255,255,.45);border-color:rgba(255,255,255,.2)}}
    .stats{{
      display:grid;grid-template-columns:auto 1fr;
      gap:.35rem 1.5rem;align-items:baseline;
    }}
    .sk{{font-size:.65rem;letter-spacing:.15em;color:rgba(255,255,255,.3);text-transform:uppercase}}
    .sv{{font-size:.82rem;color:#d0d0d0}}
    .ep-count-bar{{
      display:inline-block;height:4px;width:100%;
      background:linear-gradient(to right,var(--a) {min(100, round(char.episode_count / 51 * 100))}%,rgba(255,255,255,.08) {min(100, round(char.episode_count / 51 * 100))}%);
      box-shadow:0 0 6px var(--dim);
    }}

    /* ── Episode grid ── */
    .sec-title{{
      font-size:.6rem;letter-spacing:.3em;color:var(--a);text-transform:uppercase;
      border-bottom:1px solid var(--dim);padding-bottom:.5rem;margin-bottom:1rem;
    }}
    .ep-section{{margin-bottom:2rem}}
    .seasons{{display:flex;flex-direction:column;gap:.45rem}}
    .s-row{{display:flex;align-items:center;gap:.5rem}}
    .s-label{{width:2rem;font-size:.6rem;color:rgba(255,255,255,.25);letter-spacing:.1em}}
    .ep-cells{{display:flex;gap:3px;flex-wrap:wrap}}
    .ep{{
      width:22px;height:22px;display:flex;align-items:center;justify-content:center;
      font-size:.45rem;
      background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
      color:rgba(255,255,255,.18);
    }}
    .ep.on{{
      background:var(--mid);border-color:var(--a);color:var(--a);
      box-shadow:0 0 5px var(--dim);
    }}

    /* ── ASCII toggle overlay ── */
    .ascii-wrap{{
      position:absolute;inset:0;overflow:hidden;
      opacity:0;transition:opacity .45s ease;
      background:#040404;
    }}
    pre.ascii{{
      white-space:pre;line-height:1;font-size:1px;margin:0;
      color:var(--a);
      text-shadow:0 0 4px var(--glow),0 0 1px var(--a);
    }}
    .photo-wrap.show-ascii img{{opacity:0}}
    .photo-wrap.show-ascii .ascii-wrap{{opacity:1}}
    .toggle-btn{{
      width:100%;margin-top:.4rem;padding:.3rem;
      background:transparent;border:1px solid var(--dim);
      color:rgba(255,255,255,.3);
      font-family:'Courier New',Courier,monospace;
      font-size:.6rem;letter-spacing:.2em;cursor:pointer;
      transition:background .2s,border-color .2s,color .2s;
    }}
    .toggle-btn:hover{{background:var(--mid);border-color:var(--a);color:var(--a)}}
    /* ── ASCII action buttons ── */
    .ascii-btns{{
      position:absolute;top:.35rem;right:.35rem;z-index:10;
      display:flex;flex-direction:column;gap:.28rem;
      opacity:0;pointer-events:none;transition:opacity .2s;
    }}
    .photo-wrap.show-ascii .ascii-btns{{opacity:.4;pointer-events:auto}}
    .photo-wrap.show-ascii:hover .ascii-btns{{opacity:1}}
    .ascii-btns button{{
      background:rgba(4,4,4,.8);border:1px solid var(--dim);
      color:var(--a);cursor:pointer;padding:.22rem .3rem;line-height:1;
      transition:border-color .2s,box-shadow .2s;
    }}
    .ascii-btns button:hover{{border-color:var(--a);box-shadow:0 0 6px var(--glow)}}
    /* ── Character data stats ── */
    .char-data-section{{margin-bottom:2rem}}
    .char-data{{
      display:grid;grid-template-columns:auto 1fr;
      gap:.4rem 2rem;align-items:baseline;
    }}
    .csk{{font-size:.6rem;letter-spacing:.15em;color:rgba(255,255,255,.27);text-transform:uppercase}}
    .csv{{font-size:.82rem;color:#ccc}}
    /* ── Fullscreen overlay ── */
    #fs-overlay{{
      display:none;position:fixed;inset:0;z-index:9998;
      background:#020202;overflow:hidden;
      align-items:center;justify-content:center;
    }}
    .fs-frame{{
      position:relative;
      border:1px solid var(--dim);
      box-shadow:0 0 60px var(--glow),0 0 140px var(--dim),inset 0 0 40px var(--dim);
      padding:.6rem;
    }}
    .fc{{
      position:absolute;width:22px;height:22px;
      border-color:var(--a);border-style:solid;opacity:.9;
      box-shadow:0 0 8px var(--glow);
    }}
    .fc.tl{{top:-2px;left:-2px;border-width:3px 0 0 3px}}
    .fc.tr{{top:-2px;right:-2px;border-width:3px 3px 0 0}}
    .fc.bl{{bottom:-2px;left:-2px;border-width:0 0 3px 3px}}
    .fc.br{{bottom:-2px;right:-2px;border-width:0 3px 3px 0}}
    #ascii-fs{{
      display:block;white-space:pre;margin:0;
      color:var(--a);
      text-shadow:0 0 6px var(--glow),0 0 1px var(--a);
    }}
    .fs-close{{
      position:absolute;top:1rem;right:1rem;z-index:9999;
      background:rgba(2,2,2,.85);border:1px solid var(--dim);
      color:rgba(255,255,255,.4);font-size:.8rem;cursor:pointer;
      width:2rem;height:2rem;line-height:1;
      display:flex;align-items:center;justify-content:center;
      transition:border-color .2s,color .2s,box-shadow .2s;
    }}
    .fs-close:hover{{border-color:var(--a);color:var(--a);box-shadow:0 0 10px var(--glow)}}

    /* ── Footer ── */
    .ftr{{
      border-top:1px solid rgba(255,255,255,.07);padding-top:1rem;
      display:flex;justify-content:space-between;flex-wrap:wrap;gap:.5rem;
      font-size:.6rem;color:rgba(255,255,255,.18);letter-spacing:.12em;
    }}
    .ftr a{{color:var(--dim);text-decoration:none}}

    /* ── Animations ── */
    @keyframes glitch{{
      0%,91%,100%{{transform:none;text-shadow:none}}
      92%{{transform:translate(-2px,0);text-shadow:2px 0 #ff0040,-2px 0 #00ffff}}
      93%{{transform:translate(2px,0);text-shadow:-2px 0 #ff0040,2px 0 #00ffff}}
      94%{{transform:translate(-1px,1px);text-shadow:1px 0 #ff0040}}
      95%{{transform:none;text-shadow:none}}
      96%{{transform:translate(1px,-1px);text-shadow:-1px 0 #00ffff}}
      97%{{transform:none}}
    }}
  </style>
</head>
<body>
  <div class="wrap">

    <div class="hdr">
      <div class="hdr-brand">WUBBACLI</div>
      <div class="hdr-rec">INTERDIMENSIONAL DATABASE &nbsp;·&nbsp; RECORD #{char.id:04d}</div>
    </div>

    <div class="hero">
      <div class="photo-col">
        <div class="photo-wrap show-ascii" id="media-wrap">
          <img src="{html.escape(char.image)}" alt="{html.escape(char.name)}" onload="fitAscii()">
          <div class="ascii-wrap">
            <pre class="ascii" id="ascii-art">{escaped_art}</pre>
            <div class="ascii-btns">
              <button onclick="openFullscreen()" title="Fullscreen"><svg width="11" height="11" viewBox="0 0 11 11" fill="currentColor"><path d="M0 0h4v1H1v3H0zm7 0h4v4h-1V1H7zM0 7h1v3h3v1H0zm10 3H7v-1h3V7h1z"/></svg></button>
              <button id="copy-btn" onclick="copyAscii()" title="Copy ASCII"><svg width="11" height="11" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.3"><rect x="3.5" y=".5" width="7.5" height="9" rx="1"/><rect x=".5" y="2.5" width="7.5" height="9" rx="1" fill="#040404"/></svg></button>
            </div>
          </div>
        </div>
        <button class="toggle-btn" id="toggle-btn" onclick="toggleView()">&#9672; PHOTO VIEW</button>
      </div>
      <div class="info">
        <div class="char-name">{html.escape(char.name)}</div>
        <div class="badges">
          <span class="badge b-status">{st["icon"]} {st["label"]}</span>
          <span class="badge b-species">{html.escape(char.species.upper())}</span>
          <span class="badge b-gender">{gender_icon} {html.escape(char.gender.upper())}</span>
        </div>
        <div class="stats">
          <span class="sk">Origin</span>     <span class="sv">{html.escape(char.origin)}</span>
          <span class="sk">Location</span>   <span class="sv">{html.escape(char.location)}</span>
          {type_row}
          <span class="sk">Episodes</span>   <span class="sv">{char.episode_count} / 51 &nbsp;<span class="ep-count-bar"></span></span>
          <span class="sk">Indexed</span>    <span class="sv">{created_str}</span>
        </div>
      </div>
    </div>

    <div class="ep-section">
      <div class="sec-title">Episode Appearances &nbsp;—&nbsp; {char.episode_count} of 51</div>
      <div class="seasons">
{ep_grid}
      </div>
    </div>

    <div class="char-data-section">
      <div class="sec-title">Character Data</div>
      <div class="char-data">
        <span class="csk">ID</span>
        <span class="csv" style="color:var(--a)">#{char.id:04d}</span>
        <span class="csk">Status</span>
        <span class="csv" style="color:{accent}">{st["icon"]} {st["label"]}</span>
        <span class="csk">Species</span>
        <span class="csv" style="color:var(--sp)">{html.escape(char.species)}</span>
        {type_stat}
        <span class="csk">Gender</span>
        <span class="csv">{gender_icon} {html.escape(char.gender.title())}</span>
        <span class="csk">Origin</span>
        <span class="csv">{html.escape(char.origin)}</span>
        <span class="csk">Location</span>
        <span class="csv">{html.escape(char.location)}</span>
        <span class="csk">Dimension</span>
        <span class="csv" style="color:var(--a)">{html.escape(dimension)}</span>
        <span class="csk">Episodes</span>
        <span class="csv">{char.episode_count}<span style="color:rgba(255,255,255,.22)"> / 51</span></span>
        {first_ep_stat}
        {last_ep_stat}
        <span class="csk">Indexed</span>
        <span class="csv">{created_str}</span>
      </div>
    </div>

    <div class="ftr">
      <span>Generated by WubbaCLI</span>
      <span>DIMENSION &nbsp;{html.escape(dimension)}</span>
      <span><a href="{html.escape(char.url)}" target="_blank" rel="noopener">{html.escape(char.url)}</a></span>
      <span>{export_ts}</span>
    </div>

  </div>
  <div id="fs-overlay">
    <button class="fs-close" onclick="closeFullscreen()" title="Close">&#10005;</button>
    <div class="fs-frame">
      <span class="fc tl"></span><span class="fc tr"></span>
      <span class="fc bl"></span><span class="fc br"></span>
      <pre id="ascii-fs"></pre>
    </div>
  </div>
  <script>
    function fitAscii(){{
      var pre=document.getElementById('ascii-art');
      var wrap=document.getElementById('media-wrap');
      if(!pre||!wrap)return;
      var W=wrap.offsetWidth,H=wrap.offsetHeight;
      if(!W||!H)return;
      var lines=pre.textContent.split('\\n').filter(function(l){{return l.length>0;}});
      var maxLen=lines.reduce(function(m,l){{return Math.max(m,l.length);}},0);
      if(!maxLen||!lines.length)return;
      var fs=W/(maxLen*0.601);
      var lh=H/(lines.length*fs);
      pre.style.fontSize=fs+'px';
      pre.style.lineHeight=lh;
    }}
    function toggleView(){{
      var wrap=document.getElementById('media-wrap');
      var btn=document.getElementById('toggle-btn');
      wrap.classList.toggle('show-ascii');
      btn.textContent=wrap.classList.contains('show-ascii')?'◈ PHOTO VIEW':'◈ ASCII VIEW';
    }}
    var _asciiText=null;
    var _cpySVG='<svg width="11" height="11" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.3"><rect x="3.5" y=".5" width="7.5" height="9" rx="1"/><rect x=".5" y="2.5" width="7.5" height="9" rx="1" fill="#040404"/></svg>';
    var _okSVG='<svg width="11" height="11" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1.5,6 4.5,9.5 10.5,2.5"/></svg>';
    function copyAscii(){{
      if(!_asciiText)_asciiText=document.getElementById('ascii-art').textContent;
      var btn=document.getElementById('copy-btn');
      navigator.clipboard.writeText(_asciiText).then(function(){{
        btn.innerHTML=_okSVG;
        btn.style.borderColor='var(--a)';
        setTimeout(function(){{btn.innerHTML=_cpySVG;btn.style.borderColor='';}},1800);
      }}).catch(function(){{
        btn.innerHTML='!';
        setTimeout(function(){{btn.innerHTML=_cpySVG;}},1800);
      }});
    }}
    function openFullscreen(){{
      if(!_asciiText)_asciiText=document.getElementById('ascii-art').textContent;
      var pre=document.getElementById('ascii-fs');
      if(!pre.textContent)pre.textContent=_asciiText;
      document.getElementById('fs-overlay').style.display='flex';
      fitAsciiFS();
    }}
    function closeFullscreen(){{
      document.getElementById('fs-overlay').style.display='none';
    }}
    function fitAsciiFS(){{
      var pre=document.getElementById('ascii-fs');
      if(!pre.textContent)return;
      var W=window.innerWidth*0.92,H=window.innerHeight*0.92;
      var lines=pre.textContent.split('\\n').filter(function(l){{return l.length>0;}});
      var maxLen=lines.reduce(function(m,l){{return Math.max(m,l.length);}},0);
      if(!maxLen||!lines.length)return;
      var fsH=H/lines.length;
      var fsW=W/(maxLen*0.601);
      var fs=Math.min(fsH,fsW);
      pre.style.fontSize=fs+'px';
      pre.style.lineHeight='1';
    }}
    window.addEventListener('load',fitAscii);
    window.addEventListener('resize',function(){{
      fitAscii();
      if(document.getElementById('fs-overlay').style.display!=='none')fitAsciiFS();
    }});
    document.addEventListener('keydown',function(e){{
      if(e.key==='Escape')closeFullscreen();
    }});
  </script>
</body>
</html>
"""
    path.write_text(content, encoding="utf-8")
    return path
