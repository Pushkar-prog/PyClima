"""
Phase 3 Polish — PyClimaExplorer
Writes static/story_mode.html and upgrades app.py with Time-lapse + Story Mode tabs.
"""

import pathlib, os

# ─────────────────────────────────────────────────────────────
# PART A — WRITE static/story_mode.html
# ─────────────────────────────────────────────────────────────
pathlib.Path("static").mkdir(exist_ok=True)

STORY_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>PyClimaExplorer · Story Mode</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,400;0,500;1,400&family=Playfair+Display:ital,wght@0,700;1,700&family=Syne:wght@400;600;800&display=swap" rel="stylesheet"/>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
:root{
  --bg:#04080f;
  --c1:#e85d2f;
  --c2:#2f8de8;
  --c3:#3de8a0;
  --c4:#e8c32f;
  --text:#d0d8e8;
  --muted:#6b7a99;
}
html{scroll-behavior:smooth;}
body{background:var(--bg);color:var(--text);font-family:'Syne',sans-serif;overflow-x:hidden;cursor:none;}

/* noise overlay */
body::before{
  content:"";position:fixed;inset:0;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E");
  opacity:.04;pointer-events:none;z-index:999;
}

/* cursor */
#cursor-dot{position:fixed;width:10px;height:10px;background:#e85d2f;border-radius:50%;pointer-events:none;transform:translate(-50%,-50%);z-index:9999;mix-blend-mode:screen;transition:transform .1s;}
#cursor-ring{position:fixed;width:36px;height:36px;border:1.5px solid rgba(232,93,47,.5);border-radius:50%;pointer-events:none;transform:translate(-50%,-50%);z-index:9998;mix-blend-mode:screen;transition:transform .15s,left .12s,top .12s;}

/* progress bar */
#progress-bar{position:fixed;top:0;left:0;height:2px;background:#e85d2f;box-shadow:0 0 8px #e85d2f;width:0%;z-index:1000;transition:width .1s;}

/* nav dots */
#nav-dots{position:fixed;right:24px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:14px;z-index:500;}
.dot{width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,.2);cursor:pointer;transition:transform .2s,background .2s;position:relative;}
.dot.active{background:#e85d2f;transform:scale(1.4);}
.dot-label{position:absolute;right:18px;top:50%;transform:translateY(-50%);background:#0d1117;color:#d0d8e8;font-size:.7rem;padding:3px 8px;border-radius:4px;white-space:nowrap;opacity:0;pointer-events:none;transition:opacity .2s;font-family:'DM Mono',monospace;}
.dot:hover .dot-label{opacity:1;}

/* sections */
section{min-height:100vh;display:flex;flex-direction:column;justify-content:center;padding:80px 10vw;opacity:0;transform:translateY(40px);transition:opacity .7s,transform .7s;}
section.visible{opacity:1;transform:translateY(0);}

/* eyebrow */
.eyebrow{font-family:'DM Mono',monospace;font-size:.75rem;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);margin-bottom:20px;}

/* headings */
h1.display{font-family:'Playfair Display',serif;font-style:italic;font-size:clamp(2.4rem,6vw,5.2rem);line-height:1.1;margin-bottom:24px;}
h2.chapter{font-family:'Playfair Display',serif;font-size:clamp(1.8rem,4vw,3.2rem);line-height:1.2;margin-bottom:20px;}

.subtitle{font-size:1.15rem;color:var(--muted);max-width:640px;line-height:1.7;margin-bottom:36px;}
.body-text{max-width:620px;line-height:1.8;font-size:1.05rem;color:#b0bdd6;margin-bottom:36px;}
.body-text strong{color:#fff;}

/* buttons */
.btn{display:inline-block;padding:14px 32px;border-radius:8px;font-weight:700;font-size:1rem;text-decoration:none;cursor:pointer;border:none;transition:transform .15s,box-shadow .15s;}
.btn-primary{background:var(--c1);color:#fff;}
.btn-primary:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(232,93,47,.35);}
.btn-secondary{background:transparent;border:1.5px solid var(--c3);color:var(--c3);}
.btn-secondary:hover{background:var(--c3);color:#04080f;transform:translateY(-3px);}

/* accent bars */
.accent-bar{width:48px;height:3px;border-radius:2px;margin-bottom:28px;}

/* stats row */
.stats{display:flex;gap:40px;flex-wrap:wrap;margin-bottom:40px;}
.stat{text-align:center;}
.stat-val{font-family:'Playfair Display',serif;font-size:2.6rem;font-weight:700;}
.stat-lbl{font-family:'DM Mono',monospace;font-size:.72rem;letter-spacing:.12em;color:var(--muted);margin-top:4px;}

/* fake viz blocks */
.viz-block{border-radius:12px;height:220px;position:relative;overflow:hidden;margin-top:12px;max-width:800px;}
.viz-label{position:absolute;bottom:12px;left:14px;font-family:'DM Mono',monospace;font-size:.7rem;color:rgba(255,255,255,.5);}

/* tas heatmap */
.viz-tas{background:linear-gradient(135deg,#1a2a6c 0%,#b21f1f 35%,#fdbb2d 60%,#b21f1f 80%,#0f2027 100%);}

/* pr trend */
.viz-pr{background:linear-gradient(135deg,#6b3a00 0%,#1a3a00 30%,#003a6b 55%,#000a2a 100%);}

/* ENSO bars */
.viz-enso{display:flex;align-items:flex-end;padding:16px 12px;background:#0d1117;border:1px solid #1e2d3d;gap:2px;}
.enso-bar{flex:1;border-radius:2px 2px 0 0;transition:opacity .2s;}
.enso-bar:hover{opacity:.75;}

/* split panel */
.split-panel{display:flex;border-radius:12px;overflow:hidden;height:220px;max-width:800px;margin-top:12px;position:relative;}
.split-left{flex:1;background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);}
.split-right{flex:1;background:linear-gradient(135deg,#b21f1f,#fdbb2d,#ff512f);}
.split-divider{width:3px;background:#fff;display:flex;align-items:center;justify-content:center;font-size:.9rem;color:#0d1117;font-weight:700;position:relative;z-index:2;}
.split-label{position:absolute;top:12px;font-family:'DM Mono',monospace;font-size:.7rem;color:rgba(255,255,255,.6);padding:0 12px;}

/* outro */
#outro{text-align:center;align-items:center;}
.footer{font-family:'DM Mono',monospace;font-size:.7rem;color:var(--muted);margin-top:28px;letter-spacing:.12em;}
</style>
</head>
<body>

<div id="cursor-dot"></div>
<div id="cursor-ring"></div>
<div id="progress-bar"></div>

<nav id="nav-dots">
  <div class="dot active" data-target="intro"><span class="dot-label">Intro</span></div>
  <div class="dot" data-target="c1"><span class="dot-label">Warming</span></div>
  <div class="dot" data-target="c2"><span class="dot-label">ENSO</span></div>
  <div class="dot" data-target="c3"><span class="dot-label">Rainfall</span></div>
  <div class="dot" data-target="c4"><span class="dot-label">1920 vs 2018</span></div>
  <div class="dot" data-target="outro"><span class="dot-label">Explore</span></div>
</nav>

<!-- ═══════════════════ INTRO ═══════════════════ -->
<section id="intro">
  <div class="eyebrow">CESM1-Style Synthetic Data · 1920–2018 · 98 Years</div>
  <h1 class="display">Earth is speaking.<br/>Are you listening?</h1>
  <p class="subtitle">
    98 years of climate simulation — warming, ENSO cycles,
    shifting rainfall, and a century of change distilled into four chapters.
  </p>
  <button class="btn btn-primary" onclick="document.getElementById('c1').scrollIntoView({behavior:'smooth'})">Begin Story ↓</button>
</section>

<!-- ═══════════════════ C1 ═══════════════════ -->
<section id="c1">
  <div class="eyebrow">Chapter 01</div>
  <div class="accent-bar" style="background:var(--c1);"></div>
  <h2 class="chapter">A Century of Warming</h2>
  <p class="body-text">
    From 1920 to 2018 the planet warmed by <strong>+1.1°C</strong>.
    Polar regions amplified at <strong>3× the global mean</strong>.
    The trend map makes this unmistakable — every red pixel is a region
    that warmed faster than Earth's average.
  </p>
  <div class="stats">
    <div class="stat"><div class="stat-val" style="color:var(--c1);" data-target="1.1" data-suffix="°C" data-prefix="+">+0°C</div><div class="stat-lbl">Total Warming</div></div>
    <div class="stat"><div class="stat-val" style="color:var(--c1);" data-target="3" data-suffix="×">0×</div><div class="stat-lbl">Polar Amplification</div></div>
    <div class="stat"><div class="stat-val" style="color:var(--c1);" data-target="98" data-suffix=" yrs">0 yrs</div><div class="stat-lbl">Record Length</div></div>
  </div>
  <div class="viz-block viz-tas"><div class="viz-label">TAS Trend Map (simulated)</div></div>
</section>

<!-- ═══════════════════ C2 ═══════════════════ -->
<section id="c2">
  <div class="eyebrow">Chapter 02</div>
  <div class="accent-bar" style="background:var(--c2);"></div>
  <h2 class="chapter">El Niño &amp; La Niña Since 1920</h2>
  <p class="body-text">
    With 98 years of data we capture roughly <strong>30 complete ENSO cycles</strong>.
    Each red bar is an El Niño year — warmer oceans, disrupted rainfall, more intense storms globally.
    Each blue bar is La Niña. No manual labelling: the Niño 3.4 index flags every event automatically.
  </p>
  <div class="stats">
    <div class="stat"><div class="stat-val" style="color:var(--c2);" data-target="30" data-prefix="~" data-suffix=" events">~0 events</div><div class="stat-lbl">ENSO Cycles</div></div>
    <div class="stat"><div class="stat-val" style="color:var(--c2);" data-target="0.5" data-suffix="°C">0°C</div><div class="stat-lbl">Niño 3.4 Threshold</div></div>
    <div class="stat"><div class="stat-val" style="color:var(--c2);" data-target="98" data-suffix=" yrs">0 yrs</div><div class="stat-lbl">Record Length</div></div>
  </div>
  <div class="viz-block viz-enso" id="enso-chart"><div class="viz-label">Niño 3.4 Index (simulated)</div></div>
</section>

<!-- ═══════════════════ C3 ═══════════════════ -->
<section id="c3">
  <div class="eyebrow">Chapter 03</div>
  <div class="accent-bar" style="background:var(--c3);"></div>
  <h2 class="chapter">Shifting Rainfall Patterns</h2>
  <p class="body-text">
    Wet regions get <strong>wetter</strong>, dry regions get <strong>drier</strong>.
    Extreme precipitation events increase <strong>7% per °C</strong> of warming.
    Monsoon systems are shifting poleward — a reorganisation visible across the 98-year record.
  </p>
  <div class="stats">
    <div class="stat"><div class="stat-val" style="color:var(--c3);" data-target="7" data-suffix="%/°C">0%/°C</div><div class="stat-lbl">Precip Extreme Increase</div></div>
    <div class="stat"><div class="stat-val" style="color:var(--c3);" data-target="40" data-suffix="% shift">0% shift</div><div class="stat-lbl">Monsoon Shift</div></div>
    <div class="stat"><div class="stat-val" style="color:var(--c3);" data-target="98" data-suffix=" yrs">0 yrs</div><div class="stat-lbl">Record Length</div></div>
  </div>
  <div class="viz-block viz-pr"><div class="viz-label">PR Trend Map (simulated)</div></div>
</section>

<!-- ═══════════════════ C4 ═══════════════════ -->
<section id="c4">
  <div class="eyebrow">Chapter 04</div>
  <div class="accent-bar" style="background:var(--c4);"></div>
  <h2 class="chapter">1920 vs 2018 — A Century Apart</h2>
  <p class="body-text">
    This is not a 30-year comparison. Placing <strong>1920</strong> beside <strong>2018</strong>
    shows a full century of climate forcing. The Arctic has lost
    <strong>13% of sea ice per decade</strong>. The difference panel makes the scale of change
    impossible to ignore.
  </p>
  <div class="stats">
    <div class="stat"><div class="stat-val" style="color:var(--c4);" data-target="13" data-suffix="%/dec">0%/dec</div><div class="stat-lbl">Sea Ice Loss Rate</div></div>
    <div class="stat"><div class="stat-val" style="color:var(--c4);" data-target="98" data-suffix=" yrs">0 yrs</div><div class="stat-lbl">Time Span</div></div>
    <div class="stat"><div class="stat-val" style="color:var(--c4);" data-target="1.1" data-suffix="°C" data-prefix="+">+0°C</div><div class="stat-lbl">Total Warming</div></div>
  </div>
  <div class="split-panel">
    <div class="split-left"><span class="split-label">1920</span></div>
    <div class="split-divider">↔</div>
    <div class="split-right"><span class="split-label" style="right:0;left:auto;">2018</span></div>
  </div>
</section>

<!-- ═══════════════════ OUTRO ═══════════════════ -->
<section id="outro">
  <div class="eyebrow">The story is told</div>
  <h2 class="chapter" style="font-family:'Playfair Display',serif;font-style:italic;">The data has been told.<br/>Now explore it.</h2>
  <br/>
  <button class="btn btn-secondary" onclick="window.open('http://localhost:8501','_blank')">Open Dashboard →</button>
  <p class="footer" style="margin-top:40px;">PyClimaExplorer · Synthetic CESM1-Style Data · Technex '26</p>
</section>

<script>
// cursor
const dot  = document.getElementById('cursor-dot');
const ring = document.getElementById('cursor-ring');
document.addEventListener('mousemove', e => {
  dot.style.left  = ring.style.left  = e.clientX + 'px';
  dot.style.top   = ring.style.top   = e.clientY + 'px';
});

// progress bar
const bar = document.getElementById('progress-bar');
window.addEventListener('scroll', () => {
  const pct = window.scrollY / (document.body.scrollHeight - window.innerHeight) * 100;
  bar.style.width = Math.min(pct, 100) + '%';
  updateDots();
});

// nav dots
const sections = ['intro','c1','c2','c3','c4','outro'];
const dots = document.querySelectorAll('.dot');
dots.forEach((d, i) => {
  d.addEventListener('click', () => {
    document.getElementById(sections[i]).scrollIntoView({behavior:'smooth'});
  });
});
function updateDots() {
  let active = 0;
  sections.forEach((id, i) => {
    const el = document.getElementById(id);
    if (el && el.getBoundingClientRect().top < window.innerHeight / 2) active = i;
  });
  dots.forEach((d, i) => d.classList.toggle('active', i === active));
}

// intersection observer
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      animateCounters(e.target);
    }
  });
}, {threshold: 0.15});
document.querySelectorAll('section').forEach(s => observer.observe(s));

// animated counters
function animateCounters(section) {
  section.querySelectorAll('[data-target]').forEach(el => {
    const target = parseFloat(el.dataset.target);
    const suffix = el.dataset.suffix || '';
    const prefix = el.dataset.prefix || '';
    let start = 0;
    const duration = 1200;
    const step = ts => {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      el.textContent = prefix + (Number.isInteger(target)
        ? Math.round(target * ease)
        : (target * ease).toFixed(1)) + suffix;
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  });
}

// ENSO bars
(function() {
  const chart = document.getElementById('enso-chart');
  const barsContainer = document.createElement('div');
  barsContainer.style.cssText = 'display:flex;align-items:flex-end;width:100%;height:180px;gap:2px;position:relative;z-index:1;';
  for (let i = 0; i < 98; i++) {
    const val = 0.8 * Math.sin(2 * Math.PI * i / 4.2) + (Math.random() - 0.5) * 0.6;
    const h = Math.abs(val) / 2.0 * 100;
    const bar = document.createElement('div');
    bar.className = 'enso-bar';
    bar.style.height = h + '%';
    bar.style.background = val > 0.5 ? '#ef4444' : val < -0.5 ? '#3b82f6' : '#4b5563';
    bar.title = (1920 + i) + ': ' + val.toFixed(2);
    barsContainer.appendChild(bar);
  }
  chart.insertBefore(barsContainer, chart.firstChild);
})();
</script>
</body>
</html>"""

pathlib.Path("static/story_mode.html").write_text(STORY_HTML, encoding="utf-8")
print("✅ static/story_mode.html written")

# ─────────────────────────────────────────────────────────────
# PART B — WRITE UPGRADED app.py (7 tabs)
# ─────────────────────────────────────────────────────────────
app_code = r'''
import streamlit as st
import xarray as xr
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit.components.v1 as components
import pathlib

st.set_page_config(
    page_title="PyClimaExplorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #0d1117; color: #c9d1d9; }
  [data-testid="stSidebar"] { background: #161b22; }
  h1 {
    background: linear-gradient(90deg, #1f6feb, #3fb950);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-size: 2.2rem; font-weight: 800;
  }
  .badge {
    background: #1a4731; border: 1px solid #3fb950; border-radius: 6px;
    padding: 6px 12px; color: #3fb950; font-size: .82rem; font-weight: 600;
  }
  .metric-card {
    background: #161b22; border: 1px solid #30363d; border-radius: 8px;
    padding: 14px 18px; text-align: center;
  }
  .metric-card .val { font-size: 1.5rem; font-weight: 700; color: #58a6ff; }
  .metric-card .lbl { font-size: .75rem; color: #8b949e; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🌍 PyClimaExplorer</h1>", unsafe_allow_html=True)

VARIABLE_META = {
    "tas":    {"label": "Surface Air Temp (°C)",     "cscale": "RdBu_r",  "unit": "°C"},
    "pr":     {"label": "Precipitation (mm/day)",    "cscale": "Blues",   "unit": "mm/day"},
    "sst":    {"label": "Sea Surface Temp (°C)",     "cscale": "RdBu_r",  "unit": "°C"},
    "psl":    {"label": "Sea Level Pressure (hPa)",  "cscale": "RdBu_r",  "unit": "hPa"},
    "siconc": {"label": "Sea Ice Concentration (%)", "cscale": "Blues_r", "unit": "%"},
}

@st.cache_data
def load_data():
    return xr.open_zarr("data/cesm.zarr")

with st.spinner("Loading dataset …"):
    ds = load_data()

def comp(x):
    return x.compute().values if hasattr(x, "compute") else x.values

with st.sidebar:
    st.markdown('<div class="badge">✅ Synthetic CESM1-style data · 1920–2018</div>',
                unsafe_allow_html=True)
    st.markdown("---")
    var    = st.selectbox("Variable", list(VARIABLE_META.keys()),
                          format_func=lambda v: VARIABLE_META[v]["label"])
    season = st.selectbox("Season", ["Annual", "DJF", "MAM", "JJA", "SON"])
    year   = st.slider("Year", 1920, 2018, 1969)

meta = VARIABLE_META[var]
SEASON_MONTHS = {"DJF": [12,1,2], "MAM": [3,4,5], "JJA": [6,7,8], "SON": [9,10,11]}

@st.cache_data
def get_seasonal_mean(variable, yr, ssn):
    ds_ = xr.open_zarr("data/cesm.zarr")
    da  = ds_[variable]
    if ssn == "Annual":
        sub = da.sel(time=da["time.year"] == yr)
    else:
        months = SEASON_MONTHS[ssn]
        sub = da.sel(time=(da["time.year"] == yr) & (da["time.month"].isin(months)))
    return comp(sub.mean(dim="time"))

@st.cache_data
def get_year_mean(variable, yr):
    ds_ = xr.open_zarr("data/cesm.zarr")
    da  = ds_[variable]
    sub = da.sel(time=da["time.year"] == yr)
    return comp(sub.mean(dim="time"))

@st.cache_data
def compute_trend(variable):
    ds_ = xr.open_zarr("data/cesm.zarr")
    da  = ds_[variable]
    annual = da.groupby("time.year").mean()
    data   = comp(annual)
    years  = annual["year"].values
    x = years - years.mean()
    slope = (x[:, None, None] * (data - data.mean(axis=0))).sum(axis=0) / (x**2).sum()
    return slope * 10.0, ds_["lat"].values, ds_["lon"].values

lat_v = ds["lat"].values
lon_v = ds["lon"].values

tabs = st.tabs([
    "🗺️ Heatmap", "📈 Time Series", "🔥 Trend Map",
    "🌊 El Niño Detector", "🔄 Comparison",
    "▶️ Time-lapse", "📖 Story Mode"
])

# ── Heatmap ───────────────────────────────────────────────────
with tabs[0]:
    with st.spinner("Rendering heatmap …"):
        grid = get_seasonal_mean(var, year, season)
        p2, p98 = np.nanpercentile(grid, 2), np.nanpercentile(grid, 98)
        fig = px.imshow(grid, x=lon_v, y=lat_v, color_continuous_scale=meta["cscale"],
                        aspect="auto", title=f"{meta['label']} — {season} {year}",
                        labels={"color": meta["unit"]}, zmin=p2, zmax=p98)
        fig.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                          font_color="#c9d1d9", margin=dict(t=50,b=10,l=10,r=10))
        fig.update_xaxes(title="Longitude"); fig.update_yaxes(title="Latitude")
        st.plotly_chart(fig, use_container_width=True)

# ── Time Series ───────────────────────────────────────────────
with tabs[1]:
    c1, c2 = st.columns(2)
    with c1: sel_lat = st.slider("Latitude",  float(lat_v.min()), float(lat_v.max()), 0.0)
    with c2: sel_lon = st.slider("Longitude", float(lon_v.min()), float(lon_v.max()), 0.0)

    @st.cache_data
    def get_ts(variable, slat, slon):
        ds_ = xr.open_zarr("data/cesm.zarr")
        da  = ds_[variable]
        pt  = da.sel(lat=slat, lon=slon, method="nearest")
        ann = pt.groupby("time.year").mean()
        return ann["year"].values, comp(ann)

    with st.spinner("Computing time series …"):
        yrs, vals = get_ts(var, sel_lat, sel_lon)

    s = pd.Series(vals, index=yrs)
    roll5  = s.rolling(5,  center=True).mean()
    roll10 = s.rolling(10, center=True).mean()

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=yrs, y=vals, mode="lines", name="Annual",
                              line=dict(color="#58a6ff", width=1.2)))
    fig2.add_trace(go.Scatter(x=yrs, y=roll5, mode="lines", name="5-yr rolling",
                              line=dict(color="#f78166", width=2.2)))
    fig2.add_trace(go.Scatter(x=yrs, y=roll10, mode="lines", name="10-yr rolling",
                              line=dict(color="#3fb950", width=2.2, dash="dash")))
    fig2.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                       font_color="#c9d1d9",
                       title=f"{meta['label']} at ({sel_lat:.1f}°, {sel_lon:.1f}°)",
                       xaxis_title="Year", yaxis_title=meta["unit"],
                       legend=dict(bgcolor="#1c2128", bordercolor="#30363d"),
                       margin=dict(t=50, b=30))
    st.plotly_chart(fig2, use_container_width=True)

    delta = vals[-1] - vals[0]
    m1, m2, m3, m4 = st.columns(4)
    for col, (v, l) in zip([m1, m2, m3, m4], [
        (f"{np.nanmean(vals):.2f} {meta['unit']}", "Mean"),
        (f"{np.nanmax(vals):.2f} {meta['unit']}", "Max"),
        (f"{np.nanmin(vals):.2f} {meta['unit']}", "Min"),
        (f"{delta:+.2f} {meta['unit']}", "Total Δ"),
    ]):
        col.markdown(f'<div class="metric-card"><div class="val">{v}</div>'
                     f'<div class="lbl">{l}</div></div>', unsafe_allow_html=True)

# ── Trend Map ─────────────────────────────────────────────────
with tabs[2]:
    prog = st.progress(0, text="Computing trend map …")
    slope_dec, _lat, _lon = compute_trend(var)
    prog.progress(100, text="Done")
    cscale_t = "Blues" if var == "siconc" else "RdBu_r"
    lim = max(abs(slope_dec.max()), abs(slope_dec.min()))
    fig3 = px.imshow(slope_dec, x=lon_v, y=lat_v, color_continuous_scale=cscale_t,
                     aspect="auto", zmin=-lim, zmax=lim,
                     title=f"{meta['label']} Trend 1920–2018 ({meta['unit']}/decade)",
                     labels={"color": f"{meta['unit']}/decade"})
    fig3.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                       font_color="#c9d1d9", margin=dict(t=50,b=10))
    fig3.update_xaxes(title="Longitude"); fig3.update_yaxes(title="Latitude")
    st.plotly_chart(fig3, use_container_width=True)

    m1, m2, m3 = st.columns(3)
    for col, (v, l) in zip([m1, m2, m3], [
        (f"{slope_dec.max():+.4f} {meta['unit']}/dec", "Peak Warming"),
        (f"{slope_dec.min():+.4f} {meta['unit']}/dec", "Peak Cooling"),
        (f"{slope_dec.mean():+.4f} {meta['unit']}/dec", "Global Mean Trend"),
    ]):
        col.markdown(f'<div class="metric-card"><div class="val">{v}</div>'
                     f'<div class="lbl">{l}</div></div>', unsafe_allow_html=True)

# ── El Niño Detector ──────────────────────────────────────────
with tabs[3]:
    nino34  = comp(ds["nino34"])
    years_n = ds["year"].values
    colors  = ["#ef4444" if v > 0.5 else "#3b82f6" if v < -0.5 else "#6b7280"
               for v in nino34]
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=years_n, y=nino34, marker_color=colors, name="Niño 3.4"))
    fig4.add_hline(y= 0.5, line_dash="dash", line_color="#ef4444",
                   annotation_text="El Niño", annotation_position="right")
    fig4.add_hline(y=-0.5, line_dash="dash", line_color="#3b82f6",
                   annotation_text="La Niña", annotation_position="right")
    fig4.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                       font_color="#c9d1d9", title="ENSO Index (Niño 3.4) — 1920–2018",
                       xaxis_title="Year", yaxis_title="Niño 3.4 (°C)",
                       margin=dict(t=50, b=30))
    st.plotly_chart(fig4, use_container_width=True)

    nino_yrs = years_n[nino34 >  0.5].tolist()
    nina_yrs = years_n[nino34 < -0.5].tolist()
    neut_n   = len(years_n) - len(nino_yrs) - len(nina_yrs)
    m1, m2, m3 = st.columns(3)
    for col, (v, l) in zip([m1, m2, m3], [
        (len(nino_yrs), "El Niño Count"),
        (len(nina_yrs), "La Niña Count"),
        (neut_n,        "Neutral Count"),
    ]):
        col.markdown(f'<div class="metric-card"><div class="val">{v}</div>'
                     f'<div class="lbl">{l}</div></div>', unsafe_allow_html=True)

    with st.expander("📋 ENSO Event Years"):
        ec1, ec2 = st.columns(2)
        with ec1:
            st.markdown("**🔴 El Niño Years**")
            for y in nino_yrs: st.write(y)
        with ec2:
            st.markdown("**🔵 La Niña Years**")
            for y in nina_yrs: st.write(y)

# ── Comparison ────────────────────────────────────────────────
with tabs[4]:
    cc1, cc2 = st.columns(2)
    with cc1: yr_a = st.selectbox("Year A", list(range(1920, 2019)), index=0)
    with cc2: yr_b = st.selectbox("Year B", list(range(1920, 2019)), index=98)

    with st.spinner("Computing comparison …"):
        grid_a = get_year_mean(var, yr_a)
        grid_b = get_year_mean(var, yr_b)
        diff   = grid_b - grid_a

    fig5 = make_subplots(rows=1, cols=3,
                         subplot_titles=[str(yr_a), str(yr_b), "Δ (B−A)"])
    vmin = min(grid_a.min(), grid_b.min())
    vmax = max(grid_a.max(), grid_b.max())
    dmax = max(abs(diff.min()), abs(diff.max()))
    for ci, (data, csc, zmn, zmx) in enumerate([
        (grid_a, meta["cscale"], vmin, vmax),
        (grid_b, meta["cscale"], vmin, vmax),
        (diff,   "RdBu_r",     -dmax, dmax),
    ], 1):
        fig5.add_trace(go.Heatmap(z=data, x=lon_v, y=lat_v,
                                  colorscale=csc, zmin=zmn, zmax=zmx,
                                  showscale=(ci==3)), row=1, col=ci)
    fig5.update_layout(paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                       font_color="#c9d1d9", height=420,
                       title=f"{meta['label']} — Comparison {yr_a} vs {yr_b}",
                       margin=dict(t=60, b=20))
    st.plotly_chart(fig5, use_container_width=True)

    pct_warm = 100 * (diff > 0).sum() / diff.size
    m1, m2, m3, m4 = st.columns(4)
    for col, (v, l) in zip([m1, m2, m3, m4], [
        (f"{diff.mean():+.3f} {meta['unit']}", "Mean Δ"),
        (f"{diff.max():+.3f} {meta['unit']}", "Max Warming"),
        (f"{diff.min():+.3f} {meta['unit']}", "Max Cooling"),
        (f"{pct_warm:.1f}%", "Grid Warming"),
    ]):
        col.markdown(f'<div class="metric-card"><div class="val">{v}</div>'
                     f'<div class="lbl">{l}</div></div>', unsafe_allow_html=True)

# ── Time-lapse ────────────────────────────────────────────────
with tabs[5]:
    st.markdown("Build a 98-frame animated time-lapse across 1920–2018.")
    if st.button("🎬 Build Time-lapse Animation"):
        ds_ = xr.open_zarr("data/cesm.zarr")
        da  = ds_[var]
        frames = []
        prog = st.progress(0, text="Building frame 1 / 98")
        all_years = list(range(1920, 2019))

        for i, yr in enumerate(all_years):
            ann = comp(da.sel(time=da["time.year"] == yr).mean(dim="time"))
            frames.append(go.Frame(
                data=[go.Heatmap(z=ann, x=lon_v, y=lat_v,
                                 colorscale=meta["cscale"],
                                 zmin=float(np.nanpercentile(ann, 2)),
                                 zmax=float(np.nanpercentile(ann, 98)))],
                name=str(yr)
            ))
            prog.progress((i + 1) / 98, text=f"Building frame {i+1} / 98")

        first_ann = comp(da.sel(time=da["time.year"] == 1920).mean(dim="time"))
        fig6 = go.Figure(
            data=[go.Heatmap(z=first_ann, x=lon_v, y=lat_v,
                             colorscale=meta["cscale"])],
            layout=go.Layout(
                paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
                font_color="#c9d1d9", height=540,
                title=meta["label"],
                updatemenus=[dict(
                    type="buttons", showactive=False,
                    x=0.1, y=0,
                    buttons=[
                        dict(label="▶ Play", method="animate",
                             args=[None, {"frame": {"duration": 200, "redraw": True},
                                          "fromcurrent": True}]),
                        dict(label="⏸ Pause", method="animate",
                             args=[[None], {"frame": {"duration": 0, "redraw": False},
                                            "mode": "immediate"}]),
                    ],
                    bgcolor="#1f6feb", font=dict(color="#fff"),
                )],
                sliders=[dict(
                    currentvalue=dict(prefix="Year: ", font=dict(color="#c9d1d9")),
                    steps=[dict(args=[[str(yr)], {"frame": {"duration": 200, "redraw": True},
                                                   "mode": "immediate"}],
                                label=str(yr), method="animate")
                           for yr in all_years],
                )],
            ),
            frames=frames,
        )
        prog.empty()
        st.plotly_chart(fig6, use_container_width=True)

# ── Story Mode ────────────────────────────────────────────────
with tabs[6]:
    html_path = pathlib.Path("static/story_mode.html")
    if html_path.exists():
        html_content = html_path.read_text(encoding="utf-8")
        components.html(html_content, height=920, scrolling=True)
    else:
        st.error("Run phase3_polish.py to generate story_mode.html")
'''

pathlib.Path("app.py").write_text(app_code.strip(), encoding="utf-8")
print("✅ app.py upgraded (Phase 3 — 7 tabs)")

print("\n🚀 Launching Streamlit …")
os.execvp("streamlit", ["streamlit", "run", "app.py", "--server.headless", "true"])
