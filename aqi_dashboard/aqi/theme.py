"""Design tokens, global CSS and Plotly styling. Pure strings/dicts, so it is unit-testable."""
from __future__ import annotations

from aqi.config import copyright_line

PALETTE = {
    "ink": "#0B1B33", "muted": "#5B6B86", "bg": "#F4F6FB", "surface": "#FFFFFF", "border": "#E3E8F1",
    "primary": "#1D4ED8", "primary-dark": "#1740C9", "primary-soft": "#E6EDFF",
    "navy": "#0B1B33", "accent": "#38BDF8", "success": "#22A06B", "danger": "#DC2626",
}
COLORWAY = ("#1D4ED8", "#0EA5C6", "#7C3AED", "#E11D74", "#F97316", "#0F9D58", "#475569", "#B45309")
HEATMAP_SCALE = "RdBu"

ICONS = {  # 24x24 stroke icons used in page headers
    "home": '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-5-5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "map": '<path d="M12 21s7-6 7-11a7 7 0 0 0-14 0c0 5 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "cpu": '<rect x="5" y="5" width="14" height="14" rx="3"/><path d="M9 1v4M15 1v4M9 19v4M15 19v4M1 9h4M1 15h4M19 9h4M19 15h4"/>',
    "chart": '<path d="M5 20V10M12 20V4M19 20v-7"/>',
    "book": '<path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3V4z"/><path d="M5 17a3 3 0 0 1 3-3h11"/>',
}

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html{scroll-behavior:smooth}
.stApp{background:var(--bg);color:var(--ink);font-family:'Plus Jakarta Sans',system-ui,-apple-system,'Segoe UI',sans-serif}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5{font-family:inherit;color:var(--ink);letter-spacing:-.01em;font-weight:800}
#MainMenu,footer,.stAppDeployButton{display:none!important}
header[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1180px;padding:2rem 2.5rem 4rem}
:focus-visible{outline:3px solid var(--accent)!important;outline-offset:2px}

@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes shimmer{from{background-position:-200% 0}to{background-position:200% 0}}
.page-header,.card,.lb,[data-testid="stMetric"],[data-testid="stTabs"],.stPlotlyChart,[data-testid="stDataFrame"]{animation:rise .6s cubic-bezier(.2,.7,.2,1) both}

.page-header{display:flex;align-items:center;gap:14px;margin:0 0 1.4rem}
.page-header .icon{flex:none;width:48px;height:48px;border-radius:14px;background:var(--navy);display:grid;place-items:center}
.page-header h1{margin:0;font-size:1.9rem;line-height:1.15;padding:0}
.page-header p{margin:2px 0 0;color:var(--muted);font-size:.95rem}

.card{background:var(--surface);border:1px solid var(--border);border-radius:18px;padding:20px 22px;height:100%;
  transition:transform .25s ease,box-shadow .25s ease,border-color .25s}
.card:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(11,27,51,.10);border-color:#C9D6F5}
.card .tag{font-size:.7rem;letter-spacing:.1em;color:var(--primary);font-weight:800;text-transform:uppercase}
.card h4{margin:.35rem 0 .35rem;font-size:1.05rem}.card p{margin:0;color:var(--muted);font-size:.92rem;line-height:1.6}

[data-testid="stMetric"]{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:14px 18px;
  transition:transform .25s ease,box-shadow .25s ease}
[data-testid="stMetric"]:hover{transform:translateY(-2px);box-shadow:0 10px 24px rgba(11,27,51,.08)}
[data-testid="stMetricValue"]{font-weight:800;letter-spacing:-.02em}
[data-testid="stMetricLabel"] p{color:var(--muted);font-weight:600}

.stPlotlyChart,[data-testid="stDataFrame"]{background:var(--surface);border:1px solid var(--border);border-radius:18px;padding:6px;overflow:hidden}
[data-testid="stExpander"]{background:var(--surface);border:1px solid var(--border)!important;border-radius:14px}
[data-testid="stAlert"]{border-radius:14px}

[data-testid="stTabs"] [role="tablist"]{gap:4px;overflow-x:auto;scrollbar-width:none}
[data-testid="stTabs"] button[role="tab"]{min-height:44px;padding:0 14px;font-weight:700;border-radius:10px 10px 0 0;transition:background .2s}
[data-testid="stTabs"] button[role="tab"]:hover{background:var(--primary-soft)}
[data-testid="stTabs"] button[aria-selected="true"]{color:var(--primary)}
[data-baseweb="tab-highlight"]{background:var(--primary)!important;height:3px!important;border-radius:3px}

[data-testid="stRadio"] [role="radiogroup"]{gap:6px;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;padding:2px}
[data-testid="stRadio"] label{margin:0;min-height:40px;padding:6px 16px;border-radius:999px;background:var(--surface);
  border:1px solid var(--border);cursor:pointer;white-space:nowrap;transition:background .2s,border-color .2s,transform .15s}
[data-testid="stRadio"] label:hover{background:var(--primary-soft);transform:translateY(-1px)}
[data-testid="stRadio"] label>div:first-child{display:none}
[data-testid="stRadio"] label p{margin:0;font-weight:600;font-size:.9rem}
[data-testid="stRadio"] label:has(input:checked){background:var(--primary);border-color:var(--primary)}
[data-testid="stRadio"] label:has(input:checked) p{color:#fff}

[data-testid="stSidebar"]{background:var(--surface);border-right:1px solid var(--border)}
[data-testid="stSidebar"] [role="radiogroup"]{flex-direction:column;overflow:visible;gap:2px}
[data-testid="stSidebar"] [data-testid="stRadio"] label{width:100%;min-height:44px;border:0;border-radius:12px;background:transparent;padding:8px 14px}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked){background:var(--primary-soft)}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p{color:var(--primary-dark);font-weight:800}
.brand .logos{display:flex;align-items:center;gap:10px;margin-bottom:12px}.brand img{height:44px;width:auto;border-radius:10px}
.brand .project{font-weight:800;font-size:1.05rem}.brand .author{font-size:.82rem;margin-top:2px}
.brand .meta{font-size:.74rem;color:var(--muted);margin-top:6px;line-height:1.5}

.lb{background:var(--surface);border:1px solid var(--border);border-radius:18px;padding:20px 22px;margin-bottom:1rem}
.lb h4{margin:0 0 .9rem}.lb-row{margin-bottom:14px}
.lb-head{display:flex;justify-content:space-between;font-size:.86rem;font-weight:600;margin-bottom:6px}.lb-head span+span{color:var(--muted)}
.lb-track{height:10px;border-radius:99px;background:var(--border);overflow:hidden}
.lb-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--primary),var(--accent));transform-origin:left;animation:grow 1s cubic-bezier(.2,.7,.2,1) .3s both}

.app-footer{margin-top:3rem;padding-top:1.2rem;border-top:1px solid var(--border);text-align:center;color:var(--muted);font-size:.82rem}

@media (min-width: 641px) and (max-width: 1024px){.block-container{padding:1.5rem 1.5rem 3rem}}
@media (max-width: 640px){
  .block-container{padding:1rem .9rem 4rem}
  .page-header .icon{width:40px;height:40px}.page-header h1{font-size:1.35rem}.page-header p{font-size:.85rem}
  .card,.lb{padding:16px}[data-testid="stMetricValue"]{font-size:1.4rem}
  [data-testid="stHorizontalBlock"]{gap:.75rem}
  [data-testid="stTabs"] button[role="tab"]{padding:0 10px;font-size:.85rem}
  .stPlotlyChart,[data-testid="stDataFrame"]{padding:2px;border-radius:14px}
}
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
"""


def build_css() -> str:
    variables = ":root{" + ";".join(f"--{k}:{v}" for k, v in PALETTE.items()) + "}"
    return variables + _CSS


def plotly_layout(height: int | None = None) -> dict:
    layout = {
        "template": "plotly_white", "colorway": list(COLORWAY), "autosize": True,
        "paper_bgcolor": "rgba(0,0,0,0)", "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Plus Jakarta Sans, system-ui, sans-serif", "color": PALETTE["ink"]},
        "title_font": {"size": 17},
        "margin": {"l": 16, "r": 16, "t": 60, "b": 28},
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1, "title": ""},
        "hoverlabel": {"font_family": "Plus Jakarta Sans, system-ui, sans-serif"},
        "transition": {"duration": 400, "easing": "cubic-in-out"},
    }
    if height:
        layout["height"] = height
    return layout


def footer_html() -> str:
    return f'<div class="app-footer">{copyright_line()}</div>'
