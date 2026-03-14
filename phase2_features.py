"""
Phase 2 Features — PyClimaExplorer
Overwrites app.py adding: Trend Map, El Niño Detector, Comparison tabs.
"""

import pathlib, os

# ─────────────────────────────────────────────────────────────
# WRITE UPGRADED app.py
# ─────────────────────────────────────────────────────────────
app_code = r'''
import streamlit as st
import xarray as xr
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle

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

# ── SIDEBAR ───────────────────────────────────────────────────
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

def comp(x):
    return x.compute().values if hasattr(x, "compute") else x.values

@st.cache_data
def get_seasonal_mean(_ds_key, variable, yr, ssn):
    ds_ = xr.open_zarr("data/cesm.zarr")
    da  = ds_[variable]
    if ssn == "Annual":
        sub = da.sel(time=da["time.year"] == yr)
    else:
        months = SEASON_MONTHS[ssn]
        sub = da.sel(time=(da["time.year"] == yr) & (da["time.month"].isin(months)))
    return comp(sub.mean(dim="time"))

# ── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Heatmap", "📈 Time Series", "🔥 Trend Map",
    "🌊 El Niño Detector", "🔄 Comparison"
])

# ─────────────────────────────────────────────────────────────
# TAB 1 — HEATMAP
# ─────────────────────────────────────────────────────────────
with tab1:
    with st.spinner("Rendering heatmap …"):
        grid = get_seasonal_mean("ds", var, year, season)
        p2, p98 = np.nanpercentile(grid, 2), np.nanpercentile(grid, 98)
        lat_v = ds["lat"].values
        lon_v = ds["lon"].values
        fig = px.imshow(
            grid, x=lon_v, y=lat_v,
            color_continuous_scale=meta["cscale"],
            aspect="auto",
            title=f"{meta['label']} — {season} {year}",
            labels={"color": meta["unit"]},
            zmin=p2, zmax=p98,
        )
        fig.update_layout(
            paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
            font_color="#c9d1d9", margin=dict(t=50, b=10, l=10, r=10),
        )
        fig.update_xaxes(title="Longitude")
        fig.update_yaxes(title="Latitude")
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 2 — TIME SERIES
# ─────────────────────────────────────────────────────────────
with tab2:
    lat_v = ds["lat"].values
    lon_v = ds["lon"].values
    c1, c2 = st.columns(2)
    with c1:
        sel_lat = st.slider("Latitude",  float(lat_v.min()), float(lat_v.max()), 0.0)
    with c2:
        sel_lon = st.slider("Longitude", float(lon_v.min()), float(lon_v.max()), 0.0)

    @st.cache_data
    def get_ts(variable, slat, slon):
        ds_ = xr.open_zarr("data/cesm.zarr")
        da  = ds_[variable]
        pt  = da.sel(lat=slat, lon=slon, method="nearest")
        ann = pt.groupby("time.year").mean()
        return ann["year"].values, comp(ann)

    with st.spinner("Computing time series …"):
        yrs, vals = get_ts(var, sel_lat, sel_lon)

    s     = pd.Series(vals, index=yrs)
    roll5 = s.rolling(5, center=True).mean()

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=yrs, y=vals, mode="lines", name="Annual",
                              line=dict(color="#58a6ff", width=1.5)))
    fig2.add_trace(go.Scatter(x=yrs, y=roll5, mode="lines", name="5-yr rolling",
                              line=dict(color="#f78166", width=2.5)))
    fig2.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#161b22", font_color="#c9d1d9",
        title=f"{meta['label']} at ({sel_lat:.1f}°, {sel_lon:.1f}°)",
        xaxis_title="Year", yaxis_title=meta["unit"],
        legend=dict(bgcolor="#1c2128", bordercolor="#30363d"),
        margin=dict(t=50, b=30),
    )
    st.plotly_chart(fig2, use_container_width=True)

    m1, m2, m3 = st.columns(3)
    delta = vals[-1] - vals[0]
    for col, (v, l) in zip([m1, m2, m3], [
        (f"{np.nanmean(vals):.2f} {meta['unit']}", "Mean"),
        (f"{np.nanmax(vals):.2f} {meta['unit']}", "Max"),
        (f"{delta:+.2f} {meta['unit']}", "Total Δ"),
    ]):
        col.markdown(f'<div class="metric-card"><div class="val">{v}</div>'
                     f'<div class="lbl">{l}</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TAB 3 — TREND MAP
# ─────────────────────────────────────────────────────────────
with tab3:
    @st.cache_data
    def compute_trend(variable):
        ds_ = xr.open_zarr("data/cesm.zarr")
        da  = ds_[variable]
        annual = da.groupby("time.year").mean()
        data   = comp(annual)          # (98, 36, 72)
        years  = annual["year"].values
        x = years - years.mean()
        slope = (x[:, None, None] * (data - data.mean(axis=0))).sum(axis=0) / (x**2).sum()
        return slope * 10.0, ds_["lat"].values, ds_["lon"].values

    with st.spinner("Computing trend …"):
        slope_dec, lat_v, lon_v = compute_trend(var)

    cscale_trend = "Blues" if var == "siconc" else "RdBu_r"
    fig3 = px.imshow(
        slope_dec, x=lon_v, y=lat_v,
        color_continuous_scale=cscale_trend,
        aspect="auto",
        title=f"{meta['label']} Trend 1920–2018 ({meta['unit']}/decade)",
        labels={"color": f"{meta['unit']}/decade"},
        zmin=-np.abs(slope_dec).max(), zmax=np.abs(slope_dec).max(),
    )
    fig3.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font_color="#c9d1d9",
        margin=dict(t=50, b=10),
    )
    fig3.update_xaxes(title="Longitude")
    fig3.update_yaxes(title="Latitude")
    st.plotly_chart(fig3, use_container_width=True)

    m1, m2, m3 = st.columns(3)
    for col, (v, l) in zip([m1, m2, m3], [
        (f"{slope_dec.max():+.4f} {meta['unit']}/dec", "Peak Warming"),
        (f"{slope_dec.min():+.4f} {meta['unit']}/dec", "Peak Cooling"),
        (f"{slope_dec.mean():+.4f} {meta['unit']}/dec", "Global Mean Trend"),
    ]):
        col.markdown(f'<div class="metric-card"><div class="val">{v}</div>'
                     f'<div class="lbl">{l}</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TAB 4 — EL NIÑO DETECTOR
# ─────────────────────────────────────────────────────────────
with tab4:
    nino34 = comp(ds["nino34"])
    years_n = ds["year"].values

    colors = ["#ef4444" if v > 0.5 else "#3b82f6" if v < -0.5 else "#6b7280"
              for v in nino34]

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=years_n, y=nino34, marker_color=colors, name="Niño 3.4"))
    fig4.add_hline(y=0.5,  line_dash="dash", line_color="#ef4444",
                   annotation_text="El Niño", annotation_position="right")
    fig4.add_hline(y=-0.5, line_dash="dash", line_color="#3b82f6",
                   annotation_text="La Niña", annotation_position="right")
    fig4.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#161b22", font_color="#c9d1d9",
        title="ENSO Index (Niño 3.4) — 1920–2018",
        xaxis_title="Year", yaxis_title="Niño 3.4 Anomaly (°C)",
        margin=dict(t=50, b=30),
    )
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
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**🔴 El Niño Years**")
            for y in nino_yrs:
                st.write(y)
        with c2:
            st.markdown("**🔵 La Niña Years**")
            for y in nina_yrs:
                st.write(y)

# ─────────────────────────────────────────────────────────────
# TAB 5 — COMPARISON
# ─────────────────────────────────────────────────────────────
with tab5:
    c1, c2 = st.columns(2)
    with c1:
        yr_a = st.selectbox("Year A", list(range(1920, 2019)), index=0)
    with c2:
        yr_b = st.selectbox("Year B", list(range(1920, 2019)), index=98)

    @st.cache_data
    def get_year_mean(variable, yr):
        ds_ = xr.open_zarr("data/cesm.zarr")
        da  = ds_[variable]
        sub = da.sel(time=da["time.year"] == yr)
        return comp(sub.mean(dim="time"))

    with st.spinner("Computing comparison …"):
        grid_a = get_year_mean(var, yr_a)
        grid_b = get_year_mean(var, yr_b)
        diff   = grid_b - grid_a

    lat_v = ds["lat"].values
    lon_v = ds["lon"].values

    fig5 = make_subplots(
        rows=1, cols=3,
        subplot_titles=[str(yr_a), str(yr_b), f"Δ (B−A)"],
    )
    vmin = min(grid_a.min(), grid_b.min())
    vmax = max(grid_a.max(), grid_b.max())
    dmax = max(abs(diff.min()), abs(diff.max()))

    for col_idx, (data, cscale, zmin, zmax) in enumerate([
        (grid_a, meta["cscale"], vmin, vmax),
        (grid_b, meta["cscale"], vmin, vmax),
        (diff,   "RdBu_r",      -dmax, dmax),
    ], start=1):
        fig5.add_trace(
            go.Heatmap(z=data, x=lon_v, y=lat_v,
                       colorscale=cscale, zmin=zmin, zmax=zmax,
                       showscale=(col_idx == 3)),
            row=1, col=col_idx,
        )

    fig5.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font_color="#c9d1d9",
        title=f"{meta['label']} — Comparison {yr_a} vs {yr_b}",
        height=420, margin=dict(t=60, b=20),
    )
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
'''

pathlib.Path("app.py").write_text(app_code.strip(), encoding="utf-8")
print("✅ app.py upgraded (Phase 2 — 5 tabs)")

print("\n🚀 Launching Streamlit …")
import os
os.execvp("streamlit", ["streamlit", "run", "app.py", "--server.headless", "true"])
