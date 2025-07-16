# app.py
import os
import base64
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
    if val > 1655.0:
        return "🟢"
    if val > 1000.0:
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
        "image_path"
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
    "image_path",
]

df_to_show = df_to_show.reset_index(drop=True)

def path_to_base64_img_tag(path, width=30):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
            return f'<img src="data:image/png;base64,{encoded}" width="{width}" style="vertical-align:middle; border-radius:50%;">'
    else:
        return f'<div style="width:{width}px; height:{width}px; background:#eee; border-radius:50%;"></div>'

# Apply base64 image embedding to the Profile column
df_to_show["Profile"] = df_to_show.apply(
    lambda row: f'{path_to_base64_img_tag(row["image_path"], width=30)}&nbsp;&nbsp;{row["Profile"]}',
    axis=1
)

# Display table without index or raw image path

# -------------------------------------------------------------------
# 5) RENDER
# -------------------------------------------------------------------
col1, col2 = st.columns([1, 10])
with col1:
    st.image("./images/Bildschirmfoto 2025-07-15 um 09.11.17.png", width=100)
with col2:
    st.markdown("## 📊  E&V Schleswig-Holstein: Instagram Ranking")

st.markdown(f"Showing **Top {top_n}** by **{sort_by.replace('_',' ').title()}**")

st.markdown(
    df_to_show.drop(columns=["image_path"]).to_html(escape=False, index=False),
    unsafe_allow_html=True
)


