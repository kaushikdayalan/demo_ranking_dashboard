# app.py
import streamlit as st
import pandas as pd
import altair as alt

# -------------------------------------------------------------------
# 1) DATA DEFINITION & KPI CALC
# -------------------------------------------------------------------
df = pd.read_csv("./notebooks/data/ranking_data/ranking_dataset.csv")


st.set_page_config(
    page_title=" E&V Schleswig-Holstein: Instagram Ranking",
    layout="wide",  # <— this enables wide mode
)


# -------------------------------------------------------------------
# 2) AUX FUNCTIONS
# -------------------------------------------------------------------
def medal(rank: int) -> str:
    return {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, str(rank))


def engagement_badge(val: float) -> str:
    # simple thresholds
    if val > 5508.0:
        return "🟢"
    if val > 1858.0:
        return "🟡"
    return "🔴"


# unicode sparkline generator
# maps a list of numbers to a string of ▁▂▃▄▅▆▇ blocks
blocks = "▁▂▃▄▅▆▇▉"


def sparkline(data: list[float]) -> str:
    if not data:
        return ""
    lo, hi = min(data), max(data)
    # avoid division by zero
    span = hi - lo or 1
    return "".join(blocks[int((x - lo) / span * (len(blocks) - 1))] for x in data)


# Add dummy 7-day trend to each row
import random

df["trend"] = [
    sparkline([max(0, v + random.randint(-10, 10)) for _ in range(7)])
    for v in df["total_engagement"]
]

# -------------------------------------------------------------------
# 3) SIDEBAR CONTROLS
# -------------------------------------------------------------------
st.sidebar.header("Controls")
top_n = st.sidebar.slider("Show Top N", 1, len(df), 5)
sort_by = st.sidebar.selectbox("Rank by", ["total_posts", "total_engagement"], index=1)

# -------------------------------------------------------------------
# 4) BUILD TABLE
# -------------------------------------------------------------------
# sort, slice, then decorate
df_ranked = df.sort_values(sort_by, ascending=False).head(top_n).reset_index(drop=True)
df_ranked.insert(0, "🏅", [medal(i + 1) for i in df_ranked.index])
df_ranked["Eng. Level"] = df_ranked["total_engagement"].map(engagement_badge)
df_to_show = df_ranked[
    [
        "🏅",
        "profile_name",
        "total_posts",
        "total_likes",
        "total_comments",
        "total_engagement",
        "Eng. Level",
        "trend",
    ]
]
df_to_show.columns = [
    "Rank",
    "Profile",
    "Posts",
    "Likes",
    "Comments",
    "Engagement",
    "Level",
    "7-day Trend",
]

# -------------------------------------------------------------------
# 5) RENDER
# -------------------------------------------------------------------
col1, col2 = st.columns([1, 10])
with col1:
    st.image("./images/Bildschirmfoto 2025-07-15 um 09.11.17.png", width=50)
with col2:
    st.markdown("## 📊  E&V Schleswig-Holstein: Instagram Ranking")

st.markdown(f"Showing **Top {top_n}** by **{sort_by.replace('_',' ').title()}**")

st.dataframe(df_to_show, use_container_width=True)
