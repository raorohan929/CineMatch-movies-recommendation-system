import pickle

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="CineMatch — Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# THEME — "late-night cinema" palette
#   ink navy background, marquee gold accent, velvet-red rating accent
# ------------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');

:root{
    --bg:        #0B0E17;
    --panel:     #131729;
    --card:      #171C33;
    --card-2:    #1D2340;
    --border:    #2A2F4A;
    --gold:      #E8B94D;
    --gold-2:    #F5D374;
    --velvet:    #C1443C;
    --velvet-2:  #E1685F;
    --text:      #F2F0E8;
    --muted:     #98A0BE;
}

/* base */
.stApp{
    background: radial-gradient(1200px 600px at 15% -5%, #171C33 0%, var(--bg) 45%) fixed;
    color: var(--text);
    font-family: 'Inter', sans-serif;
}
h1, h2, h3 { font-family: 'Bebas Neue', sans-serif; letter-spacing: .04em; color: var(--gold); }
p, span, label, div { font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] .main .block-container{ padding-top: 1.6rem; max-width: 1200px; }

/* sidebar = ticket booth */
[data-testid="stSidebar"]{
    background: linear-gradient(180deg, var(--panel), #0F1322);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3{
    color: var(--gold); font-size: 1.5rem;
}
[data-testid="stSidebar"] label{ color: var(--muted) !important; font-weight: 600; font-size: .85rem; text-transform: uppercase; letter-spacing:.05em;}

/* marquee lights */
.marquee-lights{ display:flex; justify-content:center; gap:9px; margin-bottom: .3rem; }
.marquee-lights span{
    width:7px; height:7px; border-radius:50%; background: var(--gold);
    animation: blink 1.8s infinite ease-in-out;
    box-shadow: 0 0 6px var(--gold);
}
.marquee-lights span:nth-child(even){ animation-delay: .9s; }
@keyframes blink{ 0%,100%{opacity:1;} 50%{opacity:.15; box-shadow:none;} }

.hero-title{ text-align:center; font-size: 3.2rem; margin: 0; line-height:1; animation: fadeUp .6s ease; }
.hero-sub{ text-align:center; color: var(--muted); margin-top:.4rem; font-size:1.02rem; }
@keyframes fadeUp{ from{opacity:0; transform:translateY(8px);} to{opacity:1; transform:translateY(0);} }

/* film-strip divider — the recurring signature motif */
.filmstrip{
    height: 22px; margin: 1.4rem 0 1.8rem 0; border-radius: 4px;
    background-color: #1B2038;
    background-image: radial-gradient(circle at center, var(--bg) 5.5px, transparent 6px);
    background-size: 26px 22px; background-position: center;
    border-top: 1px solid var(--border); border-bottom: 1px solid var(--border);
}

/* stat chips */
div[data-testid="stMetric"]{
    background: linear-gradient(160deg, var(--card), var(--card-2));
    border: 1px solid var(--border); border-radius: 12px; padding: .9rem 1rem .7rem 1rem;
}
div[data-testid="stMetricValue"]{ color: var(--gold); font-family:'Bebas Neue'; font-size: 2rem; }
div[data-testid="stMetricLabel"]{ color: var(--muted); text-transform: uppercase; font-size:.72rem; letter-spacing:.06em; }

/* movie ticket card */
.movie-card{
    position: relative; background: linear-gradient(150deg, var(--card), var(--card-2));
    border: 1px solid var(--border); border-radius: 14px; padding: 1.15rem 1.3rem 1rem 1.3rem;
    margin-bottom: .6rem; transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
}
.movie-card:hover{ transform: translateY(-3px); border-color: var(--gold); box-shadow: 0 12px 28px rgba(232,185,77,.14); }
.rank-badge{
    position:absolute; top:-12px; left:-12px; width:40px; height:40px; border-radius:50%;
    background: linear-gradient(135deg, var(--gold), var(--gold-2)); color:#191C2E;
    font-family:'Bebas Neue'; font-size:1.3rem; display:flex; align-items:center; justify-content:center;
    box-shadow: 0 4px 10px rgba(0,0,0,.45); border: 2px solid var(--bg);
}
.card-title{ font-family:'Bebas Neue'; font-size:1.5rem; color: var(--text); letter-spacing:.02em; margin: 0 0 .1rem 2px;}
.card-year{ color: var(--muted); font-family:'JetBrains Mono'; font-size:.85rem; }
.genre-pill{
    display:inline-block; background: rgba(193,68,60,.18); color: var(--velvet-2);
    border: 1px solid rgba(193,68,60,.4); border-radius: 999px; padding: .15rem .65rem;
    font-size:.72rem; font-weight:600; letter-spacing:.03em; margin: .35rem 0 .55rem 0;
}
.stars{ color: var(--gold); letter-spacing: 2px; font-size: 1.05rem; }
.stars .empty{ color: #3A3F5C; }
.rating-num{ color: var(--muted); font-family:'JetBrains Mono'; font-size:.82rem; margin-left:.4rem;}
.pop-label{ display:flex; justify-content:space-between; font-size:.72rem; color:var(--muted); margin-top:.6rem; text-transform:uppercase; letter-spacing:.04em;}
.pop-bar-bg{ background: var(--border); border-radius: 6px; height: 7px; overflow:hidden; }
.pop-bar-fill{ background: linear-gradient(90deg, var(--gold), var(--velvet)); height:100%; border-radius:6px; }
.overview-txt{ color: var(--muted); font-size:.88rem; line-height:1.4; margin-top:.5rem;}

/* buttons */
.stButton>button{
    background: linear-gradient(135deg, var(--gold), var(--gold-2)); color:#191C2E; font-weight:700;
    border:none; border-radius: 9px; padding:.55rem 1.1rem; transition: filter .15s ease;
}
.stButton>button:hover{ filter: brightness(1.08); }
.stDownloadButton>button{
    background: transparent; color: var(--gold); border: 1px solid var(--gold); border-radius: 9px; font-weight:600;
}

/* expander = "more details" */
[data-testid="stExpander"]{ border: 1px solid var(--border); border-radius: 10px; background: var(--card); }
[data-testid="stExpander"] summary{ color: var(--text); font-weight:600; }

/* checkbox (watchlist) */
[data-testid="stCheckbox"] label p{ color: var(--gold) !important; font-weight:600; font-size:.85rem; text-transform:none; }

hr{ border-color: var(--border); }
::-webkit-scrollbar{ width:10px; }
::-webkit-scrollbar-thumb{ background: var(--border); border-radius:6px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# LOAD THE TRAINED MODEL BUNDLE (cached so it only loads once)
# ------------------------------------------------------------------------------
@st.cache_resource
def load_bundle(path="movies1.pkl"):
    with open(path, "rb") as f:
        return pickle.load(f)


bundle = load_bundle()
df = bundle["df"]
nn_model = bundle["nn_model"]
genre_feature_names = bundle["genre_feature_names"]
POPULARITY_WEIGHT = bundle["popularity_weight"]
RATING_WEIGHT = bundle["rating_weight"]


# ------------------------------------------------------------------------------
# RECOMMENDATION FUNCTION (same core logic as the notebook — untouched)
# ------------------------------------------------------------------------------
def recommend_by_genre(genre, top_n=10, min_vote_count=100):
    query = np.zeros(len(genre_feature_names) + 2)
    genre_idx = genre_feature_names.index(genre)
    query[genre_idx] = 1
    query[-2] = POPULARITY_WEIGHT
    query[-1] = RATING_WEIGHT
    query = query.reshape(1, -1)

    distances, indices = nn_model.kneighbors(query, n_neighbors=min(200, len(df)))
    candidates = df.iloc[indices[0]].copy()

    candidates = candidates[
        candidates["genre_list"].apply(lambda g: genre in g)
        & (candidates["vote_count"] >= min_vote_count)
    ]
    candidates = candidates.sort_values(["weighted_rating", "popularity"], ascending=[False, False])

    return candidates[[
        "title", "genre", "release_year", "vote_average",
        "vote_count", "popularity", "weighted_rating", "overview",
    ]].head(top_n).reset_index(drop=True)


# ------------------------------------------------------------------------------
# SMALL UI HELPERS
# ------------------------------------------------------------------------------
def star_html(rating_out_of_10: float) -> str:
    filled = int(round(rating_out_of_10 / 2))
    filled = max(0, min(5, filled))
    stars = "★" * filled + "<span class='empty'>" + "★" * (5 - filled) + "</span>"
    return f"<span class='stars'>{stars}</span><span class='rating-num'>{rating_out_of_10:.1f}/10</span>"


def pop_bar_html(value: float, max_value: float) -> str:
    pct = 0 if max_value <= 0 else max(4, min(100, round(value / max_value * 100)))
    return (
        "<div class='pop-label'><span>Popularity</span><span>" + f"{value:.1f}" + "</span></div>"
        f"<div class='pop-bar-bg'><div class='pop-bar-fill' style='width:{pct}%;'></div></div>"
    )


if "favorites" not in st.session_state:
    st.session_state.favorites = set()
if "show_results" not in st.session_state:
    st.session_state.show_results = False


# ------------------------------------------------------------------------------
# SIDEBAR — "ticket booth"
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎟️ Build Your Screening")
    selected_genre = st.selectbox("Genre", sorted(genre_feature_names))
    top_n = st.slider("Number of picks", min_value=5, max_value=25, value=10)
    min_votes = st.slider("Minimum audience votes", 0, 2000, 100, step=50)
    min_year, max_year = int(df["release_year"].min()), int(df["release_year"].max())
    year_range = st.slider("Release year range", min_year, max_year, (min_year, max_year))
    sort_by = st.selectbox(
        "Sort by",
        ["Best Match", "Highest Rated", "Most Popular", "Newest First", "Oldest First"],
    )
    view_mode = st.radio("Layout", ["Grid", "List"], horizontal=True)
    run_clicked = st.button("🎬  Get Recommendations", type="primary", width="stretch")

    st.markdown("<div class='filmstrip'></div>", unsafe_allow_html=True)
    with st.expander(f"🍿 Your Watchlist ({len(st.session_state.favorites)})"):
        if st.session_state.favorites:
            for t in sorted(st.session_state.favorites):
                st.markdown(f"- {t}")
        else:
            st.caption("Nothing saved yet — tap **Add to Watchlist** on any recommendation.")


# ------------------------------------------------------------------------------
# HERO
# ------------------------------------------------------------------------------
st.markdown("<div class='marquee-lights'>" + "<span></span>" * 16 + "</div>", unsafe_allow_html=True)
st.markdown("<h1 class='hero-title'>🎬 CINEMATCH</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='hero-sub'>Nearest-neighbour picks, ranked by rating &amp; popularity — pick a genre and roll the reel.</p>",
    unsafe_allow_html=True,
)
st.markdown("<div class='filmstrip'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# LIBRARY STATS
# ------------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Films in Library", f"{len(df):,}")
c2.metric("Genres Tracked", f"{len(genre_feature_names)}")
c3.metric("Avg. Rating", f"{df['vote_average'].mean():.1f} / 10")
c4.metric("Now Screening", selected_genre)

# ------------------------------------------------------------------------------
# MAIN CONTENT
# ------------------------------------------------------------------------------
if run_clicked:
    st.session_state.show_results = True

if st.session_state.show_results:
    results = recommend_by_genre(selected_genre, top_n=top_n * 3, min_vote_count=min_votes)
    results = results[
        (results["release_year"] >= year_range[0]) & (results["release_year"] <= year_range[1])
    ].copy()

    sort_map = {
        "Highest Rated": ("vote_average", False),
        "Most Popular": ("popularity", False),
        "Newest First": ("release_year", False),
        "Oldest First": ("release_year", True),
    }
    if sort_by in sort_map:
        col, asc = sort_map[sort_by]
        results = results.sort_values(col, ascending=asc)
    results = results.head(top_n).reset_index(drop=True)

    if results.empty:
        st.warning("No movies match these filters. Try loosening the vote count or year range.")
    else:
        st.markdown(f"### Top {len(results)} {selected_genre} picks for you")

        # --- interactive chart: rating vs popularity for this result set ---
        fig = px.scatter(
            results,
            x="vote_average",
            y="popularity",
            size="vote_count",
            color="weighted_rating",
            hover_name="title",
            size_max=38,
            color_continuous_scale=["#5B6288", "#C1443C", "#E8B94D"],
            labels={"vote_average": "Rating", "popularity": "Popularity", "weighted_rating": "Score"},
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F2F0E8", family="Inter"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=320,
            coloraxis_colorbar=dict(title="Score"),
        )
        fig.update_xaxes(gridcolor="#2A2F4A", zerolinecolor="#2A2F4A")
        fig.update_yaxes(gridcolor="#2A2F4A", zerolinecolor="#2A2F4A")
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

        st.download_button(
            "⬇️ Export these picks as CSV",
            data=results.to_csv(index=False).encode("utf-8"),
            file_name=f"{selected_genre.lower()}_recommendations.csv",
            mime="text/csv",
        )

        st.markdown("<div class='filmstrip'></div>", unsafe_allow_html=True)

        max_pop = results["popularity"].max()
        n_cols = 1 if view_mode == "List" else 2
        cols = st.columns(n_cols)

        for i, row in results.iterrows():
            with cols[i % n_cols]:
                with st.container():
                    st.markdown(
                        f"""
                        <div class="movie-card">
                            <div class="rank-badge">{i + 1}</div>
                            <div class="card-title">{row['title']} <span class="card-year">({int(row['release_year'])})</span></div>
                            <div class="genre-pill">{row['genre']}</div>
                            <div>{star_html(row['vote_average'])}</div>
                            {pop_bar_html(row['popularity'], max_pop)}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    fav_key = f"fav_{selected_genre}_{row['title']}_{i}"
                    is_fav = st.checkbox(
                        "🍿 Add to Watchlist",
                        value=row["title"] in st.session_state.favorites,
                        key=fav_key,
                    )
                    if is_fav:
                        st.session_state.favorites.add(row["title"])
                    else:
                        st.session_state.favorites.discard(row["title"])

                    with st.expander("Movie Overview"):
                        st.markdown(f"<div class='overview-txt'>{row['overview']}</div>", unsafe_allow_html=True)
                        st.caption(f"👥 {int(row['vote_count']):,} votes  ·  📈 weighted score {row['weighted_rating']:.1f}")

else:
    st.info("Set your preferences in the sidebar and click **🎬 Get Recommendations** to roll the reel.")

    st.markdown("<div class='filmstrip'></div>", unsafe_allow_html=True)
    st.markdown("#### 📊 What's in the library")

    exploded = df.explode("genre_list")
    genre_counts = (
        exploded["genre_list"].value_counts().sort_values(ascending=True).reset_index()
    )
    genre_counts.columns = ["genre", "count"]

    fig2 = go.Figure(
        go.Bar(
            x=genre_counts["count"],
            y=genre_counts["genre"],
            orientation="h",
            marker=dict(
                color=genre_counts["count"],
                colorscale=[[0, "#5B6288"], [0.5, "#C1443C"], [1, "#E8B94D"]],
            ),
        )
    )
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F2F0E8", family="Inter"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=360,
        xaxis_title="Number of films",
    )
    fig2.update_xaxes(gridcolor="#2A2F4A")
    fig2.update_yaxes(gridcolor="#2A2F4A")
    st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})
