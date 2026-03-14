"""
Phase 1 Bootstrap — PyClimaExplorer
Installs dependencies, generates synthetic CESM1-style zarr dataset,
writes app.py with Heatmap + Time Series tabs, then launches Streamlit.
"""

import subprocess, sys, os, pathlib

# ─────────────────────────────────────────────────────────────
# 1. INSTALL DEPENDENCIES
# ─────────────────────────────────────────────────────────────
packages = [
    "streamlit>=1.32.0",
    "xarray>=2024.1.0",
    "numpy>=1.26.0",
    "pandas>=2.2.0",
    "plotly>=5.20.0",
    "netCDF4>=1.6.5",
    "scipy>=1.12.0",
    "dask[array]>=2024.1.0",
    "zarr>=2.17.0",
    "tqdm>=4.66.0",
]
print("📦 Installing dependencies …")
subprocess.check_call(
    [sys.executable, "-m", "pip", "install", "--quiet"] + packages
)
print("✅ Dependencies installed")

# ─────────────────────────────────────────────────────────────
# 2. GENERATE SYNTHETIC DATASET
# ─────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
import xarray as xr

zarr_path = "data/cesm.zarr"

if not pathlib.Path(zarr_path).exists():
    print("🔧 Generating synthetic CESM1-style dataset …")

    # coordinates
    lat = np.linspace(-87.5, 87.5, 36)
    lon = np.linspace(0.0, 357.5, 72)
    times = pd.date_range("1920-01", periods=98 * 12, freq="MS")
    years = np.arange(1920, 2018)   # 98 years for annual nino34

    LAT, LON = np.meshgrid(lat, lon, indexing="ij")   # (36,72)
    rng = np.random.default_rng(42)

    # linear warming trend (fractional position 0→1 over full period)
    frac = np.linspace(0, 1, 98 * 12)   # (1176,)

    # ---------- tas ----------
    base_K  = 288.0
    base_C  = base_K - 273.15
    spatial  = 30 * np.cos(np.deg2rad(LAT))   # warmer equator
    seasonal = 5.0 * np.sin(2 * np.pi * np.arange(98 * 12) / 12)[
        :, None, None
    ]  # (1176,1,1)
    trend    = (1.1 * frac)[:, None, None]
    noise    = rng.normal(0, 0.5, (1176, 36, 72))
    tas_data = (
        base_C
        + spatial[None, :, :]
        + seasonal
        + trend
        + noise
    )

    # ---------- pr ----------
    pr_spatial = 10.0 * np.exp(-((LAT / 20) ** 2))   # tropical peak
    pr_noise   = rng.gamma(2.0, 1.0, (1176, 36, 72))
    pr_trend   = 0.002 * frac[:, None, None] * (np.abs(LAT) < 30)[None, :, :]
    pr_data    = pr_spatial[None, :, :] + pr_noise + pr_trend

    # ---------- sst ----------
    sst_data = tas_data * 0.9 + rng.normal(0, 0.3, (1176, 36, 72))

    # ---------- psl ----------
    psl_base = 1013.0
    psl_grad = -5.0 * np.sin(np.deg2rad(LAT))
    psl_wave = 2.0 * np.sin(2 * np.pi * LON / 120)
    psl_data = (
        psl_base
        + psl_grad[None, :, :]
        + psl_wave[None, :, :]
        - 0.3 * frac[:, None, None]
        + rng.normal(0, 0.5, (1176, 36, 72))
    )

    # ---------- siconc ----------
    pole_mask = (np.abs(LAT) > 60).astype(float)
    sic_seasonal = 0.3 * np.cos(2 * np.pi * np.arange(1176) / 12)[:, None, None]
    sic_trend    = -0.013 / 12 * np.arange(1176)[:, None, None]   # -13%/decade
    sic_data     = np.clip(
        pole_mask[None, :, :] * (0.8 + sic_seasonal + sic_trend)
        + rng.normal(0, 0.05, (1176, 36, 72)),
        0, 1
    ) * pole_mask[None, :, :]

    # ---------- nino34 (annual) ----------
    yr_idx  = np.arange(98)
    nino34  = 0.8 * np.sin(2 * np.pi * yr_idx / 4.2) + rng.normal(0, 0.3, 98)

    # ---------- Build Dataset ----------
    coords = dict(time=times, lat=lat, lon=lon)
    ds = xr.Dataset(
        {
            "tas":    (["time", "lat", "lon"], tas_data.astype("float32")),
            "pr":     (["time", "lat", "lon"], pr_data.astype("float32")),
            "sst":    (["time", "lat", "lon"], sst_data.astype("float32")),
            "psl":    (["time", "lat", "lon"], psl_data.astype("float32")),
            "siconc": (["time", "lat", "lon"], sic_data.astype("float32")),
            "nino34": (["year"],               nino34.astype("float32")),
        },
        coords={**coords, "year": years},
    )

    pathlib.Path("data").mkdir(exist_ok=True)
    ds.to_zarr(zarr_path)
    print("✅ Synthetic CESM1-style dataset generated (1920–2018)")
else:
    print("✅ data/cesm.zarr already exists — skipping generation")

# ─────────────────────────────────────────────────────────────
# 3. WRITE app.py
# ─────────────────────────────────────────────────────────────
app_code = r'''
import streamlit as st
import xarray as xr
import numpy as np
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="PyClimaExplorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Dark Theme ────────────────────────────────────────────────
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
  .metric-card .val { font-size: 1.6rem; font-weight: 700; color: #58a6ff; }
  .metric-card .lbl { font-size: .75rem; color: #8b949e; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🌍 PyClimaExplorer</h1>", unsafe_allow_html=True)

# ── VARIABLE META ─────────────────────────────────────────────
VARIABLE_META = {
    "tas":    {"label": "Surface Air Temp (°C)",      "cscale": "RdBu_r",  "unit": "°C"},
    "pr":     {"label": "Precipitation (mm/day)",     "cscale": "Blues",   "unit": "mm/day"},
    "sst":    {"label": "Sea Surface Temp (°C)",      "cscale": "RdBu_r",  "unit": "°C"},
    "psl":    {"label": "Sea Level Pressure (hPa)",   "cscale": "RdBu_r",  "unit": "hPa"},
    "siconc": {"label": "Sea Ice Concentration (%)",  "cscale": "Blues_r", "unit": "%"},
}

# ── DATA LOAD ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    return xr.open_zarr("data/cesm.zarr")

with st.spinner("Loading dataset …"):
    ds = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="badge">✅ Synthetic CESM1-style data · 1920–2018</div>',
                unsafe_allow_html=True)
    st.markdown("---")
    var     = st.selectbox("Variable", list(VARIABLE_META.keys()),
                           format_func=lambda v: VARIABLE_META[v]["label"])
    season  = st.selectbox("Season", ["Annual", "DJF", "MAM", "JJA", "SON"])
    year    = st.slider("Year", 1920, 2018, 1969)

meta = VARIABLE_META[var]

# ── SEASON FILTER ─────────────────────────────────────────────
SEASON_MONTHS = {"DJF": [12,1,2], "MAM": [3,4,5], "JJA": [6,7,8], "SON": [9,10,11]}

@st.cache_data
def get_seasonal_mean(_ds, variable, yr, ssn):
    da = _ds[variable]
    if ssn == "Annual":
        sub = da.sel(time=da["time.year"] == yr)
    else:
        months = SEASON_MONTHS[ssn]
        sub = da.sel(time=(da["time.year"] == yr) & (da["time.month"].isin(months)))
    arr = sub.mean(dim="time")
    return arr.compute().values if hasattr(arr, "compute") else arr.values

# ── TABS ──────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🗺️ Heatmap", "📈 Time Series"])

# ── TAB 1: HEATMAP ───────────────────────────────────────────
with tab1:
    with st.spinner("Rendering heatmap …"):
        grid = get_seasonal_mean(ds, var, year, season)
        p2, p98 = np.nanpercentile(grid, 2), np.nanpercentile(grid, 98)
        zmid_kwargs = {}
        if var in ("tas", "sst", "psl"):
            zmid_kwargs = {"zmin": p2, "zmax": p98}
        lat_vals = ds["lat"].values
        lon_vals = ds["lon"].values
        fig = px.imshow(
            grid,
            x=lon_vals, y=lat_vals,
            color_continuous_scale=meta["cscale"],
            aspect="auto",
            title=f"{meta['label']} — {season} {year}",
            labels={"color": meta["unit"]},
            **zmid_kwargs,
        )
        fig.update_layout(
            paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
            font_color="#c9d1d9", margin=dict(t=50, b=10, l=10, r=10),
            coloraxis_colorbar=dict(title=meta["unit"]),
        )
        fig.update_xaxes(title="Longitude")
        fig.update_yaxes(title="Latitude")
        st.plotly_chart(fig, use_container_width=True)

# ── TAB 2: TIME SERIES ───────────────────────────────────────
with tab2:
    lat_vals = ds["lat"].values
    lon_vals = ds["lon"].values
    c1, c2 = st.columns(2)
    with c1:
        sel_lat = st.slider("Latitude",  float(lat_vals.min()), float(lat_vals.max()), 0.0)
    with c2:
        sel_lon = st.slider("Longitude", float(lon_vals.min()), float(lon_vals.max()), 0.0)

    @st.cache_data
    def get_timeseries(_ds, variable, slat, slon):
        da   = _ds[variable]
        pt   = da.sel(lat=slat, lon=slon, method="nearest")
        ann  = pt.groupby("time.year").mean()
        vals = ann.compute().values if hasattr(ann, "compute") else ann.values
        yrs  = ann["year"].values
        return yrs, vals

    with st.spinner("Computing time series …"):
        yrs, vals = get_timeseries(ds, var, sel_lat, sel_lon)

    s = pd.Series(vals, index=yrs)
    roll5 = s.rolling(5, center=True).mean()

    import plotly.graph_objects as go
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=yrs, y=vals, mode="lines", name="Annual",
        line=dict(color="#58a6ff", width=1.5, dash="solid"),
    ))
    fig2.add_trace(go.Scatter(
        x=yrs, y=roll5, mode="lines", name="5-yr rolling",
        line=dict(color="#f78166", width=2.5),
    ))
    fig2.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
        font_color="#c9d1d9",
        title=f"{meta['label']} at ({sel_lat:.1f}°, {sel_lon:.1f}°)",
        xaxis_title="Year", yaxis_title=meta["unit"],
        legend=dict(bgcolor="#1c2128", bordercolor="#30363d"),
        margin=dict(t=50, b=30),
    )
    st.plotly_chart(fig2, use_container_width=True)

    m1, m2, m3 = st.columns(3)
    delta = vals[-1] - vals[0]
    cards = [
        (f"{np.nanmean(vals):.2f} {meta['unit']}", "Mean"),
        (f"{np.nanmax(vals):.2f} {meta['unit']}", "Max"),
        (f"{delta:+.2f} {meta['unit']}", "Total Δ (1920→2018)"),
    ]
    for col, (v, l) in zip([m1, m2, m3], cards):
        col.markdown(
            f'<div class="metric-card"><div class="val">{v}</div>'
            f'<div class="lbl">{l}</div></div>',
            unsafe_allow_html=True,
        )
'''

pathlib.Path("app.py").write_text(app_code.strip(), encoding="utf-8")
print("✅ app.py written")

# ─────────────────────────────────────────────────────────────
# 4. WRITE requirements.txt
# ─────────────────────────────────────────────────────────────
reqs = "\n".join([
    "streamlit>=1.32.0",
    "xarray>=2024.1.0",
    "numpy>=1.26.0",
    "pandas>=2.2.0",
    "plotly>=5.20.0",
    "netCDF4>=1.6.5",
    "scipy>=1.12.0",
    "dask[array]>=2024.1.0",
    "zarr>=2.17.0",
    "tqdm>=4.66.0",
])
pathlib.Path("requirements.txt").write_text(reqs, encoding="utf-8")
print("✅ requirements.txt written")

# ─────────────────────────────────────────────────────────────
# 5. LAUNCH
# ─────────────────────────────────────────────────────────────
print("\n🚀 Launching Streamlit …")
os.execvp("streamlit", ["streamlit", "run", "app.py", "--server.headless", "true"])
