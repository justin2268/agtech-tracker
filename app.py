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

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #FAFFFE; }
    [data-testid="stSidebar"] { background-color: #F1F8F1; }
    .header-block { padding: 0.5rem 0 1rem 0; }
    .header-title { font-size: 2rem; font-weight: 800; color: #1B5E20; margin: 0; }
    .header-sub { font-size: 1rem; color: #555; margin: 0.25rem 0 0 0; }
    .footer { color: #aaa; font-size: 0.78rem; text-align: center; padding: 1rem 0; }
    div[data-testid="stMetric"] {
        background: #F1F8F1;
        border: 1px solid #C8E6C9;
        border-radius: 10px;
        padding: 0.6rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
SHEET_ID = "1JE1NJ_5nMoiMTsQ7sTEmpLG_H3572pnCBXHelukTi9A"
SHEET_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    "/gviz/tq?tqx=out:csv&sheet=agtech_companies"
)

AU_STATES = {"VIC", "NSW", "QLD", "SA", "WA", "TAS", "NT", "ACT"}

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
    "Wollongong":   (-34.42, 150.89),
    "Geelong":      (-38.15, 144.36),
    "Townsville":   (-19.26, 146.82),
    "Cairns":       (-16.92, 145.77),
    "Ballarat":     (-37.56, 143.86),
    # International (for non-AU companies)
    "Auckland":     (-36.85, 174.76),
    "Vancouver":    (49.28, -123.12),
    "Quebec":       (46.81, -71.21),
    "Lévis":        (46.71, -71.18),
    "Christchurch": (-43.53, 172.64),
}

SECTOR_COLORS = {
    "cropping":    "#558B2F",
    "livestock":   "#8D6E63",
    "dairy":       "#29B6F6",
    "horticulture":"#FF7043",
    "aquaculture": "#26C6DA",
    "mixed":       "#AB47BC",
    "agnostic":    "#78909C",
}

LABEL_MAP = {
    # Sectors
    "cropping": "Cropping", "livestock": "Livestock", "dairy": "Dairy",
    "horticulture": "Horticulture", "aquaculture": "Aquaculture",
    "mixed": "Mixed", "agnostic": "Agnostic",
    # Problems
    "precision_ag": "Precision Ag", "farm_finance": "Farm Finance",
    "water_management": "Water Mgmt", "supply_chain": "Supply Chain",
    "market_access": "Market Access", "sustainability_carbon": "Sustainability/Carbon",
    "equipment_labour": "Equipment/Labour", "risk_insurance": "Risk/Insurance",
    "crop_protection": "Crop Protection", "farm_management": "Farm Management",
    # Funding
    "bootstrapped": "Bootstrapped", "seed": "Seed", "series_a": "Series A",
    "series_b": "Series B", "series_c_plus": "Series C+", "acquired": "Acquired",
    "listed": "Listed", "government_funded": "Gov Funded", "unknown": "Unknown",
    # Employee ranges
    "1_10": "1–10", "11_50": "11–50", "51_200": "51–200",
    "201_500": "201–500", "500_plus": "500+",
}

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        # Derived fields
        df["is_australian"] = df["hq_state"].isin(AU_STATES)
        df["lat"] = df["hq_city"].map(
            lambda c: CITY_COORDS.get(str(c).strip(), (None, None))[0]
        )
        df["lon"] = df["hq_city"].map(
            lambda c: CITY_COORDS.get(str(c).strip(), (None, None))[1]
        )
        # Human-readable labels for display
        df["sector_label"]  = df["farm_sector"].map(LABEL_MAP).fillna(df["farm_sector"])
        df["problem_label"] = df["problem_solved"].map(LABEL_MAP).fillna(df["problem_solved"])
        df["stage_label"]   = df["funding_stage"].map(LABEL_MAP).fillna(df["funding_stage"])
        df["emp_label"]     = df["employee_count_range"].map(LABEL_MAP).fillna(df["employee_count_range"])
        return df
    except Exception as e:
        st.error(f"⚠️ Could not load data from Google Sheets. Make sure the sheet is shared publicly. Error: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌾 Filters")

    show_non_au = st.toggle("Include non-AU HQ companies", value=False)

    working = df[df["is_australian"]] if not show_non_au else df

    all_states  = sorted(working["hq_state"].dropna().unique())
    all_sectors = sorted(working["farm_sector"].dropna().unique())
    all_problems = sorted(working["problem_solved"].dropna().unique())
    all_stages  = sorted(working["funding_stage"].dropna().unique())

    sel_states   = st.multiselect("State / Territory", all_states, default=all_states)
    sel_sectors  = st.multiselect("Farm Sector", all_sectors, default=all_sectors,
                                  format_func=lambda x: LABEL_MAP.get(x, x))
    sel_problems = st.multiselect("Problem Solved", all_problems, default=all_problems,
                                  format_func=lambda x: LABEL_MAP.get(x, x))
    sel_stages   = st.multiselect("Funding Stage", all_stages, default=all_stages,
                                  format_func=lambda x: LABEL_MAP.get(x, x))

    st.markdown("---")
    st.caption("Data sourced from public records, Crunchbase & AgFunder.\nUpdated April 2026.")

# ── Filter data ───────────────────────────────────────────────────────────────
filtered = working.copy()
if sel_states:
    au_in_state   = filtered["is_australian"] & filtered["hq_state"].isin(sel_states)
    non_au        = ~filtered["is_australian"]
    filtered = filtered[au_in_state | (non_au if show_non_au else pd.Series(False, index=filtered.index))]
if sel_sectors:
    filtered = filtered[filtered["farm_sector"].isin(sel_sectors)]
if sel_problems:
    filtered = filtered[filtered["problem_solved"].isin(sel_problems)]
if sel_stages:
    filtered = filtered[filtered["funding_stage"].isin(sel_stages)]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="header-block">'
    '<p class="header-title">🌾 Australian Agtech Landscape Tracker</p>'
    '<p class="header-sub">A live, searchable database of Australian agricultural technology companies '
    '— tracking the ecosystem shaping the future of farming.</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Metrics ───────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("Companies Tracked", len(filtered))
m2.metric("AU States / Territories", filtered[filtered["is_australian"]]["hq_state"].nunique())
m3.metric("Farm Sectors", filtered["farm_sector"].nunique())
m4.metric("Funding Stages", filtered["funding_stage"].nunique())

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_map, tab_table, tab_analytics = st.tabs(["🗺️  Map", "📋  Companies", "📊  Analytics"])

# ════════════════════════════════════════════════════════════════════════════
# MAP TAB
# ════════════════════════════════════════════════════════════════════════════
with tab_map:
    map_df = filtered[filtered["lat"].notna() & filtered["lon"].notna()].copy()

    if map_df.empty:
        st.info("No companies with known locations match your filters.")
    else:
        # Determine map centre — zoom on AU unless non-AU toggled
        if not show_non_au or filtered["is_australian"].all():
            centre = {"lat": -27.0, "lon": 134.0}
            zoom = 3.2
        else:
            centre = {"lat": -20.0, "lon": 140.0}
            zoom = 1.5

        fig_map = px.scatter_mapbox(
            map_df,
            lat="lat",
            lon="lon",
            color="farm_sector",
            color_discrete_map=SECTOR_COLORS,
            hover_name="company_name",
            hover_data={
                "hq_city":        True,
                "hq_state":       True,
                "problem_label":  True,
                "stage_label":    True,
                "emp_label":      True,
                "lat":            False,
                "lon":            False,
                "farm_sector":    False,
            },
            labels={
                "problem_label": "Problem",
                "stage_label":   "Funding",
                "emp_label":     "Employees",
                "farm_sector":   "Sector",
            },
            zoom=zoom,
            center=centre,
            mapbox_style="open-street-map",
            size_max=14,
        )
        fig_map.update_traces(marker=dict(size=12, opacity=0.85))
        fig_map.update_layout(
            height=540,
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(
                title="Farm Sector",
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="#C8E6C9",
                borderwidth=1,
            ),
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.caption(f"Showing {len(map_df)} of {len(filtered)} companies with mapped locations.")

# ════════════════════════════════════════════════════════════════════════════
# COMPANIES TABLE TAB
# ════════════════════════════════════════════════════════════════════════════
with tab_table:
    col_search, col_count = st.columns([3, 1])
    with col_search:
        search = st.text_input("🔍 Search company name or description", placeholder="e.g. carbon, irrigation, livestock...")
    with col_count:
        st.markdown(f"<br><b>{len(filtered)} companies</b>", unsafe_allow_html=True)

    display = filtered.copy()
    if search.strip():
        mask = (
            display["company_name"].str.contains(search, case=False, na=False) |
            display["short_description"].str.contains(search, case=False, na=False)
        )
        display = display[mask]

    show_cols = {
        "company_name":         "Company",
        "hq_city":              "City",
        "hq_state":             "State",
        "sector_label":         "Sector",
        "problem_label":        "Problem Solved",
        "stage_label":          "Funding Stage",
        "emp_label":            "Employees",
        "short_description":    "Description",
        "website":              "Website",
    }
    available = {k: v for k, v in show_cols.items() if k in display.columns}
    display_out = display[list(available.keys())].rename(columns=available)

    st.dataframe(
        display_out,
        use_container_width=True,
        height=480,
        column_config={
            "Website": st.column_config.LinkColumn("Website"),
            "Description": st.column_config.TextColumn("Description", width="large"),
        },
        hide_index=True,
    )

# ════════════════════════════════════════════════════════════════════════════
# ANALYTICS TAB
# ════════════════════════════════════════════════════════════════════════════
with tab_analytics:
    col_l, col_r = st.columns(2)

    # ── Sector bar ────────────────────────────────────────────────────────
    with col_l:
        sector_counts = (
            filtered["farm_sector"]
            .value_counts()
            .reset_index()
            .rename(columns={"farm_sector": "Sector", "count": "Count"})
        )
        sector_counts["Sector"] = sector_counts["Sector"].map(LABEL_MAP).fillna(sector_counts["Sector"])
        fig_sector = px.bar(
            sector_counts, x="Count", y="Sector", orientation="h",
            color="Sector",
            color_discrete_map={LABEL_MAP.get(k, k): v for k, v in SECTOR_COLORS.items()},
            title="Companies by Farm Sector",
        )
        fig_sector.update_layout(showlegend=False, height=320, margin=dict(l=0, r=10, t=40, b=0))
        st.plotly_chart(fig_sector, use_container_width=True)

    # ── Funding stage pie ─────────────────────────────────────────────────
    with col_r:
        stage_counts = (
            filtered["stage_label"]
            .value_counts()
            .reset_index()
            .rename(columns={"stage_label": "Stage", "count": "Count"})
        )
        fig_stage = px.pie(
            stage_counts, values="Count", names="Stage",
            title="Funding Stage Distribution",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.35,
        )
        fig_stage.update_layout(height=320, margin=dict(l=0, r=0, t=40, b=0))
        fig_stage.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_stage, use_container_width=True)

    col_l2, col_r2 = st.columns(2)

    # ── State bar ─────────────────────────────────────────────────────────
    with col_l2:
        au_only = filtered[filtered["is_australian"]]
        state_counts = (
            au_only["hq_state"]
            .value_counts()
            .reset_index()
            .rename(columns={"hq_state": "State", "count": "Count"})
        )
        fig_state = px.bar(
            state_counts, x="State", y="Count",
            color_discrete_sequence=["#2E7D32"],
            title="AU Companies by State",
        )
        fig_state.update_layout(showlegend=False, height=300, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_state, use_container_width=True)

    # ── Problem solved bar ────────────────────────────────────────────────
    with col_r2:
        prob_counts = (
            filtered["problem_label"]
            .value_counts()
            .reset_index()
            .rename(columns={"problem_label": "Problem", "count": "Count"})
        )
        fig_prob = px.bar(
            prob_counts, x="Count", y="Problem", orientation="h",
            color_discrete_sequence=["#388E3C"],
            title="Problems Being Solved",
        )
        fig_prob.update_layout(showlegend=False, height=300, margin=dict(l=0, r=10, t=40, b=0))
        st.plotly_chart(fig_prob, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div class="footer">'
    "Built by Justin Moriarty &nbsp;·&nbsp; "
    "Data sourced from public records, Crunchbase & AgFunder &nbsp;·&nbsp; "
    "Updated April 2026 &nbsp;·&nbsp; "
    "<a href='https://github.com/YOUR_GITHUB/agtech-tracker' style='color:#aaa;'>GitHub</a>"
    "</div>",
    unsafe_allow_html=True,
)
