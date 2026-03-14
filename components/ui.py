import streamlit as st
import os


def load_css():
    """Load custom CSS. Call at top of every page."""
    css_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets", "style.css"
    )
    try:
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def page_header(title, subtitle="", badge=None):
    """White Canva-style section header. Optional badge shown as green pill."""
    badge_html = ""
    if badge:
        badge_html = (f'<span style="background:#E8F8EB;color:#16A34A;font-size:11px;'
                      f'font-weight:600;padding:4px 10px;border-radius:20px;'
                      f'margin-left:12px;vertical-align:middle;font-family:Inter,sans-serif;">'
                      f'{badge}</span>')
    sub_html = ""
    if subtitle:
        sub_html = (f'<div style="font-family:Inter,sans-serif;font-size:14px;'
                    f'color:#6B7280;margin-top:6px;line-height:1.5;">{subtitle}</div>')
    title_div = (f'<div style="font-family:Space Grotesk,sans-serif;font-size:26px;'
                 f'font-weight:700;color:#1B2A4A;line-height:1.1;">{title}{badge_html}</div>')
    html = f'<div style="margin-bottom:20px;">{title_div}{sub_html}</div>'
    st.markdown(html, unsafe_allow_html=True)


def kpi_card(number, label, color="green", progress=70):
    """Colored KPI card — Canva dashboard style."""
    palettes = {
        "green":  ("#E8F8EB", "#6DD47E"),
        "yellow": ("#FEF9E7", "#F5C518"),
        "purple": ("#F0EEFB", "#A89CDB"),
        "blue":   ("#EFF6FF", "#7EB3F7"),
    }
    bg, bar = palettes.get(color, palettes["green"])
    num_div = (f'<div style="font-family:Space Grotesk,sans-serif;font-size:32px;'
               f'font-weight:700;color:#1B2A4A;line-height:1.1;">{number}</div>')
    lbl_div = (f'<div style="font-family:Inter,sans-serif;font-size:12px;'
               f'color:#6B7280;margin-top:5px;">{label}</div>')
    bar_inner = f'<div style="height:4px;width:{progress}%;background:{bar};border-radius:2px;"></div>'
    bar_div = f'<div style="height:4px;background:#E5E7EB;border-radius:2px;margin-top:14px;">{bar_inner}</div>'
    html = f'<div style="background:{bg};border-radius:12px;padding:18px 22px;">{num_div}{lbl_div}{bar_div}</div>'
    st.markdown(html, unsafe_allow_html=True)


def feature_pills(items):
    """Render a row of colored feature pills."""
    palettes = {
        "green":  ("#E8F8EB", "#16A34A"),
        "blue":   ("#EFF6FF", "#1D4ED8"),
        "yellow": ("#FEF9E7", "#B45309"),
    }
    spans = ""
    for label, color in items:
        bg, fg = palettes.get(color, palettes["green"])
        spans += (f'<span style="background:{bg};color:{fg};font-family:Inter,sans-serif;'
                  f'font-size:11px;font-weight:500;padding:4px 12px;border-radius:20px;'
                  f'display:inline-block;">{label}</span>')
    html = f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 18px 0;">{spans}</div>'
    st.markdown(html, unsafe_allow_html=True)


def callout(text, color="green"):
    """Left-bordered callout/info box."""
    palettes = {
        "green":  ("#E8F8EB", "#6DD47E"),
        "blue":   ("#EFF6FF", "#7EB3F7"),
        "yellow": ("#FEF9E7", "#F5C518"),
    }
    bg, border = palettes.get(color, palettes["green"])
    inner = (f'<div style="font-family:Inter,sans-serif;font-size:14px;'
             f'font-weight:500;color:#1B2A4A;line-height:1.6;">{text}</div>')
    html = (f'<div style="background:{bg};border-left:4px solid {border};'
            f'border-radius:0 12px 12px 0;padding:14px 18px;margin:12px 0;">{inner}</div>')
    st.markdown(html, unsafe_allow_html=True)


def divider():
    """Thin gray horizontal divider."""
    st.markdown('<div style="height:1px;background:#E5E7EB;margin:20px 0;"></div>',
                unsafe_allow_html=True)


def stat_card(label, value, note=""):
    """Small white stat card with label, value, optional note."""
    note_html = ""
    if note:
        note_html = f'<div style="font-size:11px;color:#9CA3AF;margin-top:4px;">{note}</div>'
    lbl_div = (f'<div style="font-size:12px;color:#6B7280;font-family:Inter,sans-serif;'
               f'margin-bottom:6px;">{label}</div>')
    val_div = (f'<div style="font-family:Space Grotesk,sans-serif;font-size:22px;'
               f'font-weight:700;color:#1B2A4A;line-height:1.1;">{value}</div>')
    html = (f'<div style="background:#F9FAFB;border:1px solid #E5E7EB;'
            f'border-radius:12px;padding:16px 20px;">{lbl_div}{val_div}{note_html}</div>')
    st.markdown(html, unsafe_allow_html=True)


def sidebar_brand():
    """Render brand header in sidebar. Call inside: with st.sidebar:"""
    brand = (f'<div style="padding:16px 0 20px 0;">'
             f'<div style="font-family:Space Grotesk,sans-serif;font-size:20px;'
             f'font-weight:700;color:#1B2A4A;">🌍 PyClimaExplorer</div>'
             f'<div style="font-family:Inter,sans-serif;font-size:12px;color:#6B7280;'
             f'margin-top:3px;">Climate Intelligence Dashboard</div></div>'
             f'<div style="height:1px;background:#E5E7EB;margin-bottom:16px;"></div>')
    st.markdown(brand, unsafe_allow_html=True)

    badge = (f'<div style="background:#E8F8EB;border-radius:8px;padding:10px 14px;margin-bottom:16px;">'
             f'<div style="font-size:12px;font-weight:600;color:#16A34A;">✅ Synthetic CESM1-style data</div>'
             f'<div style="font-size:11px;color:#6B7280;margin-top:2px;">1920\u20132018 \u00b7 98 years \u00b7 5 variables</div>'
             f'</div>')
    st.markdown(badge, unsafe_allow_html=True)

    team = (f'<div style="font-size:11px;font-weight:500;color:#9CA3AF;'
            f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;">Team</div>'
            f'<div style="font-size:13px;font-weight:600;color:#1B2A4A;">Code Crafters</div>'
            f'<div style="font-size:12px;color:#6B7280;margin-top:2px;">Pushkar Gupta \u00b7 Novance Patel</div>'
            f'<div style="height:1px;background:#E5E7EB;margin:16px 0;"></div>')
    st.markdown(team, unsafe_allow_html=True)


def plotly_layout_white():
    """Returns Plotly layout overrides for white theme."""
    return dict(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#F9FAFB",
        font=dict(family="Inter, sans-serif", color="#1B2A4A", size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        title_font=dict(family="Space Grotesk, sans-serif", size=16, color="#1B2A4A"),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0,
                    font=dict(color="#6B7280", size=11)),
        xaxis=dict(gridcolor="#E5E7EB", linecolor="#E5E7EB",
                   tickfont=dict(color="#6B7280", size=11)),
        yaxis=dict(gridcolor="#E5E7EB", linecolor="#E5E7EB",
                   tickfont=dict(color="#6B7280", size=11)),
    )
