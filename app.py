import streamlit as st
import pandas as pd
import plotly.express as px

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Australian Agtech Landscape",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Force white background regardless of system theme */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
    }
    [data-testid="stSidebar"] {
        background-color: #F7FBF7 !important;
        border-right: 1px solid #E0EDE0;
    }
    /* Header */
    .page-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1B5E20;
        letter-spacing: -0.5px;
        margin-bottom: 2px;
    }
    .page-sub {
        font-size: 0.95rem;
        color: #666;
        margin-bottom: 0;
    }
    /* Metric cards */
    [data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1.5px solid #C8E6C9 !important;
        border-radius: 10px !important;
        padding: 14px 18px !important;
    }
    [data-testid="stMetricLabel"] { color: #555 !important; font-size: 0.8rem !important; }
    [data-testid="stMetricValue"] { color: #1B5E20 !important; font-size: 1.8rem !important; font-weight: 700 !important; }
    /* Sidebar labels */
    [data-testid="stSidebar"] label { color: #333 !important; font-weight: 500 !important; }
    [data-testid="stSidebar"] .stMultiSelect span { background-color: #E8F5E9 !important; color: #1B5E20 !important; }
    /* Tab styling */
    button[data-baseweb="tab"] { font-size: 0.9rem !important; }
    /* Footer */
    .footer { color: #999; font-size: 0.78rem; text-align: center; padding: 1.5rem 0 0.5rem 0; }
    .footer a { color: #999; }
    /* Divider */
    hr { border-color: #E8F5E9 !important; margin: 0.8rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
SHEET_ID  = "1JE1NJ_5nMoiMTsQ7sTEmpLG_H3572pnCBXHelukTi9A"
SHEET_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    "/gviz/tq?tqx=out:csv&sheet=agtech_companies"
)
AU_STATES = {"VIC","NSW","QLD","SA","WA","TAS","NT","ACT"}

CITY_COORDS = {
    "Sydney":       (-33.87, 151.21),
    "Melbourne":    (-37.81, 144.96),
    "Brisbane":     (-27.47, 153.03),
    "Perth":        (-31.95, 115.86),
    "Adelaide":     (-34.93, 138.60),
    "Darwin":       (-12.46, 130.85),
    "Hobart":       (-42.88, 147.33),
    "Canberra":     (-35.28, 149.13),
    "Dalby":        (-27.18, 151.26),
    "Toowoomba":    (-27.56, 151.95),
    "Gatton":       (-27.56, 152.28),
    "Gindie":       (-23.72, 148.13),
    "Orange":       (-33.28, 149.10),
    "Newcastle":    (-32.93, 151.78),
    "Horsham":      (-36.71, 142.20),
    "Narrabri":     (-30.33, 149.78),
    "Osborne Park": (-31.90, 115.81),
    "Subiaco":      (-31.95, 115.83),
    "Auckland":     (-36.85, 174.76),
    "Vancouver":    (49.28, -123.12),
    "Quebec":       (46.81, -71.21),
    "Lévis":        (46.71, -71.18),
    "Christchurch": (-43.53, 172.64),
}

SECTOR_COLORS = {
    "cropping":     "#558B2F",
    "livestock":    "#8D6E63",
    "dairy":        "#0288D1",
    "horticulture": "#E64A19",
    "aquaculture":  "#00838F",
    "mixed":        "#6A1B9A",
    "agnostic":     "#546E7A",
}

LABEL_MAP = {
    "cropping":"Cropping","livestock":"Livestock","dairy":"Dairy",
    "horticulture":"Horticulture","aquaculture":"Aquaculture","mixed":"Mixed","agnostic":"Agnostic",
    "precision_ag":"Precision Ag","farm_finance":"Farm Finance","water_management":"Water Management",
    "supply_chain":"Supply Chain","market_access":"Market Access","sustainability_carbon":"Sustainability / Carbon",
    "equipment_labour":"Equipment & Labour","risk_insurance":"Risk & Insurance",
    "crop_protection":"Crop Protection","farm_management":"Farm Management",
    "bootstrapped":"Bootstrapped","seed":"Seed","series_a":"Series A","series_b":"Series B",
    "series_c_plus":"Series C+","acquired":"Acquired","listed":"Listed",
    "government_funded":"Gov Funded","unknown":"Unknown",
    "1_10":"1–10","11_50":"11–50","51_200":"51–200","201_500":"201–500","500_plus":"500+",
}

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        df["is_au"]   = df["hq_state"].isin(AU_STATES)
        df["lat"]     = df["hq_city"].map(lambda c: CITY_COORDS.get(str(c).strip(),(None,None))[0])
        df["lon"]     = df["hq_city"].map(lambda c: CITY_COORDS.get(str(c).strip(),(None,None))[1])
        for col, new in [("farm_sector","sector_lbl"),("problem_solved","problem_lbl"),
                         ("funding_stage","stage_lbl"),("employee_count_range","emp_lbl")]:
            df[new] = df[col].map(LABEL_MAP).fillna(df[col])
        return df
    except Exception as e:
        st.error(f"Could not load sheet — make sure it's shared publicly. ({e})")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌾 Filters")
    show_non_au = st.toggle("Include non-AU companies", value=False)
    pool = df if show_non_au else df[df["is_au"]]

    with st.expander("📍 State / Territory", expanded=True):
        all_states = sorted(pool["hq_state"].dropna().unique())
        sel_states = st.multiselect("", all_states, default=all_states, label_visibility="collapsed")

    with st.expander("🌾 Farm Sector", expanded=False):
        all_sectors = sorted(pool["farm_sector"].dropna().unique())
        sel_sectors = st.multiselect("", all_sectors, default=all_sectors,
                                     format_func=lambda x: LABEL_MAP.get(x, x), label_visibility="collapsed")

    with st.expander("🔧 Problem Solved", expanded=False):
        all_problems = sorted(pool["problem_solved"].dropna().unique())
        sel_problems = st.multiselect("", all_problems, default=all_problems,
                                      format_func=lambda x: LABEL_MAP.get(x, x), label_visibility="collapsed")

    with st.expander("💰 Funding Stage", expanded=False):
        all_stages = sorted(pool["funding_stage"].dropna().unique())
        sel_stages = st.multiselect("", all_stages, default=all_stages,
                                    format_func=lambda x: LABEL_MAP.get(x, x), label_visibility="collapsed")

    st.markdown("---")
    st.caption("Data sourced from public records,\nCrunchbase & AgFunder. April 2026.")

# ── Filter ────────────────────────────────────────────────────────────────────
f = pool.copy()
if sel_states:
    au_ok   = f["is_au"] & f["hq_state"].isin(sel_states)
    non_au  = ~f["is_au"]
    f = f[au_ok | (non_au if show_non_au else pd.Series(False, index=f.index))]
if sel_sectors:  f = f[f["farm_sector"].isin(sel_sectors)]
if sel_problems: f = f[f["problem_solved"].isin(sel_problems)]
if sel_stages:   f = f[f["funding_stage"].isin(sel_stages)]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="page-title">Australian Agtech Landscape Tracker</p>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">A live, searchable database of Australian agricultural technology companies.</p>', unsafe_allow_html=True)
st.markdown("---")

# ── Metrics ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Companies Tracked",     len(f))
c2.metric("States / Territories",  f[f["is_au"]]["hq_state"].nunique())
c3.metric("Farm Sectors",          f["farm_sector"].nunique())
c4.metric("Funding Stages",        f["funding_stage"].nunique())

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_map, tab_table, tab_charts = st.tabs(["Map", "Companies", "Analytics"])

# ══════════════════════════════
# MAP
# ══════════════════════════════
with tab_map:
    map_df = f[f["lat"].notna() & f["lon"].notna()].copy()

    if map_df.empty:
        st.info("No companies with mapped locations match the current filters.")
    else:
        fig = px.scatter_geo(
            map_df,
            lat="lat", lon="lon",
            color="farm_sector",
            color_discrete_map=SECTOR_COLORS,
            hover_name="company_name",
            hover_data={
                "hq_city":      True,
                "hq_state":     True,
                "problem_lbl":  True,
                "stage_lbl":    True,
                "emp_lbl":      True,
                "lat": False, "lon": False, "farm_sector": False,
            },
            labels={
                "problem_lbl":"Problem","stage_lbl":"Funding",
                "emp_lbl":"Employees","farm_sector":"Sector",
            },
        )
        fig.update_traces(marker=dict(size=10, opacity=0.85, line=dict(width=0.5, color="white")))
        fig.update_geos(
            showcountries=True,   countrycolor="#CCCCCC",
            showcoastlines=True,  coastlinecolor="#CCCCCC",
            showland=True,        landcolor="#F9F9F9",
            showocean=True,       oceancolor="#EBF5FB",
            showlakes=True,       lakecolor="#EBF5FB",
            lataxis_range=[-45, -8],
            lonaxis_range=[108, 158],
        )
        fig.update_layout(
            height=520,
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(
                title="Sector", orientation="v",
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#C8E6C9", borderwidth=1,
            ),
            paper_bgcolor="white",
            geo_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Showing {len(map_df)} of {len(f)} companies with known locations.")

# ══════════════════════════════
# TABLE
# ══════════════════════════════
with tab_table:
    col_s, col_n = st.columns([3, 1])
    with col_s:
        search = st.text_input("🔍 Search", placeholder="company name or description...", label_visibility="collapsed")
    with col_n:
        st.markdown(f"<p style='padding-top:8px; color:#555;'><b>{len(f)}</b> companies</p>", unsafe_allow_html=True)

    tdf = f.copy()
    if search.strip():
        mask = (
            tdf["company_name"].str.contains(search, case=False, na=False) |
            tdf["short_description"].str.contains(search, case=False, na=False)
        )
        tdf = tdf[mask]

    col_map = {
        "company_name":"Company","hq_city":"City","hq_state":"State",
        "sector_lbl":"Sector","problem_lbl":"Problem Solved",
        "stage_lbl":"Funding","emp_lbl":"Employees",
        "short_description":"Description","website":"Website",
    }
    out_cols = {k: v for k, v in col_map.items() if k in tdf.columns}
    out = tdf[list(out_cols.keys())].rename(columns=out_cols)

    st.dataframe(
        out, use_container_width=True, height=460, hide_index=True,
        column_config={
            "Website":     st.column_config.LinkColumn("Website"),
            "Description": st.column_config.TextColumn("Description", width="large"),
        },
    )

# ══════════════════════════════
# ANALYTICS
# ══════════════════════════════
with tab_charts:
    cl, cr = st.columns(2)

    with cl:
        sc = f["sector_lbl"].value_counts().reset_index()
        sc.columns = ["Sector","Count"]
        fig_s = px.bar(sc, x="Count", y="Sector", orientation="h",
                       color="Sector",
                       color_discrete_map={LABEL_MAP.get(k,k): v for k,v in SECTOR_COLORS.items()},
                       title="Companies by Farm Sector")
        fig_s.update_layout(showlegend=False, height=320, margin=dict(l=0,r=10,t=40,b=0),
                            plot_bgcolor="white", paper_bgcolor="white")
        fig_s.update_xaxes(showgrid=True, gridcolor="#F0F0F0")
        fig_s.update_yaxes(showgrid=False)
        st.plotly_chart(fig_s, use_container_width=True)

    with cr:
        stg = f["stage_lbl"].value_counts().reset_index()
        stg.columns = ["Stage","Count"]
        fig_stg = px.pie(stg, values="Count", names="Stage", hole=0.4,
                         title="Funding Stage Distribution",
                         color_discrete_sequence=px.colors.qualitative.Set2)
        fig_stg.update_layout(height=320, margin=dict(l=0,r=0,t=40,b=0),
                               paper_bgcolor="white")
        fig_stg.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_stg, use_container_width=True)

    cl2, cr2 = st.columns(2)

    with cl2:
        au = f[f["is_au"]]
        stc = au["hq_state"].value_counts().reset_index()
        stc.columns = ["State","Count"]
        fig_st = px.bar(stc, x="State", y="Count", title="AU Companies by State",
                        color_discrete_sequence=["#2E7D32"])
        fig_st.update_layout(showlegend=False, height=300, margin=dict(l=0,r=0,t=40,b=0),
                              plot_bgcolor="white", paper_bgcolor="white")
        fig_st.update_yaxes(showgrid=True, gridcolor="#F0F0F0")
        fig_st.update_xaxes(showgrid=False)
        st.plotly_chart(fig_st, use_container_width=True)

    with cr2:
        pc = f["problem_lbl"].value_counts().reset_index()
        pc.columns = ["Problem","Count"]
        fig_p = px.bar(pc, x="Count", y="Problem", orientation="h",
                       title="Problems Being Solved",
                       color_discrete_sequence=["#388E3C"])
        fig_p.update_layout(showlegend=False, height=300, margin=dict(l=0,r=10,t=40,b=0),
                             plot_bgcolor="white", paper_bgcolor="white")
        fig_p.update_xaxes(showgrid=True, gridcolor="#F0F0F0")
        fig_p.update_yaxes(showgrid=False)
        st.plotly_chart(fig_p, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div class="footer">Built by Justin Moriarty &nbsp;·&nbsp; '
    'Data from public records, Crunchbase & AgFunder &nbsp;·&nbsp; Updated April 2026 &nbsp;·&nbsp; '
    '<a href="https://github.com/justin2268/agtech-tracker">GitHub</a></div>',
    unsafe_allow_html=True,
)
