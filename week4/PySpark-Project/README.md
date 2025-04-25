# PySpark Movie Data Analysis

## Overview

This project performs an analysis of movie data using PySpark. It fetches movie details from the TMDB API, cleans and transforms the data, and then conducts various analyses, including KPI calculations and comparisons.


## Work Flow

1.  **Data Extraction**

    * The notebook fetches movie data from the TMDB API using a list of movie IDs.
    * The `extract_data` function in `functions.py` handles the API calls and creates a Spark DataFrame.

2.  **Data Cleaning**

    * The `clean_data` function in `functions.py` cleans the DataFrame by:
        * Dropping irrelevant columns.
        * Parsing JSON-like columns.
        * Extracting relevant information.
        * Handling missing data.
        * Converting data types.
        * Removing duplicates.
        * Filtering released movies.
        * Reordering columns.

3.  **KPI Calculation**

    * The `kpi_indicators` function calculates profit and ROI and adds these as new columns to the DataFrame.

4.  **Data Analysis**

    * The notebook performs various analyses using the functions in `functions.py`:
        * Ranking movies by revenue, budget, profit, ROI, vote count, vote average, and popularity.
        * Filtering movies based on criteria (e.g., Bruce Willis movies, Tarantino films).
        * Comparing franchise vs. standalone movie performance.
        * Identifying successful franchises and directors.

5.  **Visualization**
    * Some basic visualization is done using matplotlib

## Functions Overview

* `create_spark_session(app_name)`: Creates a Spark session.
* `extract_data(url, api_key, movie_ids, spark)`: Fetches movie data from the TMDB API.
* `clean_data(df)`: Cleans the movie data.
* `kpi_indicators(df)`: Calculates KPI indicators (profit, ROI).
* `rank_movies_spark(df, sort_by, ascending, min_budget_million_usd, min_votes)`: Ranks movies based on a specified column.
* `bruce_willis_movie(df)`: Filters for Science Fiction Action Movies Starring Bruce Willis
* `uma_tarentino(df)`: Filters for Movies Starring Uma Thurman Directed by Quentin Tarantino
* `franchise_vs_standalone_performance(df)`: Compares the performance of franchise vs. standalone movies.
* `successful_franchises(df, top_n)`: Identifies successful movie franchises.
* `successful_directors(df, top_n)`: Identifies successful directors.

## Insights


**Financial Success:**

* **High Revenue and Profit are Correlated:** The top three movies in terms of revenue (`Avatar`, `Avengers: Endgame`, `Titanic`) are also the top three in terms of profit, indicating a strong link between box office earnings and overall profitability.
* **High Budget Doesn't Guarantee Top Profit:** While `Avengers: Endgame` appears in both the highest revenue and highest budget lists, `Avengers: Age of Ultron` has the highest budget but doesn't feature in the top profit list. This suggests that high spending doesn't automatically translate to the highest returns.
* **Significant Profit Margins:** The profit figures for the top movies are substantial, often exceeding their budgets. For example, `Avatar` generated over $2.6 billion in profit on a budget of around $237 million.
* **Lowest Profit Still Represents Significant Earnings:** Even the "lowest profit" movies listed still generated over $1 billion in profit, highlighting the potential for massive financial success in blockbuster filmmaking.

**Return on Investment (ROI):**

* **High ROI for Blockbusters:** Movies like `Avatar` and `Titanic` demonstrate exceptionally high returns on their investment, with revenues over 10 times their budgets (ROI > 10).
* **High Budget Can Lead to Lower ROI:** `Avengers: Age of Ultron`, despite its high budget, has a significantly lower ROI compared to the top revenue/profit films. This reinforces the idea that efficient spending is crucial for maximizing returns.
* **Franchise Success Evident in ROI:** Both `Jurassic World` and `The Lion King` (while the latter is a remake, it functions as a major studio tentpole) show strong ROI, indicating the profitability of established and well-marketed franchises.

**Audience Engagement:**

* **Popularity and Vote Count Align:** Movies like `Avatar` and `Avengers: Infinity War` appear in both the "Most Voted" and "Most Popular" lists, suggesting a strong correlation between the number of people voting and the overall popularity of a film.
* **Critical Acclaim and Popularity Can Differ:** While `Avengers: Endgame` and `Avengers: Infinity War` are among the highest-rated movies, `The Lion King` and `Beauty and the Beast` appear in the "Most Popular" list but not the top-rated, indicating that popularity isn't solely driven by critical acclaim (as reflected in `vote_average`).

**Ratings:**

* **Franchise Fatigue or Evolving Tastes?:** The "Lowest Rated Movies" list features recent installments in established franchises (`Jurassic World`, `Star Wars`), which could suggest potential franchise fatigue or evolving audience expectations.
* **Blockbusters Can Achieve High Ratings:** Despite their scale, movies like `Avengers: Endgame` and `Avengers: Infinity War` have achieved very high average ratings, indicating that large-scale productions can still resonate strongly with audiences and critics.

**Overall Trends:**

* **Franchises Dominate:** Many of the top performers across different KPIs belong to major franchises (Avengers, Avatar, Jurassic World, Harry Potter, The Lion King), highlighting the financial power and audience reach of established cinematic universes.
* **Logarithmic Scale Impact:** The use of a logarithmic scale in the `plot_revenue_vs_budget` visualization (which you provided earlier) is likely necessary to effectively display the wide range of budget and revenue figures, where a few massive hits can dwarf the majority of films.

These insights provide a starting point for a deeper exploration of your movie dataset. You could further investigate the factors contributing to the high ROI of certain films, the potential reasons for lower ratings in some franchises, or the relationship between budget, popularity, and critical reception.
