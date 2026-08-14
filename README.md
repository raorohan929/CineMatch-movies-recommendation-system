DEMO LINK for UI ---- http://localhost:8501/

Project Overview
1 CineMatch — a genre-based movie recommender combining KNN with a rating/popularity weighting scheme
2 Built with Streamlit for the UI, styled like a cinema ticket booth theme

Features
1 Genre-based recommendations via NearestNeighbors model
2 Filters: number of results, minimum vote count, release year range, sort order (Best Match/Highest Rated/Most Popular/Newest/Oldest)
  Grid or List view toggle
3 Plotly visualizations: rating vs. popularity scatter plot, genre distribution bar chart
4 Personal watchlist (add/remove via checkbox)
5 CSV export of recommendations
6 Fully custom CSS theme (no external UI framework)

How It Works
1 Each movie → feature vector of one-hot genres + scaled popularity/rating (weighted by tunable factors)
2 NearestNeighbors model fit on the full feature matrix
3 User picks a genre → query vector built → nearest movies retrieved
4 Candidates filtered by genre, min vote count, year range
5 Re-ranked by weighted rating (IMDB-style Bayesian average) + popularity
6 Top results rendered as cards in the UI

Project Structure
1 rohan.py — Streamlit app (UI, filters, charts, watchlist)
2 movies1.pkl — pickled bundle (model + preprocessed data)
3 requirements.txt — dependencies
README.md

Dataset
1 ~9,600 movies, 18 genres
2 Columns: title, genre/genre_list, overview, release_year, vote_average, vote_count, popularity, weighted_rating

Tech Stack
python, Streamlit, scikit-learn (NearestNeighbors, MinMaxScaler, MultiLabelBinarizer), pandas, numpy, Plotly

Getting Started
1 Clone repo → git clone ...
2 Install deps → pip install -r requirements.txt
3 Run app → streamlit run rohan.py
4 Keep movies1.pkl in same directory as rohan.py

Usage
1 Choose genre + filters in sidebar
2 Click "Get Recommendations"
3 Browse, expand for overview, add to watchlist, export CSV

Possible Improvements
1 Content-based recommendations (TF-IDF/embeddings on overview text)
2 Collaborative filtering with user history
3 Movie posters via TMDB API
4 Deployment (Streamlit Cloud/Render/HuggingFace Spaces)
